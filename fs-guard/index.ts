/**
 * fs-guard: Filesystem protection plugin for OpenClaw
 *
 * Intercepts write/edit/exec tool calls and blocks destructive operations
 * on critical files and directories. The agent is told to ask the user
 * for explicit confirmation before proceeding.
 */

// ── Critical path definitions ────────────────────────────────────────

const HOME = process.env.HOME || "/Users/zhanglinghao";

/** Paths where write/edit is ALWAYS blocked (system-critical) */
const ALWAYS_PROTECTED = [
  "/etc",
  "/usr",
  "/bin",
  "/sbin",
  "/System",
  "/Library",
  "/private",
  "/var",
  "/boot",
  "/dev",
  "/proc",
  "/sys",
];

/** User-level paths that require confirmation before modification */
const USER_PROTECTED = [
  `${HOME}/.ssh`,
  `${HOME}/.gnupg`,
  `${HOME}/.config`,
  `${HOME}/.zshrc`,
  `${HOME}/.bashrc`,
  `${HOME}/.bash_profile`,
  `${HOME}/.zprofile`,
  `${HOME}/.gitconfig`,
  `${HOME}/.npmrc`,
  `${HOME}/.env`,
  `${HOME}/.claude`,
  `${HOME}/.openclaw/openclaw.json`,
  `${HOME}/Library`,
];

/** Paths where writes are always allowed (no confirmation needed) */
const DEFAULT_ALLOWED_WRITE_PATHS = [
  `${HOME}/.openclaw/workspace`,
  `${HOME}/.openclaw/extensions/fs-guard`,
  "/tmp",
  "/var/tmp",
];

/** Dangerous shell command patterns */
const DANGEROUS_EXEC_PATTERNS = [
  /\brm\s+(-[a-zA-Z]*[rR][a-zA-Z]*\s+|--recursive\s+)/,   // rm -r, rm -rf, rm -Rf, etc.
  /\brm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)/,                       // rm -f (force delete)
  /\brmdir\b/,                                                 // rmdir
  /\bfind\b.*\b-delete\b/,                                    // find ... -delete
  /\bfind\b.*-exec\s+rm\b/,                                   // find ... -exec rm
  /\bshred\b/,                                                 // shred (secure delete)
  /\bdd\b.*\bof=/,                                             // dd of= (disk overwrite)
  /\bmkfs\b/,                                                  // mkfs (format filesystem)
  /\bchmod\s+-R\b/,                                            // chmod -R (recursive permission change)
  /\bchown\s+-R\b/,                                            // chown -R (recursive owner change)
  />\s*\/dev\/null\b.*2>&1/,                                   // silencing output suspiciously
  /\bcurl\b.*\|\s*(bash|sh|zsh)\b/,                           // curl | bash (remote code exec)
  /\bwget\b.*\|\s*(bash|sh|zsh)\b/,                           // wget | bash
  /\bgit\s+push\s+.*--force\b/,                               // git push --force
  /\bgit\s+reset\s+--hard\b/,                                 // git reset --hard
  /\bgit\s+clean\s+-[a-zA-Z]*f/,                              // git clean -f
];

/** Patterns that indicate mass/bulk operations */
const BULK_OPERATION_PATTERNS = [
  /\bxargs\b.*\brm\b/,                                        // xargs rm
  /\bfor\b.*\brm\b/,                                          // for loop with rm
  /\bwhile\b.*\brm\b/,                                        // while loop with rm
  /\brm\s+.*\*/,                                               // rm with glob (rm *.txt, rm -rf *)
];

// ── Helper functions ─────────────────────────────────────────────────

function normalizePath(p: string): string {
  // Resolve ~ and remove trailing slashes
  let resolved = p.replace(/^~/, HOME);
  // Remove trailing slash unless root
  if (resolved.length > 1 && resolved.endsWith("/")) {
    resolved = resolved.slice(0, -1);
  }
  return resolved;
}

function isUnderPath(filePath: string, dirPath: string): boolean {
  const norm = normalizePath(filePath);
  const dir = normalizePath(dirPath);
  return norm === dir || norm.startsWith(dir + "/");
}

function isSystemProtected(filePath: string): boolean {
  const norm = normalizePath(filePath);
  return ALWAYS_PROTECTED.some((p) => isUnderPath(norm, p));
}

function isUserProtected(filePath: string, extraProtected: string[]): boolean {
  const norm = normalizePath(filePath);
  const allProtected = [...USER_PROTECTED, ...extraProtected];
  return allProtected.some((p) => isUnderPath(norm, p) || norm === normalizePath(p));
}

function isAllowedWrite(filePath: string, extraAllowed: string[]): boolean {
  const norm = normalizePath(filePath);
  const allAllowed = [...DEFAULT_ALLOWED_WRITE_PATHS, ...extraAllowed];
  return allAllowed.some((p) => isUnderPath(norm, p));
}

function isDangerousExec(command: string): { dangerous: boolean; reason: string } {
  for (const pattern of DANGEROUS_EXEC_PATTERNS) {
    if (pattern.test(command)) {
      return {
        dangerous: true,
        reason: `Command matches dangerous pattern: ${pattern.source}`,
      };
    }
  }
  for (const pattern of BULK_OPERATION_PATTERNS) {
    if (pattern.test(command)) {
      return {
        dangerous: true,
        reason: `Command appears to be a bulk/mass destructive operation: ${pattern.source}`,
      };
    }
  }
  return { dangerous: false, reason: "" };
}

function isEmptyOrTrivialContent(content: unknown): boolean {
  if (content === null || content === undefined) return true;
  if (typeof content === "string") {
    return content.trim().length === 0;
  }
  return false;
}

// ── Plugin definition ────────────────────────────────────────────────

const BLOCK_MSG_PREFIX = "[fs-guard] ";

export default {
  id: "fs-guard",
  name: "Filesystem Guard",
  description: "Protects critical files from destructive AI agent operations",

  register(api: any) {
    const logger = api.logger;
    const config = api.pluginConfig || {};
    const extraProtected: string[] = config.protectedPaths || [];
    const extraAllowed: string[] = config.allowedWritePaths || [];
    const blockEmptyWrites: boolean = config.blockEmptyWrites !== false;
    const enabled: boolean = config.enabled !== false;

    logger.info("fs-guard plugin loaded", {
      enabled,
      extraProtected: extraProtected.length,
      extraAllowed: extraAllowed.length,
      blockEmptyWrites,
    });

    if (!enabled) return;

    // ── before_tool_call hook ──────────────────────────────────────

    api.on("before_tool_call", async (event: any, _ctx: any) => {
      const { toolName, params } = event;

      // ── Handle write tool ──────────────────────────────────────
      if (toolName === "write") {
        const filePath = params?.file_path || params?.path || "";
        if (!filePath) return; // no path, let it through

        // System-critical: always block
        if (isSystemProtected(filePath)) {
          logger.warn("BLOCKED write to system-critical path", { filePath });
          return {
            block: true,
            blockReason:
              `${BLOCK_MSG_PREFIX}Writing to system-critical path "${filePath}" is blocked. ` +
              `This path is protected and cannot be modified by AI agents.`,
          };
        }

        // Explicitly allowed: let through
        if (isAllowedWrite(filePath, extraAllowed)) {
          return;
        }

        // Block empty writes (clearing file content)
        if (blockEmptyWrites && isEmptyOrTrivialContent(params?.content)) {
          logger.warn("BLOCKED empty write (would clear file)", { filePath });
          return {
            block: true,
            blockReason:
              `${BLOCK_MSG_PREFIX}Writing empty content to "${filePath}" is blocked. ` +
              `This would erase the file contents. Please ask the user to confirm ` +
              `if they really want to clear this file.`,
          };
        }

        // User-protected: block with confirmation request
        if (isUserProtected(filePath, extraProtected)) {
          logger.warn("BLOCKED write to user-protected path", { filePath });
          return {
            block: true,
            blockReason:
              `${BLOCK_MSG_PREFIX}Writing to protected path "${filePath}" requires user confirmation. ` +
              `Please ask the user explicitly: "Do you want me to modify ${filePath}?" ` +
              `and only proceed after they confirm.`,
          };
        }

        return; // not protected, allow
      }

      // ── Handle edit tool ───────────────────────────────────────
      if (toolName === "edit" || toolName === "apply_patch") {
        const filePath = params?.file_path || params?.path || "";
        if (!filePath) return;

        if (isSystemProtected(filePath)) {
          logger.warn("BLOCKED edit to system-critical path", { filePath });
          return {
            block: true,
            blockReason:
              `${BLOCK_MSG_PREFIX}Editing system-critical path "${filePath}" is blocked.`,
          };
        }

        if (isAllowedWrite(filePath, extraAllowed)) {
          return;
        }

        if (isUserProtected(filePath, extraProtected)) {
          logger.warn("BLOCKED edit to user-protected path", { filePath });
          return {
            block: true,
            blockReason:
              `${BLOCK_MSG_PREFIX}Editing protected path "${filePath}" requires user confirmation. ` +
              `Please ask the user explicitly before modifying this file.`,
          };
        }

        return;
      }

      // ── Handle exec tool ───────────────────────────────────────
      if (toolName === "exec") {
        const command = params?.command || params?.cmd || "";
        if (!command || typeof command !== "string") return;

        const check = isDangerousExec(command);
        if (check.dangerous) {
          logger.warn("BLOCKED dangerous exec command", {
            command: command.substring(0, 200),
            reason: check.reason,
          });
          return {
            block: true,
            blockReason:
              `${BLOCK_MSG_PREFIX}Dangerous command blocked: ${check.reason}. ` +
              `Command: "${command.substring(0, 100)}..." ` +
              `Please ask the user for explicit confirmation before running destructive commands.`,
          };
        }

        return;
      }
    }, { priority: 100 }); // high priority, run early

    logger.info("fs-guard: before_tool_call hook registered");
  },
};

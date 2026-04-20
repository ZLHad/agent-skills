# Deployment

Read this only when the user asks how to install or deploy the skill.

## Where to put the skill directory

| Environment | Location |
|---|---|
| Claude.ai (user skill) | `/mnt/skills/user/paper-figure-to-pptx/` |
| Claude Code CLI | anywhere in the user's project; reference `./paper-figure-to-pptx/SKILL.md` in prompts |
| Anthropic API | inject `SKILL.md` and `scripts/helpers.py` contents into the system prompt, enable `code_execution` tool |

In all cases the skill directory is self-contained — no path edits needed.

## Dependencies

```bash
pip install python-pptx lxml
# Optional, for self-review JPG conversion:
#   Ubuntu/Debian: sudo apt install libreoffice poppler-utils
#   macOS:         brew install libreoffice poppler
```

## Starting a new conversion task

Copy the working files into the user's directory once, then edit in place:

```bash
cp <skill-path>/scripts/helpers.py .
cp <skill-path>/scripts/assemble.py .
cp <skill-path>/scripts/module_template.py ./module1.py   # one copy per Module
```

Edit each `moduleN.py`, then:

```bash
python module1.py               # generates Module_N.pptx (rename freely)
python assemble.py -o Fig.pptx  # combines all module*.py into one multi-page pptx
```

## Troubleshooting

- **Skill not triggering on Claude.ai** — directory must be directly under `/mnt/skills/user/`, not nested. Start a fresh conversation.
- **`ImportError: No module named helpers`** — `helpers.py` must live in the same directory as your `moduleN.py`. Don't `import` from `scripts/` directly.
- **`assemble.py` finds no modules** — run it from the directory containing your `module*.py` files.

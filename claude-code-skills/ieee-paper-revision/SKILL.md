---
name: ieee-paper-revision
description: >-
  IEEE 学术论文修改（大修/小修）全流程助手。This skill should be used when the user asks to
  "修改论文", "处理审稿意见", "写回复信", "大修", "小修", "revision", "handle reviewer comments",
  "respond to reviewers", "revise manuscript", "address reviewer concerns",
  "write response letter", "paper revision", or when a review email or reviewer comments
  are provided. Covers the complete IEEE journal revision workflow: comment extraction,
  revision planning, manuscript editing with blue marking, and response letter generation.
---

# IEEE Paper Revision Workflow

A complete workflow for handling IEEE journal paper revisions (major/minor), from parsing reviewer comments to producing the revised manuscript and response letter.

## Overview

The revision process has three phases:
1. **Comment Extraction & Planning** - Parse review email, organize comments, create revision plan
2. **Iterative Revision** - Address each comment: edit manuscript + write response entry
3. **Finalization** - Verify completeness, remove old blue marks if needed, compile

## Phase 1: Comment Extraction & Planning

### Step 1: Locate and Parse Review Comments

Read the review email or document provided by the user. Extract:
- Editor decision (major/minor revision)
- AE summary comments
- Each individual reviewer comment (verbatim)

### Step 2: Interactive Organization

Present comments to the user organized by **manuscript section order** (recommended default), not reviewer order. This groups related comments together and avoids jumping between sections.

Use AskUserQuestion to confirm the plan:
- Show grouped comments with cross-references for overlapping concerns
- Assign severity: critical / major / minor / cosmetic
- Identify which comments from different reviewers address the same issue
- Ask user to confirm grouping or switch to reviewer-by-reviewer order

### Step 3: Initialize Response Letter

Copy the template from `assets/response_template.tex` to the project directory. Fill in:
- Manuscript ID, title, authors
- Opening paragraph (major vs minor revision tone)
- Reviewer section headers with per-reviewer thank-you sentences
- Empty `\begin{enumerate}...\end{enumerate}` blocks for each reviewer

### Step 4: Set Up Tracking

Create a TodoWrite checklist with all comments to track progress.

## Phase 2: Iterative Revision

For each comment (or group of related comments), execute this **exact sequence**:

### Step A: Read and Understand
Read the relevant manuscript section(s) to understand the current state.

### Step B: Propose Changes
Discuss the approach with the user. For complex issues, present options. Always follow CLAUDE.md academic writing rules — show before/after preview, wait for confirmation.

### Step C: Edit Manuscript
Apply changes to the main `.tex` file. Mark all new/modified text:
- **Inline text**: `\bl{new or modified text}`
- **Algorithm blocks**: `\color{blue}` after `\begin{algorithmic}`
- **Tables**: `\color{blue}` after `\centering`, caption with `\bl{Caption}`
- **New sections/appendices**: `\section{\bl{Title}}` + `\color{blue}` for body

### Step D: Write Response Entry
Immediately after editing the manuscript, add the response to the response letter `.tex` file. Each entry follows this structure:

```latex
\item {\bf Comment:} \emph{[verbatim reviewer text]}

{\bf Response:}
[Acknowledgment sentence]
[Explanation - 1-3 paragraphs depending on complexity]

[Lead-in sentence for quoted text]

\noindent \underline{Section X-Y:}
\bl{``[exact blue-marked text from manuscript]''}
```

**Key formatting rules:**
- Start with a thank-you sentence (vary phrasing across comments)
- End with `\noindent \underline{Section X:}` + blue-quoted text showing exact changes
- For overlapping comments, solve once and cross-reference: "see our response to Reviewer~1, Comment~3"
- For equations in response: wrap in `{\color{blue} \begin{equation*}...\end{equation*}}`
- For tables/algorithms in response: use `\fbox{\parbox{0.95\textwidth}{...}}` with `\color{blue}`

### Step E: Mark Complete
Update TodoWrite progress. Move to next comment.

## Phase 3: Finalization

### Handling Next Revision Round (Minor after Major)

When transitioning between revision rounds:
1. Remove all previous `\bl{...}` wrappers — keep content, strip the macro
2. Remove standalone `\color{blue}` lines (not the `\def\bl` definition)
3. Apply `\bl{...}` only to newly modified text in this round
4. Update response letter: new Manuscript ID (append .R1/.R2), new opening paragraph, only new responses

Use `perl -0777 -i -pe 's/\\bl\{((?:[^{}]|\{[^{}]*\})*)\}/$1/g' main.tex` to batch-remove `\bl{}` wrappers while preserving nested braces.

### Compilation and Verification

Compile both files with XeLaTeX and verify:
- All comments have corresponding responses
- Blue marking is consistent
- Cross-references are correct
- Page limit is met

## Additional Resources

### Reference Files

- **`references/response-letter-format.md`** - Complete formatting specification for response letters including all LaTeX patterns, per-reviewer section setup, figure/table counter prefixes, response writing depth guide, and acknowledgment sentence variations
- **`references/revision-workflow.md`** - Detailed step-by-step workflow with common scenarios (adding derivations, new experiments, notation fixes, assumption justifications)

### Template Files

- **`assets/response_template.tex`** - Base LaTeX template for the response letter with placeholders

## Quick Reference: Response Writing Depth

| Comment Type | Response Length | Structure |
|---|---|---|
| Typo/formatting | 1-2 sentences | Acknowledge + cite fix |
| Add content | 1 paragraph | Explain what/why + cite text |
| Technical concern | 2-3 paragraphs | Analysis + justification + cite |
| Major challenge | 3-5 paragraphs | Theory + evidence + changes + cite |

## Important Reminders

- Always show before/after preview before editing the manuscript (per CLAUDE.md rules)
- Never be defensive in responses — thank, then address constructively
- Reference exact sections, equations, figures by number
- When multiple reviewers raise the same issue, solve once and cross-reference
- The response letter blue-quoted text must exactly match the manuscript
- Keep the `\def\bl` macro in the manuscript preamble even after clearing old marks

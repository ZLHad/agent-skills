# IEEE Paper Revision Workflow - Detailed Guide

## Phase 1: Comment Extraction and Organization

### 1.1 Parsing the Review Email

Read the review email/document and extract:
- **Editor decision**: Major revision / Minor revision / Accept with minor changes
- **AE comments**: Summary of what the Associate Editor expects
- **Per-reviewer comments**: Each numbered or bulleted point from each reviewer

### 1.2 Structuring Comments

For each comment, create a structured entry:

```
Reviewer: [1/2/3]
Comment #: [N]
Original Text: [exact reviewer text]
Category: [technical / writing / experiment / clarification / formatting]
Severity: [critical / major / minor / cosmetic]
Related Sections: [Section II-A, Section IV-C, etc.]
Related Comments: [similar comments from other reviewers]
```

### 1.3 Organizing by Section (Recommended Default)

After extracting all comments, reorganize them by manuscript section order rather than reviewer order. This approach:
- Avoids jumping back and forth between sections
- Ensures related concerns from different reviewers are addressed together
- Produces a more coherent revision

**Grouping strategy:**
1. Group comments that touch the same section or related sections
2. Identify overlapping concerns (e.g., multiple reviewers asking for a notation table)
3. For overlapping concerns, solve once and cross-reference in responses

### 1.4 Creating the Revision Plan

Present the organized plan interactively using AskUserQuestion:

```
Revision Plan:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Group 1: Abstract & Introduction (Section I)
  - R1-C1: Add quantitative metrics to abstract
  - R1-C2: Strengthen gap analysis
  - R3-C1: More explicit gap analysis
  → Note: R1-C2 and R3-C1 overlap, can address together

Group 2: System Model (Section II)
  - R1-C3: Add notation table
  - R2-C1: Add notation table (same as R1-C3)
  - R2-C3: Position symbol ambiguity
  - R2-C4: Clarify time-varying parameters

Group 3: Algorithm Design (Section IV)
  - R2-C6: Fix Algorithm 1 prediction timing
  - R3-C4: Clarify Algorithm 2 convergence

...

Shall we proceed with this grouping, or would you prefer reviewer-by-reviewer order?
```

## Phase 2: Iterative Revision Execution

### 2.1 Per-Comment Workflow

For each comment (or group of related comments), follow this exact sequence:

**Step 1: Understand the issue**
- Re-read the reviewer's exact words
- Identify what section(s) of the manuscript are involved
- Read the relevant manuscript section(s)

**Step 2: Discuss approach with user**
- Propose a modification plan
- For complex issues, present multiple options
- Wait for user confirmation

**Step 3: Preview the change (per CLAUDE.md academic writing rules)**
- Show before/after comparison for the manuscript text
- For complex changes (formulas, multi-line), create `_preview_changes.md`
- Wait for user approval

**Step 4: Apply changes to the manuscript**
- Edit the main .tex file
- Mark new/modified text with `\bl{...}` or `\color{blue}`
- For algorithm/table blocks, use `\color{blue}` at the block level

**Step 5: Write the response letter entry**
- Immediately after modifying the manuscript, add the corresponding entry to the response .tex file
- Follow the Comment/Response format (see response-letter-format.md)
- Include the blue-quoted modified text at the end

**Step 6: Mark as complete**
- Update the TodoWrite tracker
- Move to the next comment

### 2.2 Handling Overlapping Comments

When multiple reviewers raise the same issue:
- Address it fully in the first occurrence
- In subsequent responses, write a brief acknowledgment and cross-reference:

```latex
{\bf Response:}
We thank the reviewer for this valuable suggestion. As suggested by the reviewer,
we have added a comprehensive notation table (Table~I: ``Summary of Main Notations'')
at the end of Section~I. The complete notation table is provided in our response to
Reviewer~1, Comment~3.
```

### 2.3 Types of Manuscript Changes

**Adding new text:**
```latex
% In manuscript - wrap new text with \bl{}
existing text \bl{new text added here} existing text
```

**Modifying existing text:**
```latex
% In manuscript - wrap modified text with \bl{}
\bl{modified version of the text}
```

**Adding new sections/appendices:**
```latex
\section{\bl{New Section Title}}
\color{blue}
[entire section content in blue]
```

**Adding new tables:**
```latex
\begin{table}[t]
    \caption{\bl{Table Caption}}
    \color{blue}
    \begin{tabular}{...}
    [table content]
    \end{tabular}
\end{table}
```

**Adding new algorithms:**
```latex
\begin{algorithm}[t]
\caption{\bl{Algorithm Title}}
\color{blue}
\begin{algorithmic}[1]
[algorithm content]
\end{algorithmic}
\end{algorithm}
```

## Phase 3: Finalization

### 3.1 Pre-submission Checklist

1. **All comments addressed**: Every reviewer comment has a response
2. **Blue marking consistency**: All new/modified text is properly marked in blue
3. **Cross-references valid**: All equation/figure/table numbers are correct
4. **Response letter complete**: Every comment has a well-structured response
5. **Compilation**: Both manuscript and response letter compile without errors
6. **Page limit**: Check IEEE page limit (typically 14-16 pages for regular papers)

### 3.2 Transitioning to Next Revision Round

If the paper goes through another revision round:
1. Remove all previous blue marks (keep content, remove `\bl{}` wrappers and `\color{blue}`)
2. Keep the `\def\bl` macro in preamble
3. Update the response letter:
   - Change Manuscript ID (append .R1, .R2, etc.)
   - Update opening paragraph tone
   - Delete old reviewer responses
   - Add new responses only for remaining comments
4. Apply new `\bl{...}` marks only for changes made in this round

## Common Scenarios and Patterns

### Scenario: Reviewer asks for derivation
1. Add derivation to appendix in manuscript
2. Add reference from main text to appendix: `\bl{(see Appendix~\ref{app:xxx} for detailed derivation)}`
3. In response: show the full derivation with equations, then cite the appendix text

### Scenario: Reviewer asks for new experiment/comparison
1. Run experiment, generate new figures/tables
2. Add to manuscript with blue marking
3. In response: explain methodology, present key results, cite the new figure/table

### Scenario: Reviewer questions model assumption
1. Provide theoretical justification
2. Optionally add clarification text to manuscript
3. In response: detailed analysis (may include equations), cite any changes

### Scenario: Reviewer suggests adding reference
1. Add citation to appropriate location
2. Mark with `\bl{~\cite{new_ref}}`
3. In response: brief acknowledgment, cite the modified sentence

### Scenario: Notation/formatting issue
1. Fix throughout manuscript (use search-replace)
2. Update notation table if applicable
3. In response: brief explanation of the fix

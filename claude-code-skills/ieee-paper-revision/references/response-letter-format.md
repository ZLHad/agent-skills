# Response Letter Formatting Guide

## Overview

This document provides the complete formatting specification for IEEE journal revision response letters. The response letter is a LaTeX document that accompanies the revised manuscript, providing point-by-point responses to all reviewer comments.

## Template Location

The base template is at `assets/response_template.tex`. Copy it to the project directory and fill in placeholders.

## Document Structure

### 1. Header Section

```latex
\large
Manuscript ID: VT-2025-06430  \\
Title: \normalsize\em Full Paper Title Here \em \large\\
Authors: Author1, Author2, Author3\\
```

### 2. Opening Paragraph

**For Major Revision:**
```latex
We would like to sincerely thank the Editor for handling the review process and the Reviewers for their insightful comments and constructive suggestions, which have significantly improved the quality of our manuscript. All comments have been carefully addressed, and a detailed point-by-point response is provided below.
```

**For Minor Revision:**
```latex
We would like to sincerely thank the Editor and the Reviewers for their continued support and valuable feedback throughout the review process. We are grateful that the manuscript has been accepted with minor revisions. The remaining comment(s) from Reviewer~X have been carefully addressed, and a detailed response is provided below.
```

### 3. Blue Marking Statement

Always include this line after the opening paragraph:
```latex
To facilitate the review process of the revised version, all changes are marked in {\bl {blue}} in the revised manuscript. Unless explicitly mentioned otherwise, equation and reference numbers cited in this document refer to those in the revised paper.
```

For minor revision (when there were previous blue marks):
```latex
To facilitate the review process, all newly revised text is marked in {\bl {blue}} in the revised manuscript.
```

### 4. Per-Reviewer Section Structure

Each reviewer section follows this pattern:

```latex
%=============================================================================================
% REVIEWER N
%=============================================================================================
\renewcommand{\figurename}{FIGURE}
\makeatletter \renewcommand{\thefigure}{X\@arabic\c@figure} \makeatother
\setcounter{figure}{0}
\makeatletter \renewcommand{\thetable}{X\@arabic\c@table} \makeatother
\setcounter{table}{0}

\section*{\Large \bf Comments of Reviewer N}

We sincerely thank Reviewer N for [personalized thank-you]. We have carefully addressed all the comments that were raised, as detailed below.

\begin{enumerate}

% ... individual comments here ...

\end{enumerate}
```

**Figure/Table counter prefixes by reviewer:**
- Reviewer 1: prefix `X` (e.g., FIGURE X1)
- Reviewer 2: prefix `B` (e.g., FIGURE B1)
- Reviewer 3: prefix `C` (e.g., FIGURE C1)

**Per-reviewer thank-you variations:**
- "the thorough review and constructive suggestions, which significantly helped in improving our manuscript"
- "the insightful comments and technical suggestions, which significantly helped in improving our revised manuscript"
- "the positive assessment and valuable suggestions, which significantly helped in improving our revised manuscript"

### 5. Individual Comment-Response Format

Each comment follows this exact structure:

```latex
\item {\bf Comment:} \emph{
[Exact reviewer comment text, copied verbatim from the review email]}

{\bf Response:}
[Response text here - see Response Writing Guide below]
```

### 6. Citing Modified Text in Response

After explaining the changes, always cite the exact modified text from the manuscript. The format is:

```latex
The following modification has been incorporated into the revised manuscript:

\noindent \underline{Section X-Y:}
\bl{``[Exact text as it appears in the revised manuscript, in blue]''}
```

**Multiple locations:**
```latex
The following modifications have been incorporated into the revised manuscript:

\noindent \underline{Section I-A:}
\bl{``[Modified text 1]''}

\noindent \underline{Section IV-C:}
\bl{``[Modified text 2]''}
```

**For algorithms or tables:**
Use a `\fbox{\parbox{...}}` environment with blue color:
```latex
\noindent \underline{Section IV-B (Algorithm 1):}
{\color{blue}
\begin{center}
\fbox{\parbox{0.95\textwidth}{
\textbf{Algorithm 1: Algorithm Name (Revised)}\\[2pt]
\hrule
\vspace{4pt}
[Algorithm pseudocode here]
}}
\end{center}
}
```

**For equations:**
```latex
{\color{blue}
\begin{equation*}
[equation content]
\end{equation*}
}
```

**For tables:**
```latex
\begin{table}[h]
\caption{\textcolor{blue}{Table Caption}}
\label{tab:label}
\renewcommand{\arraystretch}{1.1}
\centering
\small
\color{blue}
\begin{tabular}{...}
[table content]
\end{tabular}
\color{black}
\end{table}
```

## Response Writing Guide

### Response Structure Pattern

Each response typically follows a 3-part structure:

1. **Acknowledgment** (1 sentence): Thank the reviewer for the specific comment
2. **Explanation** (1-3 paragraphs): Describe what was done, provide reasoning/analysis
3. **Citation** (quoted text): Show the exact modified text

### Acknowledgment Sentence Patterns

- "We sincerely thank the reviewer for this valuable suggestion."
- "We sincerely appreciate this insightful comment."
- "We thank the reviewer for this important observation."
- "We greatly appreciate this constructive suggestion."
- "We thank the reviewer for this important clarification request."

### Explanation Depth by Comment Type

**Simple clarification/typo:**
- 1-2 sentences explaining the fix
- Cite modified text

**Technical suggestion (add content):**
- 1 paragraph explaining what was added and why
- Cite modified text

**Major technical concern:**
- 1 paragraph acknowledging and explaining approach
- 1-2 paragraphs with technical analysis/derivation
- 1 paragraph summarizing changes
- Cite modified text (possibly from multiple sections)

**Methodology challenge:**
- 1 paragraph acknowledging the concern
- 2-3 paragraphs with detailed theoretical/empirical justification
- 1 paragraph describing manuscript changes
- Cite modified text + possibly include new figures/tables/equations

### Key Principles

1. **Never be defensive** - Always thank, then address constructively
2. **Be specific** - Reference exact sections, equations, figures by number
3. **Show evidence** - Include derivations, experimental results, or citations
4. **Quote changes** - Always end with the exact blue-marked text from the manuscript
5. **Cross-reference** - When multiple reviewers raise similar issues, reference earlier responses: "The complete notation table is provided in our response to Reviewer~1, Comment~3."

## Blue Marking in Main Manuscript

### Using `\bl{...}` for inline text

```latex
\bl{This is new or modified text that appears in blue.}
```

### Using `\color{blue}` for blocks

For algorithm environments, tables, or large blocks:
```latex
\begin{algorithm}[t]
\caption{\bl{Algorithm Title}}
\label{alg:label}
\color{blue}
\begin{algorithmic}[1]
[algorithm content]
\end{algorithmic}
\end{algorithm}
```

### Minor Revision: Removing Old Blue Marks

When transitioning from major to minor revision:
1. Remove all `\bl{...}` wrappers: keep inner content, remove `\bl{` and `}`
2. Remove standalone `\color{blue}` lines
3. Keep the `\def\bl` definition in preamble
4. Apply `\bl{...}` only to newly modified text

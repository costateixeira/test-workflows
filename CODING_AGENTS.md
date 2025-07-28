# Prompt for a Coding Agent 

## Overview
This prompt is intended for coding agents, such as Copilot, to describe how to interact with the users when coding in this reporsitory.

A few key behviours required are:
* the agent should strive to make code that are valid.  if there is documentation or schemas given, they should be strictly adhereed to.
* if the user wants to package the suggested changes, use the `multifile.xml` format for packaging and managing proposed changes to repositories. The `multifile.xml` serves as a structured data format to facilitate collaboration between developers and coding agents, ensuring transparency, traceability, and ease of applying changes.
* if a diff is requested it should follow this format https://www.gnu.org/software/diffutils/manual/#Detailed-Unified.  the default behaviour should be to provide a minimal diff
* Avoid HTML Tags in Markdown as HTML tags in Markdown content can cause confusion and should be avoided.
* Minimizing Code Changes:
   - The user strongly prefers minimal changes to the code. Each line of code changed is considered a negative point.  too many negative points and the user is sad.  please minimize the number of negative points
   - The coding agent must strive to propose solutions that achieve the user's goals while making the fewest possible changes to the existing codebase.

9. **Respecting Coding Style Directives:**
   - Before answering a coding request, the coding agent must scan the root directory of the repository for files that define coding style, such as `codestyle.md`, `code_style.*`, or similar directives.
   - If such files exist, the agent must interpret and adhere to the coding style guidelines outlined in those files when providing its answers.


## Coding Agent Responsibilities
1. **Creating a `multifile.xml`:**
   - multifile should follow the schema defined here: https://github.com/WorldHealthOrganization/smart-base/blob/main/input/scripts/includes/multifile.xsd
   - the coding agent should follow the documentation in the schema on the intended use of multifile XML documents.
   - the multifile should be a valid file according to the multifile.csd schema
   - When a user requests coding help that involves generating or modifying code, the coding agent must create or update a `multifile.xml` file.
   - This file packages all suggested changes, metadata, and conversations in a structured format.
   - each file should contain the text contents as strings, wrapped in CDATA if needed
   - the agent should keep an ongoing log in conversation.md

2. **Asking About `multifile.xml` Updates:**
   - Each time the coding agent proposes changes to a file, it must ask the user whether they want the file added to or updated in the `multifile.xml`.
   - ideally this is a nice prompt with buttons to make it clear to the user that some action is being prompted

3. **Updating the `<conversation/>` Element:**
   - The `<conversation/>` element in the `multifile.xml` must be kept up to date with the ongoing discussion between the user and the agent.
   - This element should include the context of the user's request, the agent's responses, any clarifications, and details of the changes made.
   - The `@model` attribute must include a detailed description of the coding agent module, including its version.
   - the content of <conversation/> should be markdown wrapped in appropriate CDATA

4. **Proposing Changes:**
   - Each file modification or addition should be included as a `<file>` element within the `multifile.xml`.
   - The `@path` attribute of `<file>` specifies the location of the file in the repository.
   - If the changes are provided as a diff, the `@diff` attribute should indicate the diff format (e.g., `"unified"`), and the content of the `<file>` element should contain the diff.
   - If a diff is requested it should be a minimal diff. A minimal diff is one in which as few lines of codes are changed, and in which all existing whitespace and indentation is preserved.  we want to make it easy to see the proposed changes and only the proposed changes. 
   - The content of the `<file>` element must be plain text only. XML content is not allowed.

5. **Commit Message:**
   - The coding agent must generate a proposed `<commit/>` message under `<meta/>` in the `multifile.xml`.
   - The proposed commit message should summarize:
     - The reason for the changes made.
     - What the changes were.
   - This message will help the user understand the purpose and scope of the proposed changes.

6. **Updating the Issue Attribute:**
   - If the user requests help to solve a specific issue, the `@issue` attribute in the `<multifile>` element must be updated with the appropriate issue identifier.
   - If no specific issue is noted, the `@issue` attribute should be omitted entirely.

7. **Ensuring File Content Consistency:**
    - The content of files in the `multifile.xml` must always match the content of files in the workbench.
    - When updating the `multifile.xml`, the coding agent must ensure that the content of the files in the `multifile` and the workbench are synchronized.

8. **Keeping the `<conversation/>` Element Updated:**
    - The coding agent must ensure that the `<conversation/>` element in the `multifile.xml` is regularly updated with a complete log of the discussion, including:
      - User requests and clarifications.
      - The agent's responses and explanations.
      - Details about any changes made to files or metadata.
    - This ensures transparency and traceability in the collaboration process.

## How the User Applies Changes
- The user utilizes the `multifile_processor.py` script to process the `multifile.xml` file and apply the changes to their repository.
- The script handles verifying the branch, applying changes (or diffs), showing a diff to the user, committing the changes, and optionally pushing them to the remote repository.

## Location of the XSD
- The XML schema definition (XSD) for validating the `multifile.xml` file is located at:
  `@WorldHealthOrganization/smart-base/files/input/scripts/include/multifile.xsd`.

## Workflow Summary
1. **User Request:** The user asks for coding help or requests a solution to a specific issue.
2. **Agent Response:** The agent generates code suggestions and encapsulates them in a `multifile.xml`. If an issue is specified, the `@issue` attribute is updated with the relevant identifier. If no issue is specified, the `@issue` attribute should be omitted.
3. **User Review:** The user reviews the `multifile.xml` and uses the `multifile_processor.py` script to apply the changes.
4. **Validation:** The `multifile_processor.py` validates the `multifile.xml` against the provided XSD.
5. **Application:** The script applies the changes to the user's repository, ensuring alignment with the user's goals.

By following this workflow, the coding agent ensures a structured, transparent, and user-friendly approach to collaborative coding while respecting the user's preference for minimal code changes, adhering to any coding style guidelines defined in the repository, and ensuring consistency between the `multifile.xml` and the workbench.

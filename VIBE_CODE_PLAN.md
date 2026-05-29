# Vibe_Code-This Project Plan

### Section 1: Strict Development Workflow
You MUST adhere to these rules throughout the entire build process:
1. **Test-Driven Changes:** After every single functional change or feature addition, you must run the application to test and confirm functionality. Do not stack multiple unverified changes.
2. **Atomic Commits:** After every successful, tested change, you must immediately create a Git commit with a clear, descriptive message documenting what was added or fixed.
3. **Continuous Refactoring:** Regularly pause to review the codebase for refactoring opportunities. Ensure the PyQt6 architecture remains modular, clean, and maintainable.

### Section 2: Application Specifications
**Project Structure:**
- Bootstrapper: `Vibe_Code-This/Click_Here_To_Start.command` (Creates a venv, installs requirements, runs app).
- Source Code: `Vibe_Code-This/src/main.py`
- Data Storage: JSON format saving the full workspace state.

**Window Layout Requirements:**
1. **Top Row Controls:** 
   - "Import" button (loads a complete workspace from a JSON file).
   - "Save As" button (exports current state to a JSON file).
   - Center label displaying the name of the currently selected folder.
   - "Close" button (top right) which overrides default close, saves state to a default JSON, and exits.
2. **Three-Column Interface:**
   - **Column 1 (Folder Tree):** A tree widget supporting infinite nesting. Top right Add button prompts for name and optional color. Right-click context menu requires "rename", "duplicate", "delete" (with confirm prompt), and "change color". Folders must be drag-and-droppable into each other (with confirm prompt). Bottom has a search/filter box.
   - **Column 2 (Task List):** A list widget tied directly to the currently selected folder. Top right Add button for task title. Items must be reorderable via drag-and-drop (no nesting).
   - **Column 3 (Notes & Code Area):** A custom text editor tied to the selected task. Header contains: an edit mode toggle (Pencil icon), Attach file button, Open file button, and a "Trans" button.
      - *Edit Mode Logic:* If a task's note is empty, default to edit mode. If it has content, default to read-only when opened.

**Specific Custom Behaviors:**
- **The "Tab" Copy Block:** In the text editor, if the user presses `Tab`, it must intercept the keypress and start formatting typed characters into a distinct block (light grey background, thin dark outline). Pressing `Space` or `Return` exits the block formatting. Left-clicking anywhere on this formatted block must instantly copy its contents to the clipboard. Show instructional text/watermark: "Press tab for copy cblock".
- **The Translucent Window:** The "Trans" button spawns a small, frameless, semi-transparent, always-on-top, read-only window containing the exact content of the current text area for quick reference and copying.
- **Color Cascading:** When a folder's color is changed, the UI must dynamically update so that the folder item, its nested sub-folders, its tasks, and the border surrounding the Notes Column all inherit and reflect that specific color.

# Vibe-Code-This: The Anti-Bloat Snippet Manager ⚡️

![Vibe Code This Demo](images/demo.gif)
*(Note: Replace this placeholder with an actual GIF showing the 1-click copy and translucent window!)*

**Vibe-Code-This** is a blazing-fast, local-first note-taking and snippet manager. 

I got tired of the bloat in "Second Brain" apps like Notion and Obsidian just to save a few code snippets. I didn't want to manage plugins, build relational databases, or wait for cloud syncs. I just wanted a fast, local way to organize folders, track tasks, and instantly copy code blocks to my clipboard. 

So I built this.

## 🚀 Killer Features

*   **1-Click Copy Blocks:** Highlight any text and press the "🔲 Copy" button (or hit `Tab` while typing). It formats the block instantly. Later, just **left-click anywhere on the block** to instantly copy the contents to your clipboard. No more tedious highlighting. 
*   **The Translucent Window:** Click the "Trans" button to detach your notes into a frameless, semi-transparent window that stays pinned above your IDE or browser. Perfect for referencing code without switching monitors.
*   **100% Offline & Local:** Everything saves instantly to a local JSON file on your hard drive. No subscriptions, no cloud syncing, no accounts required.
*   **Cascading Colors:** Color-code your workflow. When you assign a color to a root folder, the entire UI gracefully inherits that accent color.

## 📥 Installation

**For Non-Developers (The Easy Way):**
You don't need to know Python to use this. Head over to the **[Releases](#)** tab on the right side of this page and download the pre-compiled binary for your operating system (Mac, Windows, or Linux). Extract it, click the app, and you're good to go.

**For Developers (Run from Source):**
1. Clone this repository: `git clone https://github.com/nordmendez/Vibe_Code_This-.git`
2. Run the bootstrapper script for Mac/Linux: `./Click_Here_To_Start.command`
   *Or install manually:*
   ```bash
   pip install pyqt6 qfluentwidgets qframelesswindow
   python src/main.py
   ```

## 🧠 Who is this for?
*   **Developers:** Saving terminal commands, boilerplate, and SQL queries.
*   **Prompt Engineers:** Organizing LLM prompts and context windows.
*   **Customer Support:** Organizing canned email replies.
*   **Writers & Researchers:** Pinning translucent reference notes above a Word document.

## ⚖️ License
The source code in this repository is provided for educational and non-commercial use under a custom Non-Commercial License. You are free to compile and use it for your personal workflows! 

---
*Built with Python & PyQt6.*

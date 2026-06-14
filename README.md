# 🗂️ File Organizer

A command-line Python tool that automatically sorts a messy folder into
organized subfolders by file type — with dry-run preview, full undo support,
and session logging.

---

## ✨ Features

- **Auto-categorizes** files into 10 folder types (Images, Audio, Video, Documents, Spreadsheets, Code, Archives, Executables, Design, Misc)
- **Dry-run mode** — preview exactly what will move before touching anything
- **Undo** — restore the last session with a single flag
- **Collision-safe** — never overwrites existing files; appends a counter instead (`file_2.pdf`)
- **Session logging** — every action written to `organizer.log` with timestamps
- **Summary report** — category breakdown printed to terminal after each run
- **Zero dependencies** — uses Python standard library only

---

## 🚀 Usage

```bash
# Organize the current directory
python organizer.py

# Organize a specific folder
python organizer.py ~/Downloads

# Preview what would happen (no files moved)
python organizer.py ~/Downloads --dry-run

# Undo the last organize session
python organizer.py ~/Downloads --undo
```

---

## 📁 Output Example

**Before:**
```
Downloads/
├── resume.pdf
├── photo.jpg
├── budget.xlsx
├── script.py
├── song.mp3
└── archive.zip
```

**After `python organizer.py ~/Downloads`:**
```
Downloads/
├── Documents/
│   └── resume.pdf
├── Images/
│   └── photo.jpg
├── Spreadsheets/
│   └── budget.xlsx
├── Code/
│   └── script.py
├── Audio/
│   └── song.mp3
└── Archives/
    └── archive.zip
```

---

## 📋 Terminal Report

```
  ────────────────────────────────────────────────────
                  📋  SESSION REPORT                 
  ────────────────────────────────────────────────────
  Directory            /Users/you/Downloads
  Mode                 LIVE
  Files processed      47
  Time elapsed         0.03s
  ────────────────────────────────────────────────────
  CATEGORY                      FILES
  ──────────────────────────────────
  📄  Documents                     18
  🖼️  Images                        12
  📊  Spreadsheets                   7
  🎬  Video                          4
  📝  Code                           3
  🗜️  Archives                       2
  📦  Misc                           1
  ──────────────────────────────────
  TOTAL                             47
  ────────────────────────────────────────────────────
```

---

## 📂 File Categories

| Folder | Extensions |
|---|---|
| Images | `.jpg` `.jpeg` `.png` `.gif` `.bmp` `.svg` `.webp` `.heic` |
| Audio | `.mp3` `.wav` `.aac` `.flac` `.ogg` `.m4a` |
| Video | `.mp4` `.mov` `.avi` `.mkv` `.wmv` `.webm` |
| Documents | `.pdf` `.doc` `.docx` `.txt` `.rtf` `.epub` |
| Spreadsheets | `.xls` `.xlsx` `.csv` `.numbers` |
| Code | `.py` `.js` `.html` `.css` `.json` `.sh` `.sql` + more |
| Archives | `.zip` `.tar` `.gz` `.rar` `.7z` |
| Executables | `.exe` `.dmg` `.pkg` `.deb` `.msi` |
| Design | `.psd` `.ai` `.fig` `.sketch` `.xd` `.eps` |
| Misc | Everything else |

---

## 🛠️ Requirements

- Python 3.9+
- No external libraries required

---

## 💡 How It Works

1. Scans the target directory for files (non-recursive, skips hidden files)
2. Maps each file's extension to a category
3. Creates the destination subfolder if it doesn't exist
4. Moves the file — renaming with a counter suffix if a name collision exists
5. Saves an undo manifest (`.organizer_undo.json`) for session reversal
6. Logs every action to `organizer.log` with timestamps

---

## 🔮 Potential Extensions

- [ ] Recursive mode (`--recursive` flag)
- [ ] Custom category config via JSON file
- [ ] Move vs. copy mode (`--copy` flag)
- [ ] Filter by date modified
- [ ] GUI wrapper with Tkinter

---

*Built by Madison · Phoenix, AZ · [Portfolio](https://yourusername.github.io)*

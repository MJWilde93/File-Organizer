"""
file_organizer.py
─────────────────
Automatically sorts files in a target directory into
categorized subfolders, logs every action, and produces
a summary report.

Usage:
    python organizer.py                    # organizes current directory
    python organizer.py ~/Downloads        # organizes a specific folder
    python organizer.py ~/Downloads --dry-run  # preview only, no changes
    python organizer.py ~/Downloads --undo     # restore last session
"""

import os
import sys
import shutil
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# ── Category → file extensions map ──────────────────────────────────────────
CATEGORIES = {
    "🖼️  Images":     [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg",
                        ".webp", ".ico", ".tiff", ".heic"],
    "🎵  Audio":       [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma"],
    "🎬  Video":       [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv",
                        ".webm", ".m4v"],
    "📄  Documents":   [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt",
                        ".pages", ".epub"],
    "📊  Spreadsheets":[".xls", ".xlsx", ".csv", ".numbers", ".ods"],
    "📝  Code":        [".py", ".js", ".ts", ".html", ".css", ".json",
                        ".xml", ".sh", ".bat", ".cpp", ".c", ".java",
                        ".rb", ".go", ".rs", ".php", ".sql", ".yaml", ".toml"],
    "🗜️  Archives":    [".zip", ".tar", ".gz", ".rar", ".7z", ".bz2", ".xz"],
    "💾  Executables": [".exe", ".dmg", ".pkg", ".deb", ".rpm", ".msi", ".app"],
    "🎨  Design":      [".psd", ".ai", ".xd", ".fig", ".sketch", ".indd",
                        ".eps", ".afdesign"],
    "📦  Misc":        [],   # catch-all
}

# Folder names (emoji stripped for actual directory names)
FOLDER_NAMES = {
    "🖼️  Images":      "Images",
    "🎵  Audio":       "Audio",
    "🎬  Video":       "Video",
    "📄  Documents":   "Documents",
    "📊  Spreadsheets":"Spreadsheets",
    "📝  Code":        "Code",
    "🗜️  Archives":    "Archives",
    "💾  Executables": "Executables",
    "🎨  Design":      "Design",
    "📦  Misc":        "Misc",
}

LOG_FILE   = "organizer.log"
UNDO_FILE  = ".organizer_undo.json"


# ── Logging setup ────────────────────────────────────────────────────────────
def setup_logging(target_dir: Path) -> logging.Logger:
    logger = logging.getLogger("organizer")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s  [%(levelname)s]  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler — saves to target directory
    fh = logging.FileHandler(target_dir / LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    # Console handler — clean output for the user
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_category(file_path: Path) -> str:
    """Return the category label for a given file extension."""
    ext = file_path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "📦  Misc"


def safe_destination(dest_folder: Path, filename: str) -> Path:
    """
    If a file with the same name already exists at the destination,
    append a counter suffix rather than overwriting.
    e.g. report.pdf → report_2.pdf
    """
    dest = dest_folder / filename
    if not dest.exists():
        return dest

    stem   = Path(filename).stem
    suffix = Path(filename).suffix
    counter = 2
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        dest = dest_folder / new_name
        if not dest.exists():
            return dest
        counter += 1


def build_extension_map() -> dict:
    """Reverse-map: extension → category label."""
    ext_map = {}
    for category, extensions in CATEGORIES.items():
        for ext in extensions:
            ext_map[ext] = category
    return ext_map


# ── Core logic ────────────────────────────────────────────────────────────────
def scan_files(target_dir: Path, logger: logging.Logger) -> list[Path]:
    """
    Return all files directly inside target_dir (non-recursive).
    Skips hidden files, the log file, and the undo file.
    """
    skip = {LOG_FILE, UNDO_FILE, "organizer.py"}
    files = []
    for item in target_dir.iterdir():
        if item.is_file() and item.name not in skip and not item.name.startswith("."):
            files.append(item)
    logger.debug(f"Scanned {target_dir}: found {len(files)} file(s) to process.")
    return files


def organize(target_dir: Path, dry_run: bool, logger: logging.Logger) -> dict:
    """
    Move files into category subfolders.
    Returns a move_log dict used for undo and reporting.
    """
    files  = scan_files(target_dir, logger)
    moves  = []                          # list of {from, to, category}
    stats  = defaultdict(int)            # category → count
    errors = []

    if not files:
        logger.info("  No files found to organize.")
        return {}

    mode_tag = "[DRY RUN] " if dry_run else ""

    for file_path in sorted(files):
        category    = get_category(file_path)
        folder_name = FOLDER_NAMES[category]
        dest_folder = target_dir / folder_name

        dest_path = safe_destination(dest_folder, file_path.name)

        if dry_run:
            logger.info(f"  {mode_tag}WOULD MOVE  {file_path.name}  →  {folder_name}/")
        else:
            try:
                dest_folder.mkdir(exist_ok=True)
                shutil.move(str(file_path), str(dest_path))
                logger.info(f"  ✓  Moved  {file_path.name}  →  {folder_name}/")
                logger.debug(f"    Full path: {dest_path}")
                moves.append({
                    "from":     str(file_path),
                    "to":       str(dest_path),
                    "category": category,
                })
            except Exception as e:
                logger.error(f"  ✗  Failed to move {file_path.name}: {e}")
                errors.append(str(file_path.name))

        stats[category] += 1

    # Save undo data
    if not dry_run and moves:
        undo_data = {
            "session_time": datetime.now().isoformat(),
            "moves": moves,
        }
        undo_path = target_dir / UNDO_FILE
        with open(undo_path, "w") as f:
            json.dump(undo_data, f, indent=2)
        logger.debug(f"Undo data saved to {undo_path}")

    return {
        "files_processed": len(files),
        "stats":           dict(stats),
        "errors":          errors,
        "dry_run":         dry_run,
    }


def undo_last_session(target_dir: Path, logger: logging.Logger):
    """Reverse the most recent organize session."""
    undo_path = target_dir / UNDO_FILE
    if not undo_path.exists():
        logger.info("  No undo data found. Run the organizer first.")
        return

    with open(undo_path) as f:
        undo_data = json.load(f)

    session_time = undo_data.get("session_time", "unknown")
    moves = undo_data.get("moves", [])

    logger.info(f"\n  Undoing session from {session_time}")
    logger.info(f"  Restoring {len(moves)} file(s)...\n")

    restored = 0
    for move in reversed(moves):
        src  = Path(move["to"])
        dest = Path(move["from"])
        if src.exists():
            try:
                shutil.move(str(src), str(dest))
                logger.info(f"  ↩  Restored  {src.name}  →  {dest.parent.name}/")
                restored += 1
            except Exception as e:
                logger.error(f"  ✗  Could not restore {src.name}: {e}")
        else:
            logger.warning(f"  ?  File not found, skipping: {src}")

    # Clean up empty category folders
    for folder_name in FOLDER_NAMES.values():
        folder = target_dir / folder_name
        if folder.exists() and not any(folder.iterdir()):
            folder.rmdir()
            logger.debug(f"Removed empty folder: {folder_name}/")

    undo_path.unlink()
    logger.info(f"\n  ✓  Restored {restored}/{len(moves)} file(s).")


# ── Report printer ────────────────────────────────────────────────────────────
def print_report(result: dict, target_dir: Path, elapsed: float):
    if not result:
        return

    dry_run = result.get("dry_run", False)
    stats   = result.get("stats", {})
    errors  = result.get("errors", [])
    total   = result.get("files_processed", 0)

    bar = "─" * 52
    print(f"\n  {bar}")
    print(f"  {'📋  SESSION REPORT':^50}")
    print(f"  {bar}")
    print(f"  {'Directory':<20} {str(target_dir)}")
    print(f"  {'Mode':<20} {'DRY RUN (no changes made)' if dry_run else 'LIVE'}")
    print(f"  {'Files processed':<20} {total}")
    print(f"  {'Time elapsed':<20} {elapsed:.2f}s")
    print(f"  {bar}")
    print(f"  {'CATEGORY':<28} {'FILES':>6}")
    print(f"  {'─'*34}")
    for category, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {category:<28} {count:>6}")
    print(f"  {'─'*34}")
    print(f"  {'TOTAL':<28} {total:>6}")
    if errors:
        print(f"\n  ⚠  Errors ({len(errors)}):")
        for e in errors:
            print(f"     • {e}")
    print(f"  {bar}\n")


# ── CLI entry point ───────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="🗂️  File Organizer — sort a messy folder in seconds.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python organizer.py                     Organize current directory
  python organizer.py ~/Downloads         Organize Downloads folder
  python organizer.py ~/Downloads --dry-run   Preview without moving
  python organizer.py ~/Downloads --undo      Undo last session
        """
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Target directory to organize (default: current directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be moved without actually moving anything"
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Undo the most recent organize session"
    )
    return parser.parse_args()


def main():
    args       = parse_args()
    target_dir = Path(args.directory).expanduser().resolve()

    if not target_dir.exists():
        print(f"\n  ✗  Directory not found: {target_dir}\n")
        sys.exit(1)

    if not target_dir.is_dir():
        print(f"\n  ✗  Path is not a directory: {target_dir}\n")
        sys.exit(1)

    logger = setup_logging(target_dir)

    print(f"\n  🗂️   File Organizer")
    print(f"  Target: {target_dir}\n")

    start_time = datetime.now()

    if args.undo:
        undo_last_session(target_dir, logger)
    else:
        if args.dry_run:
            print("  ── DRY RUN — no files will be moved ──\n")
        result = organize(target_dir, dry_run=args.dry_run, logger=logger)
        elapsed = (datetime.now() - start_time).total_seconds()
        print_report(result, target_dir, elapsed)

        if not args.dry_run and result.get("files_processed", 0) > 0:
            print(f"  💡  To undo:  python organizer.py {args.directory} --undo\n")


if __name__ == "__main__":
    main()

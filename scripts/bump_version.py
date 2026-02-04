#!/usr/bin/env python3
"""
Version Bump Script for JawTrackingSystem (JTS)

This script updates version, copyright year, and date across all project files.

Usage:
    # Preview changes (dry run)
    python scripts/bump_version.py --version 1.2.0 --year 2026 --dry-run

    # Apply version bump with new copyright year
    python scripts/bump_version.py --version 1.2.0 --year 2026

    # Version only (keep current copyright year)
    python scripts/bump_version.py --version 1.2.0

    # Show current version
    python scripts/bump_version.py --show-current

Files updated:
    - jts/*.py (8 modules): __version__, __copyright__, __date__
    - jts/__init__.py: __version__, __author__, __copyright__
    - examples/*.py (2 files): __version__, __copyright__, __date__
    - tests/*.py (4 files): __version__, __copyright__, __date__
    - setup.py: version variable
    - CITATION.cff: version, date-released
"""

__author__ = "Paul-Otto Müller"
__copyright__ = "Copyright 2026, Paul-Otto Müller"
__license__ = "CC BY-NC-SA 4.0"
__version__ = "1.1.1"

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional


# Project root directory (parent of scripts/)
PROJECT_ROOT = Path(__file__).parent.parent

# Files to update
PYTHON_FILES = [
    # jts/ modules
    "jts/core.py",
    "jts/helper.py",
    "jts/qualisys.py",
    "jts/qualisys_streaming.py",
    "jts/streaming.py",
    "jts/calibration_controllers.py",
    "jts/plotly_visualization.py",
    "jts/precision_analysis.py",
    # examples/
    "examples/hdf5_analysis_example.py",
    "examples/split_hdf5_example.py",
    # tests/
    "tests/test_core.py",
    "tests/test_helper.py",
    "tests/test_qualisys.py",
    "tests/test_precision_analysis.py",
]

INIT_FILE = "jts/__init__.py"
SETUP_FILE = "setup.py"
CITATION_FILE = "CITATION.cff"
THIS_SCRIPT = "scripts/bump_version.py"


def get_current_version() -> Optional[str]:
    """Extract current version from jts/core.py."""
    core_path = PROJECT_ROOT / "jts" / "core.py"
    if not core_path.exists():
        return None
    
    content = core_path.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    return match.group(1) if match else None


def get_current_year() -> Optional[str]:
    """Extract current copyright year from jts/core.py."""
    core_path = PROJECT_ROOT / "jts" / "core.py"
    if not core_path.exists():
        return None
    
    content = core_path.read_text(encoding="utf-8")
    match = re.search(r'__copyright__\s*=\s*["\']Copyright\s+(\d{4})', content)
    return match.group(1) if match else None


def update_python_file(
    filepath: Path,
    new_version: str,
    new_year: Optional[str],
    new_date: str,
    dry_run: bool = False
) -> list[str]:
    """Update version, copyright, and date in a Python file."""
    if not filepath.exists():
        return [f"  ⚠ File not found: {filepath}"]
    
    content = filepath.read_text(encoding="utf-8")
    original = content
    changes = []
    
    # Update __version__
    new_content, count = re.subn(
        r'(__version__\s*=\s*["\'])([^"\']+)(["\'])',
        rf'\g<1>{new_version}\g<3>',
        content
    )
    if count > 0:
        changes.append(f"  __version__ = \"{new_version}\"")
        content = new_content
    
    # Update __copyright__ (year only if provided)
    if new_year:
        new_content, count = re.subn(
            r'(__copyright__\s*=\s*["\']Copyright\s+)\d{4}',
            rf'\g<1>{new_year}',
            content
        )
        if count > 0:
            changes.append(f"  __copyright__ year = {new_year}")
            content = new_content
    
    # Update __date__ (convert to DD.MM.YYYY format)
    date_parts = new_date.split("-")  # YYYY-MM-DD
    formatted_date = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"  # DD.MM.YYYY
    new_content, count = re.subn(
        r'(__date__\s*=\s*["\'])([^"\']+)(["\'])',
        rf'\g<1>{formatted_date}\g<3>',
        content
    )
    if count > 0:
        changes.append(f"  __date__ = \"{formatted_date}\"")
        content = new_content
    
    if content != original and not dry_run:
        filepath.write_text(content, encoding="utf-8")
    
    return changes


def update_init_file(
    filepath: Path,
    new_version: str,
    new_year: Optional[str],
    dry_run: bool = False
) -> list[str]:
    """Update or create jts/__init__.py with version info."""
    changes = []
    
    new_copyright = f"Copyright {new_year}, Paul-Otto Müller" if new_year else "Copyright 2025, Paul-Otto Müller"
    
    new_content = f'''"""
JawTrackingSystem (JTS): A customizable, low-cost, optical jaw tracking system.

A modular and extensible Python package for analyzing jaw motion using motion capture data.
"""

__version__ = "1.1.1"
__author__ = "Paul-Otto Müller"
__copyright__ = "{new_copyright}"
__license__ = "CC BY-NC-SA 4.0"
'''
    
    changes.append(f"  __version__ = \"{new_version}\"")
    changes.append(f"  __author__ = \"Paul-Otto Müller\"")
    changes.append(f"  __copyright__ = \"{new_copyright}\"")
    
    if not dry_run:
        filepath.write_text(new_content, encoding="utf-8")
    
    return changes


def update_setup_py(
    filepath: Path,
    new_version: str,
    dry_run: bool = False
) -> list[str]:
    """Update version in setup.py."""
    if not filepath.exists():
        return [f"  ⚠ File not found: {filepath}"]
    
    content = filepath.read_text(encoding="utf-8")
    original = content
    changes = []
    
    # Update version = "X.Y.Z"
    new_content, count = re.subn(
        r'(version\s*=\s*["\'])([^"\']+)(["\'])',
        rf'\g<1>{new_version}\g<3>',
        content
    )
    if count > 0:
        changes.append(f"  version = \"{new_version}\"")
        content = new_content
    
    if content != original and not dry_run:
        filepath.write_text(content, encoding="utf-8")
    
    return changes


def update_citation_cff(
    filepath: Path,
    new_version: str,
    new_date: str,
    dry_run: bool = False
) -> list[str]:
    """Update version and date-released in CITATION.cff."""
    if not filepath.exists():
        return [f"  ⚠ File not found: {filepath}"]
    
    content = filepath.read_text(encoding="utf-8")
    original = content
    changes = []
    
    # Update version: X.Y.Z
    new_content, count = re.subn(
        r'(^version:\s*)[\d.]+',
        rf'\g<1>{new_version}',
        content,
        flags=re.MULTILINE
    )
    if count > 0:
        changes.append(f"  version: {new_version}")
        content = new_content
    
    # Update date-released: 'YYYY-MM-DD'
    new_content, count = re.subn(
        r"(^date-released:\s*')[^']+(')",
        rf"\g<1>{new_date}\g<2>",
        content,
        flags=re.MULTILINE
    )
    if count > 0:
        changes.append(f"  date-released: '{new_date}'")
        content = new_content
    
    if content != original and not dry_run:
        filepath.write_text(content, encoding="utf-8")
    
    return changes


def main():
    parser = argparse.ArgumentParser(
        description="Bump version across all JTS project files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--version", "-v",
        help="New version string (e.g., 1.2.0)"
    )
    parser.add_argument(
        "--year", "-y",
        help="New copyright year (e.g., 2026). If not provided, year is unchanged."
    )
    parser.add_argument(
        "--date", "-d",
        help="Release date in YYYY-MM-DD format. Defaults to today.",
        default=date.today().isoformat()
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview changes without writing to files."
    )
    parser.add_argument(
        "--show-current", "-s",
        action="store_true",
        help="Show current version and exit."
    )
    
    args = parser.parse_args()
    
    # Show current version
    current_version = get_current_version()
    current_year = get_current_year()
    
    if args.show_current:
        print(f"Current version: {current_version or 'unknown'}")
        print(f"Current copyright year: {current_year or 'unknown'}")
        return 0
    
    if not args.version:
        parser.error("--version is required (use --show-current to see current version)")
    
    print("=" * 60)
    print("JawTrackingSystem Version Bump")
    print("=" * 60)
    print(f"Current version:  {current_version or 'unknown'}")
    print(f"New version:      {args.version}")
    print(f"Copyright year:   {args.year or '(unchanged)'}")
    print(f"Release date:     {args.date}")
    print(f"Dry run:          {args.dry_run}")
    print("=" * 60)
    
    if args.dry_run:
        print("\n🔍 DRY RUN - No files will be modified\n")
    
    total_files = 0
    
    # Update Python files
    print("\n📁 Python modules:")
    for rel_path in PYTHON_FILES:
        filepath = PROJECT_ROOT / rel_path
        changes = update_python_file(filepath, args.version, args.year, args.date, args.dry_run)
        if changes:
            print(f"\n  {rel_path}:")
            for change in changes:
                print(f"    {change}")
            total_files += 1
    
    # Update this script too
    print(f"\n  {THIS_SCRIPT}:")
    this_script_path = PROJECT_ROOT / THIS_SCRIPT
    changes = update_python_file(this_script_path, args.version, args.year, args.date, args.dry_run)
    if changes:
        for change in changes:
            print(f"    {change}")
        total_files += 1
    
    # Update __init__.py
    print(f"\n📦 Package init ({INIT_FILE}):")
    init_path = PROJECT_ROOT / INIT_FILE
    changes = update_init_file(init_path, args.version, args.year, args.dry_run)
    for change in changes:
        print(f"  {change}")
    total_files += 1
    
    # Update setup.py
    print(f"\n⚙️  Setup file ({SETUP_FILE}):")
    setup_path = PROJECT_ROOT / SETUP_FILE
    changes = update_setup_py(setup_path, args.version, args.dry_run)
    for change in changes:
        print(f"  {change}")
    total_files += 1
    
    # Update CITATION.cff
    print(f"\n📝 Citation file ({CITATION_FILE}):")
    citation_path = PROJECT_ROOT / CITATION_FILE
    changes = update_citation_cff(citation_path, args.version, args.date, args.dry_run)
    for change in changes:
        print(f"  {change}")
    total_files += 1
    
    print("\n" + "=" * 60)
    if args.dry_run:
        print(f"✅ Dry run complete. {total_files} files would be modified.")
        print("   Run without --dry-run to apply changes.")
    else:
        print(f"✅ Version bump complete. {total_files} files modified.")
        print("\n⚠️  Don't forget to update CHANGELOG.md manually!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

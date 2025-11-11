"""Script to aggregate all markdown files from specs/rules into AGENTS.md."""

import sys
from pathlib import Path


def main():
    """Collect all markdown files from specs/rules and write to AGENTS.md."""
    project_root = Path(__file__).parent.parent
    rules_dir = project_root / "specs" / "rules"
    output_file = project_root / "AGENTS.md"

    if not rules_dir.exists():
        print(f"Error: Directory {rules_dir} does not exist", file=sys.stderr)
        return 1

    # Get all markdown files sorted alphabetically
    md_files = sorted(rules_dir.glob("*.md"))

    if not md_files:
        print(f"Warning: No markdown files found in {rules_dir}", file=sys.stderr)
        return 0

    # Collect content from all files
    content_parts = []
    for md_file in md_files:
        file_content = md_file.read_text(encoding="utf-8").strip()
        if file_content:
            content_parts.append(file_content)

    # Join with double newline separator
    aggregated_content = "\n\n---\n\n".join(content_parts)

    # Write to output file
    output_file.write_text(aggregated_content + "\n", encoding="utf-8")
    
    print(f"Successfully aggregated {len(content_parts)} files into {output_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

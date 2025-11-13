"""Script to aggregate all markdown files from specs/rules into AGENTS.md."""

import re
import sys
from pathlib import Path


def process_includes(content: str, project_root: Path) -> str:
    """Replace {include [text](path)} patterns with actual file content."""
    # Pattern to match {include [text](path)}
    pattern = r'\{include\s+\[([^\]]+)\]\(([^\)]+)\)\}'
    
    def replace_include(match):
        display_text = match.group(1)
        file_path = match.group(2)
        
        # Resolve path relative to project root
        # Remove leading ../../ and resolve
        resolved_path = project_root / file_path.lstrip('../')
        
        if not resolved_path.exists():
            print(f"Warning: File not found: {resolved_path}", file=sys.stderr)
            return match.group(0)  # Keep original if file not found
        
        try:
            file_content = resolved_path.read_text(encoding="utf-8")
            # Determine file extension for code block
            extension = resolved_path.suffix.lstrip('.')
            return f"```{extension}\n{file_content}\n```"
        except Exception as e:
            print(f"Error reading {resolved_path}: {e}", file=sys.stderr)
            return match.group(0)  # Keep original on error
    
    return re.sub(pattern, replace_include, content)


def main():
    """Collect all markdown files from specs/rules and write to AGENTS.md."""
    project_root = Path(__file__).parent.parent
    rules_dir = project_root / "specs" / "rules"
    output_file = project_root / "AGENTS.md"
    readme_content = (project_root / "README.md").read_text()

    if not rules_dir.exists():
        print(f"Error: Directory {rules_dir} does not exist", file=sys.stderr)
        return 1

    # Get all markdown files sorted alphabetically
    md_files = sorted(rules_dir.glob("*.md"))

    if not md_files:
        print(f"Warning: No markdown files found in {rules_dir}", file=sys.stderr)
        return 0

    # Collect content from all files
    content_parts = ["Файл генерируется автоматически из файлов в specs/rules/*", readme_content]
    for md_file in md_files:
        file_content = md_file.read_text(encoding="utf-8").strip()
        if file_content:
            # Process include patterns in the content
            file_content = process_includes(file_content, project_root)
            content_parts.append(file_content)

    # Join with double newline separator
    aggregated_content = "\n\n---\n\n".join(content_parts)

    # Write to output file
    output_file.write_text(aggregated_content + "\n", encoding="utf-8")
    
    print(f"Successfully aggregated {len(content_parts)} files into {output_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

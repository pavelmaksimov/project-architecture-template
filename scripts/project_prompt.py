import argparse
import fnmatch
import sys
import tomllib
from datetime import datetime
from pathlib import Path


def load_config(config_path: Path) -> dict:
    if not config_path.is_file():
        msg = f"Config file not found: {config_path}"
        raise FileNotFoundError(msg)

    if tomllib is None:  # pragma: no cover
        msg = "tomllib is not available. Use Python 3.11+."
        raise RuntimeError(msg)

    with config_path.open("rb") as f:
        return tomllib.load(f)


def is_binary_file(path: Path, sample_size: int = 4096) -> bool:
    """Heuristically detect binary files."""
    try:
        with path.open("rb") as f:
            sample = f.read(sample_size)
    except OSError:
        return True

    if b"\0" in sample:
        return True

    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        return True

    return False


def collect_files(project_root: Path, cfg: dict) -> list[Path]:
    include_patterns = cfg.get("include-paths") or []
    exclude_patterns = cfg.get("exclude_paths") or []
    exclude_empty = bool(cfg.get("exclude-empty-files", False))

    all_files: list[Path] = [p for p in project_root.rglob("*") if p.is_file()]
    selected: list[Path] = []

    for path in all_files:
        rel = path.relative_to(project_root).as_posix()

        if not any(fnmatch.fnmatch(rel, pattern) for pattern in include_patterns):
            continue

        if any(fnmatch.fnmatch(rel, pattern) for pattern in exclude_patterns):
            continue

        if exclude_empty and path.stat().st_size == 0:
            continue

        if is_binary_file(path):
            continue

        selected.append(path)

    # Stable ordering
    selected.sort(key=lambda p: p.relative_to(project_root).as_posix())
    return selected


def detect_language(path: Path) -> str:
    ext = path.suffix.lower()
    return {
        ".py": "python",
        ".md": "markdown",
        ".toml": "toml",
        ".txt": "",
        ".ini": "ini",
        ".yaml": "yaml",
        ".yml": "yaml",
    }.get(ext, "")


def build_output_content(project_root: Path, files: list[Path]) -> str:
    build_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts = [
        "# Project Prompt",
        f"build time {build_time}",
    ]

    for path in files:
        rel = path.relative_to(project_root).as_posix()
        language = detect_language(path)

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Should not happen due to is_binary_file, but be safe and skip
            continue

        parts.append(f"## {rel}")
        parts.append(f"```{language}".rstrip())
        parts.append(content)
        parts.append("```")

    parts.append("\n")

    return "\n".join(parts)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a single markdown prompt file from project sources.",
    )
    default_config = Path.cwd() / "project-prompt.toml"
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=default_config,
        help=f"Path to TOML config file (default: {default_config})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    project_root = Path(__file__).parent.parent.resolve()
    config_path = args.config.resolve()

    try:
        cfg = load_config(config_path)
    except Exception as exc:
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 1

    files = collect_files(project_root, cfg)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = project_root / f"project-prompt-{timestamp}.md"

    content = build_output_content(project_root, files)
    output_path.write_text(content, encoding="utf-8")

    chars_count = len(content)
    lines_count = content.count("\n")

    print(f"Project prompt saved to: {output_path}")
    print(f"Config used: {config_path}")
    print(f"Characters: {chars_count}")
    print(f"Tokens: ~{chars_count // 3}")
    print(f"Lines: {lines_count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

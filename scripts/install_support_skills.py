#!/usr/bin/env python3
"""Validate, back up, and atomically install the repository support skills."""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterator


SKILL_NAMES = (
    "analyze-intercom-faqs",
    "capture-zeno-support-screenshots",
    "draft-intercom-articles",
    "manage-zeno-support-content",
    "zeno-support-article-v1",
)
IGNORED_NAMES = {".DS_Store", "__pycache__"}


class InstallError(RuntimeError):
    pass


def tree_files(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*")):
        if any(part in IGNORED_NAMES for part in path.relative_to(root).parts):
            continue
        if path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise InstallError(f"symbolic links are not allowed in a skill: {path}")
        if path.is_file():
            yield path


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in tree_files(root):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        value = path.read_bytes()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(len(value).to_bytes(8, "big"))
        digest.update(value)
    return digest.hexdigest()


def validate_skill(path: Path, name: str) -> dict[str, Any]:
    if path.name != name or not path.is_dir() or path.is_symlink():
        raise InstallError(f"missing or unsafe repository skill directory: {path}")
    skill_file = path / "SKILL.md"
    agent_file = path / "agents" / "openai.yaml"
    if not skill_file.is_file() or not agent_file.is_file():
        raise InstallError(f"{name} must contain SKILL.md and agents/openai.yaml")
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---\n") or f"\nname: {name}\n" not in text:
        raise InstallError(f"{name}/SKILL.md has invalid frontmatter")
    if "description:" not in text.split("---", 2)[1]:
        raise InstallError(f"{name}/SKILL.md has no description")
    if "[TODO" in text or "TODO:" in text:
        raise InstallError(f"{name}/SKILL.md contains an unresolved TODO")
    if len(text.splitlines()) > 500:
        raise InstallError(f"{name}/SKILL.md exceeds 500 lines")
    if not list(tree_files(path)):
        raise InstallError(f"{name} is empty")
    return {"name": name, "sha256": tree_hash(path)}


def run_external_validator(skill: Path, target_root: Path) -> None:
    validator = target_root / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
    if not validator.is_file():
        return
    command = [sys.executable, str(validator), str(skill)]
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    detail = (completed.stdout + completed.stderr).strip()
    if completed.returncode and "No module named 'yaml'" in detail and shutil.which("uv"):
        completed = subprocess.run(
            ["uv", "run", "--with", "pyyaml", "python", str(validator), str(skill)],
            check=False,
            capture_output=True,
            text=True,
        )
        detail = (completed.stdout + completed.stderr).strip()
    if completed.returncode:
        raise InstallError(f"skill validator failed for {skill.name}: {detail}")


def resolve_roots(source: str | None, target: str | None) -> tuple[Path, Path]:
    repository = Path(__file__).resolve().parents[1]
    source_root = Path(source).expanduser().resolve() if source else repository / "skills"
    target_root = (
        Path(target).expanduser().resolve()
        if target
        else (Path.home() / ".codex" / "skills").resolve()
    )
    if source_root == target_root:
        raise InstallError("source and target skill roots must differ")
    if target_root == Path(target_root.anchor) or target_root == Path.home().resolve():
        raise InstallError("refusing to use a filesystem root or home directory as the target")
    return source_root, target_root


def install(source_root: Path, target_root: Path, *, dry_run: bool) -> dict[str, Any]:
    validations = []
    for name in SKILL_NAMES:
        skill = source_root / name
        validations.append(validate_skill(skill, name))
        run_external_validator(skill, target_root)
    result: dict[str, Any] = {
        "source": str(source_root),
        "target": str(target_root),
        "dry_run": dry_run,
        "skills": validations,
    }
    if dry_run:
        return result

    target_root.mkdir(parents=True, exist_ok=True)
    lock_path = target_root / ".support-skills-install.lock"
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        stage = Path(tempfile.mkdtemp(prefix=".support-skills-stage-", dir=target_root))
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        backup = target_root / ".backups" / f"support-skills-{stamp}"
        moved_old: list[str] = []
        installed: list[str] = []
        try:
            for item in validations:
                name = item["name"]
                shutil.copytree(
                    source_root / name,
                    stage / name,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
                )
                if tree_hash(stage / name) != item["sha256"]:
                    raise InstallError(f"staged copy hash mismatch for {name}")
            backup.mkdir(parents=True, exist_ok=False)
            for item in validations:
                name = item["name"]
                destination = target_root / name
                if destination.is_symlink():
                    raise InstallError(f"refusing to replace symbolic-link target: {destination}")
                if destination.exists():
                    os.replace(destination, backup / name)
                    moved_old.append(name)
                os.replace(stage / name, destination)
                installed.append(name)
                if tree_hash(destination) != item["sha256"]:
                    raise InstallError(f"installed copy hash mismatch for {name}")
        except BaseException:
            for name in reversed(installed):
                destination = target_root / name
                if destination.exists():
                    os.replace(destination, stage / f"failed-{name}")
                if name in moved_old and (backup / name).exists():
                    os.replace(backup / name, destination)
            for name in reversed(moved_old):
                destination = target_root / name
                if name not in installed and not destination.exists() and (backup / name).exists():
                    os.replace(backup / name, destination)
            raise
        finally:
            if stage.exists() and not any(stage.iterdir()):
                stage.rmdir()
        result.update(
            backup=str(backup),
            installed=installed,
            installed_hashes={name: tree_hash(target_root / name) for name in installed},
        )
        return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and atomically install the vendored Zeno support skills."
    )
    parser.add_argument("--source", help="repository skills directory")
    parser.add_argument("--target", help="target directory (default: ~/.codex/skills)")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        source, target = resolve_roots(args.source, args.target)
        result = install(source, target, dry_run=args.dry_run)
    except InstallError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps({"ok": True, **result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

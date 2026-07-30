#!/usr/bin/env python3
"""Atomically coordinate article-review ownership across parallel Codex threads."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


SCHEMA_VERSION = 1
EXIT_OTHER_THREAD = 2
EXIT_THREAD_BUSY = 3
EXIT_NOT_OWNER = 4
EXIT_INVALID = 5


class RegistryError(Exception):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def empty_registry() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "claims": {}}


def validate_token(value: str, field: str) -> str:
    value = value.strip()
    if not value:
        raise RegistryError(f"{field} must not be empty")
    if any(character in value for character in "\r\n\t"):
        raise RegistryError(f"{field} must be a single-line value")
    return value


def load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_registry()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RegistryError(f"cannot read registry: {error}") from error
    if data.get("schema_version") != SCHEMA_VERSION:
        raise RegistryError("unsupported registry schema_version")
    claims = data.get("claims")
    if not isinstance(claims, dict):
        raise RegistryError("registry claims must be an object")
    for article_id, claim in claims.items():
        if not isinstance(article_id, str) or not isinstance(claim, dict):
            raise RegistryError("registry contains an invalid claim")
        if not isinstance(claim.get("thread_id"), str) or not claim["thread_id"]:
            raise RegistryError(f"claim {article_id} has no thread_id")
    return data


def write_registry(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


@contextmanager
def locked_registry(path: Path) -> Iterator[dict[str, Any]]:
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(f"{path.name}.lock")
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        yield load_registry(path)


def emit(result: dict[str, Any]) -> None:
    print(json.dumps(result, indent=2, sort_keys=True))


def claim_article(args: argparse.Namespace) -> int:
    article_id = validate_token(args.article_id, "article_id")
    thread_id = validate_token(args.thread_id, "thread_id")
    title = validate_token(args.title, "title")
    workspace = str(Path(args.workspace).expanduser().resolve())
    registry_path = Path(args.registry).expanduser().resolve()

    with locked_registry(registry_path) as registry:
        claims = registry["claims"]
        existing = claims.get(article_id)
        if existing and existing["thread_id"] != thread_id:
            emit(
                {
                    "ok": False,
                    "status": "claimed_by_other_thread",
                    "article_id": article_id,
                    "claim": existing,
                }
            )
            return EXIT_OTHER_THREAD

        other_claims = [
            claim
            for claimed_article, claim in claims.items()
            if claimed_article != article_id and claim["thread_id"] == thread_id
        ]
        if other_claims:
            emit(
                {
                    "ok": False,
                    "status": "thread_already_has_active_claim",
                    "article_id": article_id,
                    "active_claims": other_claims,
                }
            )
            return EXIT_THREAD_BUSY

        if existing:
            emit(
                {
                    "ok": True,
                    "status": "already_owned_by_thread",
                    "article_id": article_id,
                    "claim": existing,
                }
            )
            return 0

        timestamp = utc_now()
        new_claim = {
            "article_id": article_id,
            "title": title,
            "thread_id": thread_id,
            "workspace": workspace,
            "reserved_at": timestamp,
        }
        claims[article_id] = new_claim
        registry["updated_at"] = timestamp
        write_registry(registry_path, registry)
        emit(
            {
                "ok": True,
                "status": "claimed",
                "article_id": article_id,
                "claim": new_claim,
            }
        )
        return 0


def status(args: argparse.Namespace) -> int:
    registry_path = Path(args.registry).expanduser().resolve()
    article_id = validate_token(args.article_id, "article_id")
    thread_id = validate_token(args.thread_id, "thread_id")

    with locked_registry(registry_path) as registry:
        claim = registry["claims"].get(article_id)
        if claim is None:
            emit(
                {
                    "ok": True,
                    "status": "unclaimed",
                    "article_id": article_id,
                    "thread_id": thread_id,
                }
            )
            return 0
        ownership = (
            "owned_by_thread"
            if claim["thread_id"] == thread_id
            else "claimed_by_other_thread"
        )
        emit(
            {
                "ok": ownership == "owned_by_thread",
                "status": ownership,
                "article_id": article_id,
                "claim": claim,
            }
        )
        return 0 if ownership == "owned_by_thread" else EXIT_OTHER_THREAD


def release_article(args: argparse.Namespace) -> int:
    registry_path = Path(args.registry).expanduser().resolve()
    article_id = validate_token(args.article_id, "article_id")
    thread_id = validate_token(args.thread_id, "thread_id")

    with locked_registry(registry_path) as registry:
        claims = registry["claims"]
        existing = claims.get(article_id)
        if existing is None:
            emit(
                {
                    "ok": True,
                    "status": "already_unclaimed",
                    "article_id": article_id,
                }
            )
            return 0
        if existing["thread_id"] != thread_id:
            emit(
                {
                    "ok": False,
                    "status": "not_claim_owner",
                    "article_id": article_id,
                    "claim": existing,
                }
            )
            return EXIT_NOT_OWNER

        del claims[article_id]
        registry["updated_at"] = utc_now()
        write_registry(registry_path, registry)
        emit({"ok": True, "status": "released", "article_id": article_id})
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Atomically coordinate active Intercom article reviews."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    claim_parser = subparsers.add_parser("claim")
    claim_parser.add_argument("--registry", required=True)
    claim_parser.add_argument("--thread-id", required=True)
    claim_parser.add_argument("--article-id", required=True)
    claim_parser.add_argument("--title", required=True)
    claim_parser.add_argument("--workspace", required=True)
    claim_parser.set_defaults(handler=claim_article)

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--registry", required=True)
    status_parser.add_argument("--thread-id", required=True)
    status_parser.add_argument("--article-id", required=True)
    status_parser.set_defaults(handler=status)

    release_parser = subparsers.add_parser("release")
    release_parser.add_argument("--registry", required=True)
    release_parser.add_argument("--thread-id", required=True)
    release_parser.add_argument("--article-id", required=True)
    release_parser.set_defaults(handler=release_article)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.handler(args)
    except RegistryError as error:
        emit({"ok": False, "status": "invalid", "error": str(error)})
        return EXIT_INVALID


if __name__ == "__main__":
    sys.exit(main())

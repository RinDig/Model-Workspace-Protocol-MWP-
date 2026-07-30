#!/usr/bin/env python3
"""Locally own Intercom article HTML and stage draft-only API changes."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import difflib
import fcntl
import hashlib
import html as html_lib
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zlib
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, MutableMapping, Sequence, TextIO


SCHEMA_VERSION = 1
CURRENT_STATE_SCHEMA_VERSION = 1
DEFAULT_STORE = "~/Documents/Intercom Articles"
DEFAULT_API_BASE = "https://api.intercom.io"
API_VERSION = "Preview"
TOKEN_ENV = "INTERCOM_ACCESS_TOKEN"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ARTICLE_ID_RE = re.compile(r"^[0-9]+$")
WRITE_PATH_RE = re.compile(r"^/articles/[0-9]+$")
DRAFT_PATH_RE = re.compile(r"^/articles/[0-9]+/draft$")
CURRENT_STATE_SOURCE = "intercom-mcp:list_articles"
MCP_ARTICLE_SOURCE = "intercom-mcp:get_article"
CURRENT_STATE_JSON = "current-state.json"
CURRENT_STATE_MARKDOWN = "CURRENT_STATE.md"
COMPARISON_DIR = "reviews"
COMPARISON_SCHEMA_VERSION = 1
SCREENSHOT_SCHEMA_VERSION = 1
SCREENSHOT_DIR = "screenshots"
SCREENSHOT_STATES = {
    "planned", "captured", "approved", "manual_upload_pending", "reconciled",
}
SCREENSHOT_ID_RE = re.compile(r"^shot-[0-9]{2,}$")
SCREENSHOT_PLACEHOLDER_RE = re.compile(
    r"^\[Screenshot:\s*(shot-[0-9]{2,})\s*\|\s*([^\]\n]+?)\s*\]$"
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_SCREENSHOT_BYTES = 10 * 1024 * 1024
SCREENSHOT_VIEWPORT = {"width": 1440, "height": 900}
INTERCOM_IMAGE_HOSTS = {
    "downloads.intercomcdn.com",
    "downloads.intercomcdn.eu",
    "downloads.au.intercomcdn.com",
    "uploads.intercomcdn.com",
    "uploads.intercomcdn.eu",
    "uploads.eu.intercomcdn.com",
    "uploads.au.intercomcdn.com",
    "uploads.intercomusercontent.com",
    "intercom-attachments.eu",
    "au.intercom-attachments.com",
    *(f"intercom-attachments-{index}.com" for index in range(1, 10)),
}
SCREENSHOT_BASELINE_FIELDS = (
    "id", "content_id", "workspace_id", "title", "description", "body",
    "author_id", "state", "created_at", "parent_ids", "parent_type",
    "default_locale", "url",
)
SCREENSHOT_IMMUTABLE_FIELDS = tuple(
    field for field in SCREENSHOT_BASELINE_FIELDS if field != "body"
)
CATALOG_SNAPSHOT_FIELDS = {
    "source", "fetched_at", "complete", "total_pages", "pages_fetched",
    "total_count", "articles",
}
CATALOG_ARTICLE_FIELDS = {
    "id", "content_id", "title", "description", "state", "parent_id", "parent_type",
    "author_id", "created_at", "updated_at", "url",
}
MCP_ARTICLE_SNAPSHOT_FIELDS = {"source", "fetched_at", "complete", "article"}
MCP_ARTICLE_FIELDS = {
    "id", "content_id", "workspace_id", "title", "description", "body", "author_id",
    "state", "created_at", "updated_at", "parent_id", "parent_type", "url",
}

CONTENT_TAGS = {
    "p", "br", "hr", "h1", "h2", "a", "img", "ul", "ol", "li",
    "table", "thead", "tbody", "tr", "th", "td", "iframe", "pre",
    "code", "b", "strong", "i", "em", "div",
}
VOID_TAGS = {"br", "hr", "img"}
INLINE_TAGS = {"br", "a", "img", "code", "b", "strong", "i", "em"}
INLINE_PARENTS = {"p", "h1", "h2", "a", "b", "strong", "i", "em"}
TEXT_CONTAINERS = {"p", "h1", "h2", "a", "li", "td", "th", "pre"}
ALLOWED_ATTRS = {
    "p": {"class"},
    "h1": {"class", "id"},
    "h2": {"class", "id"},
    "a": {"class", "href", "target", "rel", "title"},
    "img": {"src", "alt", "title", "width", "height", "style"},
    "div": {"class"},
    "iframe": {
        "src", "title", "allow", "allowfullscreen", "frameborder", "width", "height"
    },
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan"},
}
VIDEO_HOST_SUFFIXES = (
    "youtube.com", "youtube-nocookie.com", "youtu.be", "vimeo.com",
    "wistia.com", "wistia.net", "loom.com", "vidyard.com", "streamio.com",
    "stream-io-video.com",
)
REMOTE_COMPARE_FIELDS = (
    "id", "content_id", "workspace_id", "title", "description", "body", "author_id",
    "state", "updated_at", "has_unpublished_changes", "draft_updated_at",
    "parent_ids", "default_locale",
)
LIVE_COMPARE_FIELDS = (
    "id", "content_id", "workspace_id", "title", "description", "body", "author_id",
    "state", "updated_at", "parent_ids", "default_locale",
)
FORBIDDEN_PAYLOAD_KEYS = {
    "scheduled_publish_at", "scheduled_unpublish_at", "translated_content",
    "audience_ids", "folder_id", "ai_chatbot_availability",
    "ai_copilot_availability", "ai_sales_agent_availability",
}


class GuardrailError(RuntimeError):
    """A fail-closed local or remote guardrail."""


class ApiError(GuardrailError):
    """A sanitized API failure."""

    def __init__(self, message: str, *, status: int | None = None, ambiguous: bool = False):
        super().__init__(message)
        self.status = status
        self.ambiguous = ambiguous


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_text(encoded)


def redact(value: str, token: str | None) -> str:
    redacted = value
    if token:
        redacted = redacted.replace(token, "[REDACTED]")
    redacted = re.sub(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+", "Bearer [REDACTED]", redacted)
    return redacted[:1000]


def normalize_id(value: Any, field: str) -> int:
    raw = str(value)
    if not ARTICLE_ID_RE.fullmatch(raw):
        raise GuardrailError(f"{field} must contain digits only")
    return int(raw)


def normalize_id_list(values: Iterable[Any]) -> list[int]:
    return [normalize_id(value, "collection ID") for value in values]


def validate_slug(slug: str) -> str:
    if not SLUG_RE.fullmatch(slug):
        raise GuardrailError("slug must use lowercase letters, digits, and single hyphens")
    return slug


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not slug:
        raise GuardrailError("could not derive a slug; pass --slug explicitly")
    return validate_slug(slug[:80].rstrip("-"))


def resolve_store(raw: str | None = None, environ: Mapping[str, str] | None = None) -> Path:
    env = os.environ if environ is None else environ
    value = raw or env.get("INTERCOM_ARTICLES_HOME") or DEFAULT_STORE
    return Path(value).expanduser().resolve()


def resolve_review_copy_dir(raw: str | None) -> Path | None:
    if not raw:
        return None
    path = Path(raw).expanduser()
    if not path.is_absolute():
        raise GuardrailError("--review-copy-dir must be an absolute path inside the active workspace")
    resolved = path.resolve()
    if resolved == Path(resolved.anchor):
        raise GuardrailError("--review-copy-dir cannot be a filesystem root")
    return resolved


def atomic_write_text(path: Path, value: str, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def atomic_write_bytes(path: Path, value: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary_path, mode)
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GuardrailError(f"{label} is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise GuardrailError(f"{label} is not valid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise GuardrailError(f"{label} must contain a JSON object")
    return value


@contextlib.contextmanager
def store_lock(store: Path) -> Iterator[None]:
    store.mkdir(parents=True, exist_ok=True)
    lock_path = store / ".intercom-articles.lock"
    with lock_path.open("a+", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise GuardrailError(f"another local process holds the content-store lock: {lock_path}") from exc
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _safe_url(value: str, *, iframe: bool = False, image: bool = False) -> None:
    parsed = urllib.parse.urlsplit(value)
    if iframe:
        host = (parsed.hostname or "").lower()
        if parsed.scheme != "https" or not any(
            host == suffix or host.endswith(f".{suffix}") for suffix in VIDEO_HOST_SUFFIXES
        ):
            raise GuardrailError(f"unsupported iframe source: {value}")
        return
    if image:
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise GuardrailError(f"image source must be an absolute HTTP(S) URL: {value}")
        return
    if parsed.scheme and parsed.scheme.lower() not in {"http", "https", "mailto"}:
        raise GuardrailError(f"unsafe URL scheme: {parsed.scheme}")
    if value.lstrip().lower().startswith(("javascript:", "data:", "vbscript:")):
        raise GuardrailError("unsafe URL value")


class ArticleHTMLValidator(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[dict[str, Any]] = []
        self.meaningful = False

    def fail(self, message: str) -> None:
        raise GuardrailError(f"invalid article HTML: {message} (line {self.getpos()[0]})")

    def _ancestors(self, tag: str) -> list[dict[str, Any]]:
        return [frame for frame in self.stack if frame["tag"] == tag]

    def _validate_attrs(self, tag: str, attrs: Sequence[tuple[str, str | None]]) -> None:
        seen: set[str] = set()
        allowed = ALLOWED_ATTRS.get(tag, set())
        values: dict[str, str] = {}
        for raw_name, raw_value in attrs:
            name = raw_name.lower()
            if name in seen:
                self.fail(f"duplicate attribute {name!r} on <{tag}>")
            seen.add(name)
            if name.startswith("on") or name not in allowed:
                self.fail(f"unsupported attribute {name!r} on <{tag}>")
            values[name] = raw_value or ""

        classes = set(values.get("class", "").split())
        if classes:
            permitted: set[str] = set()
            if tag in {"p", "h1", "h2"}:
                permitted.add("intercom-align-center")
            if tag == "p":
                permitted.add("no-margin")
            if tag == "a":
                permitted.update({"intercom-content-link", "intercom-h2b-button"})
            if tag == "div":
                permitted.add("intercom-container")
            if not classes <= permitted:
                self.fail(f"unsupported class on <{tag}>: {', '.join(sorted(classes - permitted))}")
        if tag == "div" and classes != {"intercom-container"}:
            self.fail("<div> is allowed only as an Intercom image container")

        if tag in {"h1", "h2"} and "id" in values:
            if not re.fullmatch(r"h_[a-f0-9]{10}", values["id"]):
                self.fail(f"unsupported Intercom heading ID on <{tag}>")

        if tag == "a" and "href" in values:
            _safe_url(values["href"])
        if tag == "img":
            if not values.get("src"):
                self.fail("<img> requires src")
            _safe_url(values["src"], image=True)
            if "style" in values and re.sub(r"\s+", "", values["style"]).lower() not in {
                "height:auto", "height:auto;"
            }:
                self.fail("<img> supports only Intercom's height: auto style")
        if tag == "iframe":
            if not values.get("src"):
                self.fail("<iframe> requires src")
            _safe_url(values["src"], iframe=True)
        for numeric in ("width", "height", "colspan", "rowspan", "frameborder"):
            if numeric in values and values[numeric] and not values[numeric].isdigit():
                self.fail(f"{numeric} must be numeric on <{tag}>")

    def _mark_content(self) -> None:
        self.meaningful = True
        for frame in reversed(self.stack):
            if frame["tag"] == "li":
                frame["content"] = True
                break

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag not in CONTENT_TAGS:
            self.fail(f"unsupported tag <{tag}>")
        self._validate_attrs(tag, attrs)

        parent = self.stack[-1]["tag"] if self.stack else None
        if parent in INLINE_PARENTS and tag not in INLINE_TAGS:
            self.fail(f"<{parent}> may contain only inline content")
        if parent == "code":
            self.fail("<code> may contain text only")
        if parent == "pre" and tag != "code":
            self.fail("<pre> may contain only text and <code>")
        if parent == "iframe":
            self.fail("<iframe> must not contain child elements")
        if parent == "div" and tag != "img":
            self.fail("an Intercom image container may contain only one <img>")
        if tag == "div" and parent in INLINE_PARENTS | {"ul", "ol", "table", "thead", "tbody", "tr"}:
            self.fail("an Intercom image container is not allowed in this parent")
        if tag == "a" and self._ancestors("a"):
            self.fail("nested links are not supported")
        if parent in {"ul", "ol"} and tag != "li":
            self.fail(f"<{parent}> may contain only <li> children")
        if tag == "li" and parent not in {"ul", "ol"}:
            self.fail("<li> must be a direct child of <ul> or <ol>")
        if tag in {"ul", "ol"} and any(frame["tag"] in {"ul", "ol"} for frame in self.stack):
            self.fail("nested lists are not supported")
        if tag == "table":
            if self._ancestors("table"):
                self.fail("nested tables are not supported")
            if self._ancestors("li"):
                self.fail("tables are not supported inside list items")
        if tag in {"thead", "tbody"} and parent != "table":
            self.fail(f"<{tag}> must be a direct child of <table>")
        if tag == "tr" and parent not in {"table", "thead", "tbody"}:
            self.fail("<tr> must be a direct child of <table>, <thead>, or <tbody>")
        if tag in {"td", "th"} and parent != "tr":
            self.fail(f"<{tag}> must be a direct child of <tr>")
        if parent == "table" and tag not in {"thead", "tbody", "tr"}:
            self.fail(f"<table> has invalid direct child <{tag}>")
        if parent in {"thead", "tbody"} and tag != "tr":
            self.fail(f"<{parent}> may contain only <tr> children")
        if parent == "tr" and tag not in {"td", "th"}:
            self.fail(f"<tr> has invalid direct child <{tag}>")

        if tag in {"img", "hr", "iframe"}:
            self._mark_content()
        if tag == "img":
            for frame in reversed(self.stack):
                if frame["tag"] == "div":
                    frame["images"] += 1
                    if frame["images"] > 1:
                        self.fail("an Intercom image container must contain exactly one <img>")
                    break
        if tag == "li":
            list_frame = self.stack[-1]
            list_frame["items"] += 1
        if tag == "tr":
            for frame in reversed(self.stack):
                if frame["tag"] == "table":
                    frame["rows"] += 1
                    break
        if tag in {"td", "th"}:
            for frame in reversed(self.stack):
                if frame["tag"] == "tr":
                    frame["cells"] += 1
                    break
            for frame in reversed(self.stack):
                if frame["tag"] == "table":
                    frame["cells"] += 1
                    break

        if tag not in VOID_TAGS:
            frame: dict[str, Any] = {"tag": tag}
            if tag in {"ul", "ol"}:
                frame["items"] = 0
            elif tag == "li":
                frame["content"] = False
            elif tag == "table":
                frame.update(rows=0, cells=0)
            elif tag == "tr":
                frame["cells"] = 0
            elif tag == "div":
                frame["images"] = 0
            self.stack.append(frame)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() not in VOID_TAGS:
            self.fail(f"self-closing <{tag}> is not supported")
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in VOID_TAGS:
            self.fail(f"void tag <{tag}> must not have an end tag")
        if not self.stack or self.stack[-1]["tag"] != tag:
            expected = self.stack[-1]["tag"] if self.stack else "no tag"
            self.fail(f"mismatched </{tag}>; expected </{expected}>")
        frame = self.stack.pop()
        if tag in {"ul", "ol"} and frame["items"] < 1:
            self.fail(f"<{tag}> must contain at least one non-empty item")
        if tag == "li" and not frame["content"]:
            self.fail("list items must not be empty")
        if tag == "table" and (frame["rows"] < 1 or frame["cells"] < 1):
            self.fail("tables require at least one row and one cell")
        if tag == "tr" and frame["cells"] < 1:
            self.fail("table rows require at least one cell")
        if tag == "div" and frame["images"] != 1:
            self.fail("an Intercom image container must contain exactly one <img>")

    def handle_data(self, data: str) -> None:
        if not data.strip():
            return
        if not self.stack:
            self.fail("text must be inside a supported content element")
        if self.stack[-1]["tag"] in {"ul", "ol", "table", "thead", "tbody", "tr"}:
            self.fail(f"text is not allowed directly inside <{self.stack[-1]['tag']}>")
        if self.stack[-1]["tag"] == "iframe":
            self.fail("<iframe> must not contain text")
        if self.stack[-1]["tag"] == "div":
            self.fail("an Intercom image container may not contain text")
        if not any(frame["tag"] in TEXT_CONTAINERS for frame in self.stack):
            self.fail("prose must be inside a paragraph, heading, list item, table cell, link, or pre block")
        self._mark_content()

    def handle_comment(self, data: str) -> None:
        self.fail("comments are not supported")

    def handle_decl(self, decl: str) -> None:
        self.fail("complete HTML documents and declarations are not supported")

    def handle_pi(self, data: str) -> None:
        self.fail("processing instructions are not supported")

    def finish(self) -> None:
        self.close()
        if self.stack:
            self.fail(f"unclosed <{self.stack[-1]['tag']}>")
        if not self.meaningful:
            self.fail("article body must not be empty")


def validate_html(body: str) -> None:
    parser = ArticleHTMLValidator()
    try:
        parser.feed(body)
        parser.finish()
    except GuardrailError:
        raise
    except Exception as exc:
        raise GuardrailError(f"invalid article HTML: {exc}") from exc


INLINE_MARKDOWN_RE = re.compile(
    r"(\*\*[^*\n]+\*\*|`[^`\n]+`|\[[^\]\n]+\]\([^()\n]+\)|\*[^*\n]+\*)"
)
RAW_HTML_RE = re.compile(r"</?[A-Za-z][^>]*>")
ORDERED_ITEM_RE = re.compile(r"^(\d+)\.\s+(.+)$")
BULLET_ITEM_RE = re.compile(r"^-\s+(.+)$")
# Legacy placeholders remain readable so existing local drafts do not break. New
# screenshot-managed drafts are validated against SCREENSHOT_PLACEHOLDER_RE.
SCREENSHOT_RE = re.compile(r"^\[Screenshot:\s*[^\]]+\]$")


def parse_screenshot_placeholder(value: str) -> tuple[str, str] | None:
    match = SCREENSHOT_PLACEHOLDER_RE.fullmatch(value.strip())
    if not match:
        return None
    return match.group(1), match.group(2).strip()


def screenshot_placeholders(body: str) -> list[tuple[str, str]]:
    parser = CanonicalHTML()
    validate_html(body)
    parser.feed(body)
    parser.close()
    placeholders: list[tuple[str, str]] = []
    for event in parser.events:
        if event[0] != "text":
            continue
        parsed = parse_screenshot_placeholder(str(event[1]))
        if parsed:
            placeholders.append(parsed)
    return placeholders


def render_markdown_inline(value: str) -> str:
    """Render the deliberately small inline subset emitted by the Zeno writer."""
    if RAW_HTML_RE.search(value) or "![" in value:
        raise GuardrailError("Markdown handoff must not contain raw HTML or images")
    output: list[str] = []
    position = 0
    for match in INLINE_MARKDOWN_RE.finditer(value):
        plain = value[position:match.start()]
        if any(marker in plain for marker in ("**", "`", "[", "]", "*")):
            raise GuardrailError("Markdown handoff contains unbalanced or unsupported inline markup")
        output.append(html_lib.escape(plain))
        token = match.group(0)
        if token.startswith("**"):
            output.append(f"<strong>{html_lib.escape(token[2:-2])}</strong>")
        elif token.startswith("`"):
            output.append(f"<code>{html_lib.escape(token[1:-1])}</code>")
        elif token.startswith("["):
            label, url = token[1:].split("](", 1)
            url = url[:-1]
            parsed = urllib.parse.urlsplit(url)
            if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
                raise GuardrailError("Markdown links must be verified absolute HTTPS URLs")
            _safe_url(url)
            output.append(
                f'<a href="{html_lib.escape(url, quote=True)}">{html_lib.escape(label)}</a>'
            )
        else:
            output.append(f"<em>{html_lib.escape(token[1:-1])}</em>")
        position = match.end()
    remainder = value[position:]
    if any(marker in remainder for marker in ("**", "`", "[", "]", "*")):
        raise GuardrailError("Markdown handoff contains unbalanced or unsupported inline markup")
    output.append(html_lib.escape(remainder))
    rendered = "".join(output).strip()
    if not rendered:
        raise GuardrailError("Markdown block must not be empty")
    return rendered


def markdown_to_intercom_html(markdown: str, expected_title: str) -> str:
    """Convert constrained review Markdown into an Intercom body fragment."""
    if "\t" in markdown:
        raise GuardrailError("Markdown handoff must use spaces, not tabs")
    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    first = next((index for index, line in enumerate(lines) if line.strip()), None)
    if first is None or not lines[first].startswith("# ") or lines[first].startswith("## "):
        raise GuardrailError("Markdown handoff must start with exactly one H1 title")
    title = lines[first][2:].strip()
    if title != expected_title.strip():
        raise GuardrailError("Markdown H1 must exactly match the local article title")

    blocks: list[str] = []
    index = first + 1
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue
        if line.startswith("# "):
            raise GuardrailError("Markdown handoff must contain exactly one H1 title")
        if line.startswith("###") or stripped.startswith(">") or stripped.startswith("|"):
            raise GuardrailError("Markdown handoff contains an unsupported block structure")
        if line.startswith("## "):
            blocks.append(f"<h2>{render_markdown_inline(line[3:].strip())}</h2>")
            index += 1
            continue
        if stripped.startswith("```"):
            code_lines: list[str] = []
            index += 1
            while index < len(lines) and lines[index].strip() != "```":
                code_lines.append(lines[index])
                index += 1
            if index >= len(lines):
                raise GuardrailError("Markdown code fence is not closed")
            blocks.append(f"<pre><code>{html_lib.escape(chr(10).join(code_lines))}</code></pre>")
            index += 1
            continue

        ordered = ORDERED_ITEM_RE.match(stripped)
        bullet = BULLET_ITEM_RE.match(stripped)
        if (ordered or bullet) and not line[:1].isspace():
            list_tag = "ol" if ordered else "ul"
            items: list[str] = []
            while index < len(lines):
                if lines[index][:1].isspace():
                    break
                candidate = lines[index].strip()
                match = ORDERED_ITEM_RE.match(candidate) if list_tag == "ol" else BULLET_ITEM_RE.match(candidate)
                if not match:
                    break
                content = match.group(2) if list_tag == "ol" else match.group(1)
                rendered_item = render_markdown_inline(content)
                index += 1
                while index < len(lines) and not lines[index].strip():
                    index += 1
                if index < len(lines) and lines[index][:1].isspace() and SCREENSHOT_RE.fullmatch(lines[index].strip()):
                    screenshot = html_lib.escape(lines[index].strip())
                    rendered_item += f"<p><em>{screenshot}</em></p>"
                    index += 1
                    while index < len(lines) and not lines[index].strip():
                        index += 1
                items.append(f"<li>{rendered_item}</li>")
            blocks.append(f"<{list_tag}>{''.join(items)}</{list_tag}>")
            continue

        if SCREENSHOT_RE.fullmatch(stripped):
            blocks.append(f"<p><em>{html_lib.escape(stripped)}</em></p>")
            index += 1
            continue
        if line[:1].isspace():
            raise GuardrailError("Markdown handoff contains unsupported indentation")

        paragraph: list[str] = []
        while index < len(lines):
            candidate = lines[index]
            candidate_stripped = candidate.strip()
            if not candidate_stripped:
                break
            if (
                candidate.startswith("#")
                or candidate_stripped.startswith("```")
                or ORDERED_ITEM_RE.match(candidate_stripped)
                or BULLET_ITEM_RE.match(candidate_stripped)
                or SCREENSHOT_RE.fullmatch(candidate_stripped)
            ):
                break
            if candidate[:1].isspace():
                raise GuardrailError("Markdown handoff contains unsupported indentation")
            paragraph.append(candidate_stripped)
            index += 1
        if not paragraph:
            raise GuardrailError(f"unsupported Markdown block: {stripped[:80]}")
        blocks.append(f"<p>{render_markdown_inline(' '.join(paragraph))}</p>")

    body = "\n".join(blocks) + "\n"
    validate_html(body)
    return body


class CanonicalHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.events: list[tuple[Any, ...]] = []
        self.pre_depth = 0
        self.stack: list[tuple[str, bool]] = []

    @staticmethod
    def attrs(
        tag: str, attrs: Sequence[tuple[str, str | None]]
    ) -> tuple[tuple[str, str], ...]:
        normalized: list[tuple[str, str]] = []
        for name, value in attrs:
            name = name.lower()
            value = value or ""
            if tag in {"h1", "h2"} and name == "id":
                continue
            if tag == "img" and name == "style":
                continue
            if tag == "img" and name == "src":
                parsed = urllib.parse.urlsplit(value)
                if (parsed.hostname or "").lower() in INTERCOM_IMAGE_HOSTS:
                    value = urllib.parse.urlunsplit(
                        (parsed.scheme.lower(), parsed.netloc.lower(), parsed.path, "", "")
                    )
            if name == "class":
                classes = sorted(
                    item for item in value.split()
                    if item not in {"intercom-content-link", "no-margin"}
                )
                if not classes:
                    continue
                value = " ".join(classes)
            if tag == "a" and name == "target" and value == "_blank":
                continue
            normalized.append((name, value))
        return tuple(sorted(normalized))

    @staticmethod
    def tag(tag: str) -> str:
        return {"b": "strong", "i": "em", "h1": "h2"}.get(tag, tag)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        classes = {
            value
            for name, raw in attrs
            if name.lower() == "class"
            for value in (raw or "").split()
        }
        suppress = (
            (tag == "p" and bool(self.stack) and self.stack[-1][0] == "li")
            or (tag == "div" and classes == {"intercom-container"})
        )
        if tag not in VOID_TAGS:
            self.stack.append((tag, suppress))
        if not suppress:
            self.events.append(("start", self.tag(tag), self.attrs(tag, attrs)))
        if tag == "pre":
            self.pre_depth += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self.events.append(("start", self.tag(tag), self.attrs(tag, attrs)))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        source_tag, suppress = self.stack.pop()
        if source_tag != tag:
            raise GuardrailError(f"canonical HTML stack mismatch for </{tag}>")
        if not suppress:
            self.events.append(("end", self.tag(tag)))
        if tag == "pre":
            self.pre_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.pre_depth and not data.strip():
            return
        self.events.append(("text", data if self.pre_depth else re.sub(r"\s+", " ", data)))


def canonical_html(body: str) -> tuple[tuple[Any, ...], ...]:
    validate_html(body)
    parser = CanonicalHTML()
    parser.feed(body)
    parser.close()
    events: list[tuple[Any, ...]] = []
    for event in parser.events:
        if event == ("end", "p") and events and events[-1] == ("start", "p", ()):
            events.pop()
            continue
        events.append(event)
    return tuple(events)


def html_equivalent(local: str, remote: str) -> bool:
    return canonical_html(local) == canonical_html(remote)


def derive_editor_url_template(content_id: str, sample_url: str) -> str:
    content_id = str(normalize_id(content_id, "sample content ID"))
    parsed = urllib.parse.urlsplit(sample_url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise GuardrailError("sample editor URL must be an HTTPS URL without embedded credentials")
    if content_id in parsed.netloc:
        raise GuardrailError("sample content ID must appear in the editor URL path, query, or fragment")
    pattern = re.compile(rf"(?<![0-9]){re.escape(content_id)}(?![0-9])")
    matches = list(pattern.finditer(sample_url))
    if len(matches) != 1:
        raise GuardrailError("sample editor URL must contain the complete content ID exactly once")
    match = matches[0]
    template = sample_url[: match.start()] + "{content_id}" + sample_url[match.end() :]
    if template.replace("{content_id}", content_id) != sample_url:
        raise GuardrailError("could not derive a reliable direct editor link template")
    return template


def editor_url(config: Mapping[str, Any], content_id: Any) -> str:
    value = str(normalize_id(content_id, "content ID"))
    template = config.get("editor_url_template")
    if not isinstance(template, str) or template.count("{content_id}") != 1:
        raise GuardrailError("config has no reliable editor URL template; run setup again")
    result = template.replace("{content_id}", value)
    parsed = urllib.parse.urlsplit(result)
    if parsed.scheme != "https" or not parsed.hostname:
        raise GuardrailError("generated editor URL is invalid")
    return result


def validate_api_base(value: str) -> str:
    parsed = urllib.parse.urlsplit(value.rstrip("/"))
    local = parsed.hostname in {"127.0.0.1", "localhost"}
    if (parsed.scheme != "https" and not (local and parsed.scheme == "http")) or not parsed.hostname:
        raise GuardrailError("API base must be HTTPS (HTTP is accepted only for local tests)")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise GuardrailError("API base must contain only scheme and host, with an optional port")
    return value.rstrip("/")


def load_config(store: Path) -> dict[str, Any]:
    config = load_json(store / "config.json", "config")
    required = {"api_base", "workspace_id", "default_author_id", "default_locale", "editor_url_template"}
    missing = sorted(required - config.keys())
    if missing:
        raise GuardrailError(f"config is missing fields: {', '.join(missing)}")
    config["api_base"] = validate_api_base(str(config["api_base"]))
    if not str(config["workspace_id"]).strip():
        raise GuardrailError("workspace_id must not be empty")
    config["default_author_id"] = normalize_id(config["default_author_id"], "default author ID")
    if config["default_locale"] != "en":
        raise GuardrailError("only the default English locale is supported")
    editor_url(config, 1)
    return config


def empty_manifest() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "articles": {}}


def load_manifest(store: Path, *, create: bool = False) -> dict[str, Any]:
    path = store / "manifest.json"
    if create and not path.exists():
        return empty_manifest()
    manifest = load_json(path, "manifest")
    if manifest.get("schema_version") != SCHEMA_VERSION or not isinstance(manifest.get("articles"), dict):
        raise GuardrailError("manifest schema is unsupported")
    return manifest


def screenshot_manifest_path(store: Path, slug: str) -> Path:
    return store / SCREENSHOT_DIR / validate_slug(slug) / "manifest.json"


def load_screenshot_manifest(store: Path, slug: str, *, required: bool = True) -> dict[str, Any] | None:
    path = screenshot_manifest_path(store, slug)
    if not path.exists() and not required:
        return None
    value = load_json(path, "screenshot manifest")
    if (
        value.get("schema_version") != SCREENSHOT_SCHEMA_VERSION
        or value.get("slug") != validate_slug(slug)
        or value.get("state") not in SCREENSHOT_STATES
        or not isinstance(value.get("screenshots"), list)
    ):
        raise GuardrailError("screenshot manifest schema is unsupported")
    return value


def _clean_string(value: Any, field: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise GuardrailError(f"{field} must be a string")
    cleaned = value.strip()
    if not allow_empty and not cleaned:
        raise GuardrailError(f"{field} must not be empty")
    if "\x00" in cleaned:
        raise GuardrailError(f"{field} contains an invalid character")
    return cleaned


def _validate_origin(value: Any) -> str:
    origin = _clean_string(value, "screenshot allowed origin")
    parsed = urllib.parse.urlsplit(origin)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        raise GuardrailError("screenshot allowed origins must be HTTPS origins without paths or credentials")
    return urllib.parse.urlunsplit(("https", parsed.netloc.lower(), "", "", ""))


def validate_screenshot_plan(value: Mapping[str, Any]) -> dict[str, Any]:
    allowed_fields = {
        "schema_version", "allowed_origins", "workspace_sentinel", "screenshots",
    }
    if set(value) != allowed_fields or value.get("schema_version") != SCREENSHOT_SCHEMA_VERSION:
        raise GuardrailError("screenshot plan fields or schema version are invalid")
    origins_raw = value.get("allowed_origins")
    if not isinstance(origins_raw, list) or not origins_raw:
        raise GuardrailError("screenshot plan requires at least one allowed origin")
    origins = [_validate_origin(origin) for origin in origins_raw]
    if len(origins) != len(set(origins)):
        raise GuardrailError("screenshot plan contains duplicate allowed origins")
    sentinel = _clean_string(value.get("workspace_sentinel"), "workspace_sentinel")
    shots_raw = value.get("screenshots")
    if not isinstance(shots_raw, list) or not shots_raw:
        raise GuardrailError("screenshot plan requires at least one screenshot")
    fields = {
        "id", "placement", "capture_goal", "expected_ui_labels", "framing",
        "alt_text", "setup_notes", "status",
    }
    shots: list[dict[str, Any]] = []
    ids: set[str] = set()
    for index, raw in enumerate(shots_raw, start=1):
        if not isinstance(raw, dict) or set(raw) != fields:
            raise GuardrailError(f"screenshot plan item {index} has invalid fields")
        shot_id = _clean_string(raw.get("id"), f"screenshot {index} id")
        if not SCREENSHOT_ID_RE.fullmatch(shot_id):
            raise GuardrailError("screenshot IDs must use shot- followed by at least two digits")
        if shot_id in ids:
            raise GuardrailError(f"duplicate screenshot ID: {shot_id}")
        ids.add(shot_id)
        labels_raw = raw.get("expected_ui_labels")
        if (
            not isinstance(labels_raw, list)
            or not labels_raw
            or any(not isinstance(label, str) or not label.strip() for label in labels_raw)
        ):
            raise GuardrailError(f"{shot_id} expected_ui_labels must be a non-empty string list")
        labels = [label.strip() for label in labels_raw]
        if len(labels) != len(set(labels)):
            raise GuardrailError(f"{shot_id} contains duplicate expected UI labels")
        status = raw.get("status")
        if status not in {"required", "optional"}:
            raise GuardrailError(f"{shot_id} status must be required or optional")
        shots.append({
            "id": shot_id,
            "placement": _clean_string(raw.get("placement"), f"{shot_id} placement"),
            "capture_goal": _clean_string(raw.get("capture_goal"), f"{shot_id} capture_goal"),
            "expected_ui_labels": labels,
            "framing": _clean_string(raw.get("framing"), f"{shot_id} framing"),
            "alt_text": _clean_string(raw.get("alt_text"), f"{shot_id} alt_text"),
            "setup_notes": _clean_string(
                raw.get("setup_notes"), f"{shot_id} setup_notes", allow_empty=True
            ),
            "status": status,
        })
    return {
        "schema_version": SCREENSHOT_SCHEMA_VERSION,
        "allowed_origins": origins,
        "workspace_sentinel": sentinel,
        "screenshots": shots,
    }


def _load_screenshot_plan_file(path_value: str) -> dict[str, Any]:
    path = _resolve_safe_input(path_value, "screenshot plan")
    return validate_screenshot_plan(load_json(path, "screenshot plan"))


def _resolve_safe_input(path_value: str, label: str) -> Path:
    raw = Path(path_value).expanduser()
    if not raw.is_absolute():
        raise GuardrailError(f"{label} path must be absolute")
    if ".." in raw.parts:
        raise GuardrailError(f"{label} path traversal is not allowed")
    if raw.is_symlink():
        raise GuardrailError(f"{label} must not be a symbolic link")
    resolved = raw.resolve()
    if not resolved.is_file():
        raise GuardrailError(f"{label} is missing or is not a regular file: {resolved}")
    return resolved


def _shot_by_id(screenshot_manifest: Mapping[str, Any], shot_id: str) -> dict[str, Any]:
    if not SCREENSHOT_ID_RE.fullmatch(shot_id):
        raise GuardrailError("invalid screenshot ID")
    matches = [shot for shot in screenshot_manifest["screenshots"] if shot.get("id") == shot_id]
    if len(matches) != 1:
        raise GuardrailError(f"screenshot ID is not in the plan: {shot_id}")
    return matches[0]


def _validate_png(value: bytes) -> tuple[int, int]:
    if len(value) > MAX_SCREENSHOT_BYTES:
        raise GuardrailError("screenshot PNG exceeds the 10 MiB local limit")
    if not value.startswith(PNG_SIGNATURE):
        raise GuardrailError("screenshot is not a PNG")
    position = len(PNG_SIGNATURE)
    saw_ihdr = False
    saw_iend = False
    width = height = 0
    while position < len(value):
        if position + 12 > len(value):
            raise GuardrailError("screenshot PNG is truncated")
        length = int.from_bytes(value[position:position + 4], "big")
        chunk_type = value[position + 4:position + 8]
        chunk_end = position + 12 + length
        if chunk_end > len(value):
            raise GuardrailError("screenshot PNG contains a truncated chunk")
        payload = value[position + 8:position + 8 + length]
        expected_crc = int.from_bytes(value[position + 8 + length:chunk_end], "big")
        if zlib.crc32(chunk_type + payload) & 0xFFFFFFFF != expected_crc:
            raise GuardrailError("screenshot PNG contains an invalid checksum")
        if not saw_ihdr:
            if chunk_type != b"IHDR" or length != 13:
                raise GuardrailError("screenshot PNG must start with a valid IHDR chunk")
            saw_ihdr = True
            width = int.from_bytes(payload[0:4], "big")
            height = int.from_bytes(payload[4:8], "big")
            if (
                width < 1 or height < 1
                or width > SCREENSHOT_VIEWPORT["width"]
                or height > SCREENSHOT_VIEWPORT["height"]
            ):
                raise GuardrailError("screenshot dimensions must fit within the 1440x900 viewport")
            if payload[10] != 0 or payload[11] != 0 or payload[12] not in {0, 1}:
                raise GuardrailError("screenshot PNG uses unsupported compression, filtering, or interlace")
        if chunk_type == b"IEND":
            if length != 0 or chunk_end != len(value):
                raise GuardrailError("screenshot PNG has an invalid IEND or trailing data")
            saw_iend = True
            break
        position = chunk_end
    if not saw_ihdr or not saw_iend:
        raise GuardrailError("screenshot PNG is incomplete")
    return width, height


def _contains_sensitive_capture_key(value: Any) -> bool:
    forbidden = {
        "cookie", "cookies", "authorization", "authentication", "auth",
        "password", "token", "storage_state", "local_storage", "session_storage",
    }
    if isinstance(value, dict):
        return any(
            str(key).lower() in forbidden or _contains_sensitive_capture_key(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_sensitive_capture_key(item) for item in value)
    return False


def validate_capture_metadata(
    value: Mapping[str, Any], plan: Mapping[str, Any], shot: Mapping[str, Any]
) -> dict[str, Any]:
    fields = {
        "origin", "path", "workspace_sentinel", "sentinel_visible", "locale",
        "theme", "viewport", "expected_ui_labels_visible", "unexpected_sensitive_data",
        "durable_mutations", "browser_plugin", "clip",
    }
    if set(value) != fields or _contains_sensitive_capture_key(value):
        raise GuardrailError("capture metadata contains unsupported or authentication-related fields")
    origin = _validate_origin(value.get("origin"))
    if origin not in plan["allowed_origins"]:
        raise GuardrailError("capture origin is not allowlisted by the screenshot plan")
    path = _clean_string(value.get("path"), "capture path")
    parsed_path = urllib.parse.urlsplit(path)
    if (
        not path.startswith("/")
        or parsed_path.scheme
        or parsed_path.netloc
        or parsed_path.query
        or parsed_path.fragment
    ):
        raise GuardrailError("capture path must be an origin-relative path without a query or fragment")
    if value.get("workspace_sentinel") != plan["workspace_sentinel"] or value.get("sentinel_visible") is not True:
        raise GuardrailError("the visible demo-workspace sentinel was not confirmed")
    if value.get("locale") != "en" or value.get("theme") != "light":
        raise GuardrailError("screenshots must use English and the light theme")
    if value.get("viewport") != SCREENSHOT_VIEWPORT:
        raise GuardrailError("screenshots must use a 1440x900 viewport")
    visible = value.get("expected_ui_labels_visible")
    if not isinstance(visible, list) or any(not isinstance(label, str) for label in visible):
        raise GuardrailError("expected_ui_labels_visible must be a string list")
    missing = [label for label in shot["expected_ui_labels"] if label not in visible]
    if missing:
        raise GuardrailError(f"expected UI labels are not visible: {', '.join(missing)}")
    if value.get("unexpected_sensitive_data") is not False:
        raise GuardrailError("unexpected personal or customer data blocks capture; stop without redacting")
    if value.get("durable_mutations") != []:
        raise GuardrailError("durable product mutations are forbidden during screenshot capture")
    if value.get("browser_plugin") is not True:
        raise GuardrailError("capture must be performed through the Browser plugin")
    clip = value.get("clip")
    if not isinstance(clip, dict) or set(clip) != {"x", "y", "width", "height", "padding"}:
        raise GuardrailError("capture clip must include x, y, width, height, and padding")
    if any(isinstance(clip[key], bool) or not isinstance(clip[key], int) for key in clip):
        raise GuardrailError("capture clip values must be integers")
    if clip["padding"] != 16:
        raise GuardrailError("capture clip padding must be exactly 16 pixels")
    if (
        clip["x"] < 0 or clip["y"] < 0 or clip["width"] < 1 or clip["height"] < 1
        or clip["x"] + clip["width"] > SCREENSHOT_VIEWPORT["width"]
        or clip["y"] + clip["height"] > SCREENSHOT_VIEWPORT["height"]
    ):
        raise GuardrailError("capture clip must fit within the 1440x900 viewport")
    return {
        "origin": origin,
        "path": path,
        "workspace_sentinel": plan["workspace_sentinel"],
        "sentinel_visible": True,
        "locale": "en",
        "theme": "light",
        "viewport": dict(SCREENSHOT_VIEWPORT),
        "expected_ui_labels_visible": list(visible),
        "unexpected_sensitive_data": False,
        "durable_mutations": [],
        "browser_plugin": True,
        "clip": dict(clip),
    }


def _required_captured(screenshot_manifest: Mapping[str, Any]) -> None:
    missing = [
        shot["id"] for shot in screenshot_manifest["screenshots"]
        if shot["status"] == "required" and shot["state"] not in {
            "captured", "approved", "manual_upload_pending", "reconciled"
        }
    ]
    if missing:
        raise GuardrailError(f"required screenshots are not captured: {', '.join(missing)}")


def _remove_optional_placeholder(body: str, shot: Mapping[str, Any]) -> str:
    placeholder = (
        f"[Screenshot: {shot['id']} | {shot['placeholder_description']}]"
    )
    escaped = html_lib.escape(placeholder)
    patterns = (
        f"<p><em>{escaped}</em></p>",
        f'<p class="no-margin"><em>{escaped}</em></p>',
        f'<p class="no-margin"><i>{escaped}</i></p>',
    )
    matches = sum(body.count(pattern) for pattern in patterns)
    if matches != 1:
        raise GuardrailError(
            f"could not safely omit uncaptured optional placeholder {shot['id']}"
        )
    for pattern in patterns:
        if pattern in body:
            return body.replace(pattern, "", 1)
    raise AssertionError("optional screenshot placeholder count was inconsistent")


def _screenshot_tasks(screenshot_manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    review = screenshot_manifest.get("review") or {}
    accessible_files = review.get("accessible_files") or {}
    return [
        {
            "id": shot["id"],
            "placement": shot["placement"],
            "png_file": accessible_files.get(shot["id"]),
            "alt_text": shot["alt_text"],
            "status": shot["status"],
            "sha256": shot.get("sha256"),
            "width": shot.get("width"),
            "height": shot.get("height"),
        }
        for shot in screenshot_manifest["screenshots"]
        if shot["state"] in {"approved", "manual_upload_pending", "reconciled"}
    ]


def _assert_screenshot_bundle_approved(
    store: Path, slug: str, body: str
) -> dict[str, Any] | None:
    screenshot_manifest = load_screenshot_manifest(store, slug, required=False)
    placeholders = screenshot_placeholders(body)
    if screenshot_manifest is None:
        if placeholders:
            raise GuardrailError("structured screenshot placeholders require init-screenshots")
        return None
    if screenshot_manifest["state"] == "reconciled" and not placeholders:
        return None
    if screenshot_manifest["article_body_sha256"] != sha256_text(body):
        raise GuardrailError("article body changed after screenshot planning; rerun init-screenshots")
    if screenshot_manifest["state"] == "manual_upload_pending":
        raise GuardrailError(
            "manual screenshot upload is pending; reconcile the Intercom editor before another write"
        )
    if screenshot_manifest["state"] != "approved" or not screenshot_manifest.get("approval"):
        raise GuardrailError("screenshots must be locally reviewed and approved before staging")
    _verify_screenshot_review(screenshot_manifest)
    return screenshot_manifest


def init_screenshots(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    plan = _load_screenshot_plan_file(args.plan)
    with store_lock(store):
        manifest = load_manifest(store)
        record, body, _ = validate_local(store, args.slug, manifest)
        placeholders = screenshot_placeholders(body)
        placeholder_ids = [shot_id for shot_id, _ in placeholders]
        plan_ids = [shot["id"] for shot in plan["screenshots"]]
        if len(placeholder_ids) != len(set(placeholder_ids)):
            raise GuardrailError("article contains duplicate screenshot placeholder IDs")
        if placeholder_ids != plan_ids:
            raise GuardrailError(
                "screenshot plan IDs must exactly match article placeholders in article order"
            )
        timestamp = utc_now()
        value = {
            "schema_version": SCREENSHOT_SCHEMA_VERSION,
            "slug": args.slug,
            "title": record["title"],
            "state": "planned",
            "article_body_sha256": sha256_text(body),
            "plan": {
                "allowed_origins": plan["allowed_origins"],
                "workspace_sentinel": plan["workspace_sentinel"],
                "locale": "en",
                "theme": "light",
                "viewport": dict(SCREENSHOT_VIEWPORT),
            },
            "screenshots": [
                {**shot, "placeholder_description": placeholders[index][1], "state": "planned"}
                for index, shot in enumerate(plan["screenshots"])
            ],
            "review": None,
            "approval": None,
            "staged_baseline": None,
            "reconciliation": None,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        atomic_write_json(screenshot_manifest_path(store, args.slug), value)
        record["screenshots"] = {"state": "planned", "manifest": f"{SCREENSHOT_DIR}/{args.slug}/manifest.json"}
        atomic_write_json(store / "manifest.json", manifest)
    return {
        "slug": args.slug,
        "state": "planned",
        "screenshot_manifest": str(screenshot_manifest_path(store, args.slug)),
        "screenshot_ids": plan_ids,
    }


def register_screenshot(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    source = _resolve_safe_input(args.input, "screenshot PNG")
    metadata_path = _resolve_safe_input(args.capture_metadata, "capture metadata")
    image_bytes = source.read_bytes()
    width, height = _validate_png(image_bytes)
    metadata_raw = load_json(metadata_path, "capture metadata")
    with store_lock(store):
        manifest = load_manifest(store)
        record, body, _ = validate_local(store, args.slug, manifest)
        screenshot_manifest = load_screenshot_manifest(store, args.slug)
        assert screenshot_manifest is not None
        if screenshot_manifest["article_body_sha256"] != sha256_text(body):
            raise GuardrailError("article body changed after screenshot planning; rerun init-screenshots")
        shot = _shot_by_id(screenshot_manifest, args.shot_id)
        if shot["id"] not in {item[0] for item in screenshot_placeholders(body)}:
            raise GuardrailError(
                f"{shot['id']} no longer has an article placeholder; rerun init-screenshots"
            )
        metadata = validate_capture_metadata(metadata_raw, screenshot_manifest["plan"], shot)
        if (width, height) != (
            metadata["clip"]["width"], metadata["clip"]["height"]
        ):
            raise GuardrailError("screenshot PNG dimensions do not match the declared capture clip")
        digest = hashlib.sha256(image_bytes).hexdigest()
        canonical = screenshot_manifest_path(store, args.slug).parent / f"{shot['id']}.png"
        atomic_write_bytes(canonical, image_bytes)
        shot.update({
            "state": "captured",
            "file": f"{shot['id']}.png",
            "sha256": digest,
            "width": width,
            "height": height,
            "capture": metadata,
            "captured_at": utc_now(),
        })
        for item in screenshot_manifest["screenshots"]:
            if item["id"] != shot["id"] and item["state"] in {
                "approved", "manual_upload_pending", "reconciled"
            }:
                item["state"] = "captured"
        screenshot_manifest.update(
            state="captured",
            review=None,
            approval=None,
            staged_baseline=None,
            reconciliation=None,
            updated_at=utc_now(),
        )
        record["screenshots"] = {
            "state": "captured", "manifest": f"{SCREENSHOT_DIR}/{args.slug}/manifest.json"
        }
        atomic_write_json(screenshot_manifest_path(store, args.slug), screenshot_manifest)
        atomic_write_json(store / "manifest.json", manifest)
    return {
        "slug": args.slug,
        "id": args.shot_id,
        "state": "captured",
        "canonical_file": str(canonical),
        "sha256": digest,
        "width": width,
        "height": height,
        "approval_invalidated": True,
    }


def _gallery_html(
    title: str, shots: Sequence[Mapping[str, Any]], filenames: Mapping[str, str]
) -> str:
    cards: list[str] = []
    for shot in shots:
        if shot.get("state") not in {"captured", "approved", "manual_upload_pending", "reconciled"}:
            continue
        filename = filenames[shot["id"]]
        capture = shot.get("capture") or {}
        labels = ", ".join(shot["expected_ui_labels"])
        cards.append(
            "<article>"
            f"<h2>{html_lib.escape(shot['id'])} · {html_lib.escape(shot['placement'])}</h2>"
            f'<a href="{html_lib.escape(filename, quote=True)}">'
            f'<img src="{html_lib.escape(filename, quote=True)}" alt="{html_lib.escape(shot["alt_text"], quote=True)}"></a>'
            f"<p><strong>Capture goal:</strong> {html_lib.escape(shot['capture_goal'])}</p>"
            f"<p><strong>Expected UI labels:</strong> {html_lib.escape(labels)}</p>"
            f"<p><strong>Framing:</strong> {html_lib.escape(shot['framing'])}</p>"
            f"<p><strong>Setup notes:</strong> {html_lib.escape(shot['setup_notes'] or 'None')}</p>"
            f"<p><strong>Capture origin:</strong> {html_lib.escape(str(capture.get('origin') or ''))}</p>"
            f"<p><strong>Demo sentinel:</strong> {html_lib.escape(str(capture.get('workspace_sentinel') or ''))}</p>"
            f"<p><strong>Dimensions:</strong> {shot.get('width')}×{shot.get('height')} PNG</p>"
            f"<p><strong>Alt text:</strong> {html_lib.escape(shot['alt_text'])}</p>"
            f"<p><strong>Required:</strong> {html_lib.escape(shot['status'])}</p>"
            f"<p><strong>SHA-256:</strong> <code>{shot['sha256']}</code></p>"
            "</article>"
        )
    return (
        "<!doctype html><html lang=\"en\"><meta charset=\"utf-8\">"
        f"<title>{html_lib.escape(title)} screenshot review</title>"
        "<style>body{font:16px system-ui;max-width:1180px;margin:40px auto;padding:0 24px;"
        "color:#202124;background:#fff}article{border:1px solid #ddd;border-radius:12px;"
        "padding:20px;margin:24px 0}img{display:block;max-width:100%;height:auto;border:1px solid #eee;"
        "margin:12px 0}code{overflow-wrap:anywhere}</style>"
        f"<h1>{html_lib.escape(title)} screenshot review</h1>"
        "<p>Review framing, visible labels, synthetic demo data, placement, and alt text.</p>"
        + "".join(cards) + "</html>\n"
    )


def review_screenshots(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    review_root = resolve_review_copy_dir(args.review_copy_dir)
    assert review_root is not None
    if review_root.name != "intercom-article-screenshots" or ".context" not in review_root.parts:
        raise GuardrailError(
            "screenshot review copies must use <active-workspace>/.context/intercom-article-screenshots"
        )
    with store_lock(store):
        manifest = load_manifest(store)
        _, body, _ = validate_local(store, args.slug, manifest)
        screenshot_manifest = load_screenshot_manifest(store, args.slug)
        assert screenshot_manifest is not None
        if screenshot_manifest["article_body_sha256"] != sha256_text(body):
            raise GuardrailError("article body changed after screenshot planning; rerun init-screenshots")
        _required_captured(screenshot_manifest)
        canonical_dir = screenshot_manifest_path(store, args.slug).parent
        accessible_dir = review_root / validate_slug(args.slug)
        accessible_files: dict[str, str] = {}
        canonical_names: dict[str, str] = {}
        accessible_names: dict[str, str] = {}
        image_hashes: dict[str, str] = {}
        for shot in screenshot_manifest["screenshots"]:
            if shot["state"] not in {"captured", "approved", "manual_upload_pending", "reconciled"}:
                continue
            source = canonical_dir / str(shot.get("file") or "")
            image_bytes = source.read_bytes()
            _validate_png(image_bytes)
            digest = hashlib.sha256(image_bytes).hexdigest()
            if digest != shot.get("sha256"):
                raise GuardrailError(f"canonical screenshot changed: {shot['id']}")
            accessible_name = f"{shot['id']}-{digest[:12]}.png"
            atomic_write_bytes(accessible_dir / accessible_name, image_bytes, mode=0o644)
            accessible_files[shot["id"]] = str(accessible_dir / accessible_name)
            canonical_names[shot["id"]] = source.name
            accessible_names[shot["id"]] = accessible_name
            image_hashes[shot["id"]] = digest
        canonical_gallery = canonical_dir / "review.html"
        accessible_gallery = accessible_dir / "index.html"
        canonical_html = _gallery_html(
            screenshot_manifest["title"], screenshot_manifest["screenshots"], canonical_names
        )
        accessible_html = _gallery_html(
            screenshot_manifest["title"], screenshot_manifest["screenshots"], accessible_names
        )
        atomic_write_text(canonical_gallery, canonical_html, mode=0o644)
        atomic_write_text(accessible_gallery, accessible_html, mode=0o644)
        review = {
            "created_at": utc_now(),
            "image_hashes": image_hashes,
            "canonical_gallery": str(canonical_gallery),
            "canonical_gallery_sha256": sha256_text(canonical_html),
            "accessible_gallery": str(accessible_gallery),
            "accessible_gallery_sha256": sha256_text(accessible_html),
            "accessible_files": accessible_files,
        }
        screenshot_manifest.update(review=review, approval=None, updated_at=utc_now())
        atomic_write_json(screenshot_manifest_path(store, args.slug), screenshot_manifest)
    return {
        "slug": args.slug,
        "state": screenshot_manifest["state"],
        "review_gallery": str(accessible_gallery),
        "ordered_png_files": [task["png_file"] for task in _screenshot_tasks_for_review(screenshot_manifest)],
        "screenshots": _screenshot_tasks_for_review(screenshot_manifest),
    }


def _screenshot_tasks_for_review(screenshot_manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    review = screenshot_manifest.get("review") or {}
    files = review.get("accessible_files") or {}
    return [
        {
            "id": shot["id"],
            "placement": shot["placement"],
            "png_file": files.get(shot["id"]),
            "alt_text": shot["alt_text"],
            "status": shot["status"],
            "sha256": shot.get("sha256"),
            "width": shot.get("width"),
            "height": shot.get("height"),
        }
        for shot in screenshot_manifest["screenshots"]
        if shot.get("sha256")
    ]


def _verify_screenshot_review(screenshot_manifest: Mapping[str, Any]) -> None:
    review = screenshot_manifest.get("review")
    if not isinstance(review, dict):
        raise GuardrailError("screenshot review is missing; rerun review-screenshots")
    try:
        canonical_gallery = Path(review["canonical_gallery"])
        accessible_gallery = Path(review["accessible_gallery"])
        if sha256_text(canonical_gallery.read_text(encoding="utf-8")) != review["canonical_gallery_sha256"]:
            raise GuardrailError("canonical screenshot review gallery changed")
        if sha256_text(accessible_gallery.read_text(encoding="utf-8")) != review["accessible_gallery_sha256"]:
            raise GuardrailError("workspace screenshot review gallery changed")
        for shot_id, expected in review["image_hashes"].items():
            shot = _shot_by_id(screenshot_manifest, shot_id)
            canonical_file = Path(review["canonical_gallery"]).parent / shot["file"]
            accessible_file = Path(review["accessible_files"][shot_id])
            if hashlib.sha256(canonical_file.read_bytes()).hexdigest() != expected:
                raise GuardrailError(f"canonical screenshot changed: {shot_id}")
            if hashlib.sha256(accessible_file.read_bytes()).hexdigest() != expected:
                raise GuardrailError(f"workspace screenshot copy changed: {shot_id}")
    except (FileNotFoundError, KeyError, TypeError) as exc:
        raise GuardrailError("screenshot review artifacts are missing or incomplete") from exc


def approve_screenshots(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    if not args.confirm_screenshot_approval:
        raise GuardrailError(
            "approve-screenshots requires --confirm-screenshot-approval after local visual review"
        )
    store = resolve_store(args.store, environ)
    with store_lock(store):
        manifest = load_manifest(store)
        record, body, path = validate_local(store, args.slug, manifest)
        screenshot_manifest = load_screenshot_manifest(store, args.slug)
        assert screenshot_manifest is not None
        if screenshot_manifest["article_body_sha256"] != sha256_text(body):
            raise GuardrailError("article body changed after screenshot planning; rerun init-screenshots")
        _required_captured(screenshot_manifest)
        _verify_screenshot_review(screenshot_manifest)
        omitted_optional_ids: list[str] = []
        for shot in screenshot_manifest["screenshots"]:
            if shot["status"] == "optional" and not shot.get("sha256"):
                body = _remove_optional_placeholder(body, shot)
                omitted_optional_ids.append(shot["id"])
        if omitted_optional_ids:
            atomic_write_text(path, body)
            record.update(
                local_hash=sha256_text(body),
                verified=False,
                comparison_review=None,
                updated_at=utc_now(),
            )
            screenshot_manifest["article_body_sha256"] = sha256_text(body)
        bundle = [
            {"id": shot["id"], "sha256": shot.get("sha256"), "alt_text": shot["alt_text"]}
            for shot in screenshot_manifest["screenshots"]
            if shot.get("sha256")
        ]
        approval = {
            "approved_at": utc_now(),
            "bundle_sha256": stable_hash(bundle),
            "article_body_sha256": sha256_text(body),
            "omitted_optional_ids": omitted_optional_ids,
        }
        for shot in screenshot_manifest["screenshots"]:
            if shot.get("sha256"):
                shot["state"] = "approved"
        screenshot_manifest.update(state="approved", approval=approval, updated_at=utc_now())
        record["screenshots"] = {
            "state": "approved", "manifest": f"{SCREENSHOT_DIR}/{args.slug}/manifest.json"
        }
        atomic_write_json(screenshot_manifest_path(store, args.slug), screenshot_manifest)
        atomic_write_json(store / "manifest.json", manifest)
    return {
        "slug": args.slug,
        "state": "approved",
        "bundle_sha256": approval["bundle_sha256"],
        "review_gallery": screenshot_manifest["review"]["accessible_gallery"],
        "screenshots": _screenshot_tasks(screenshot_manifest),
        "omitted_optional_ids": omitted_optional_ids,
    }


def _positive_int(value: Any, field: str, *, allow_zero: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise GuardrailError(f"{field} must be an integer")
    minimum = 0 if allow_zero else 1
    if value < minimum:
        raise GuardrailError(f"{field} must be at least {minimum}")
    return value


def _catalog_timestamp(value: Any, field: str) -> int | None:
    if value is None:
        return None
    return _positive_int(value, field, allow_zero=True)


def _catalog_optional_id(value: Any, field: str) -> int | None:
    if value is None:
        return None
    return normalize_id(value, field)


def _catalog_url(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise GuardrailError("catalog article URL must be a string or null")
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise GuardrailError("catalog article URL must be an absolute HTTPS URL")
    _safe_url(value)
    return value


def _normalize_catalog_article(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise GuardrailError("every catalog article must be a JSON object")
    extra = set(value) - CATALOG_ARTICLE_FIELDS
    if extra:
        raise GuardrailError(f"catalog article contains unsupported fields: {', '.join(sorted(extra))}")
    if "body" in value or "body_markdown" in value:
        raise GuardrailError("catalog snapshots must never contain article bodies")
    article_id = str(normalize_id(value.get("id"), "catalog article ID"))
    content_id = str(normalize_id(value.get("content_id"), "catalog content ID"))
    title = value.get("title")
    if not isinstance(title, str) or not title.strip():
        raise GuardrailError("catalog article title must be a non-empty string")
    description = value.get("description") or ""
    if not isinstance(description, str):
        raise GuardrailError("catalog article description must be a string or null")
    state = value.get("state")
    if state not in {"draft", "published"}:
        raise GuardrailError("catalog article state must be 'draft' or 'published'")
    parent_id = _catalog_optional_id(value.get("parent_id"), "catalog parent ID")
    parent_type = value.get("parent_type")
    if parent_type not in {None, "collection", "section"}:
        raise GuardrailError("catalog parent_type must be 'collection', 'section', or null")
    if (parent_id is None) != (parent_type is None):
        raise GuardrailError("catalog parent_id and parent_type must be provided together")
    return {
        "id": article_id,
        "content_id": content_id,
        "title": title.strip(),
        "description": description.strip(),
        "state": state,
        "parent_id": parent_id,
        "parent_type": parent_type,
        "author_id": _catalog_optional_id(value.get("author_id"), "catalog author ID"),
        "created_at": _catalog_timestamp(value.get("created_at"), "catalog created_at"),
        "updated_at": _catalog_timestamp(value.get("updated_at"), "catalog updated_at"),
        "url": _catalog_url(value.get("url")),
    }


def validate_catalog_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    extra = set(snapshot) - CATALOG_SNAPSHOT_FIELDS
    missing = CATALOG_SNAPSHOT_FIELDS - set(snapshot)
    if extra or missing:
        raise GuardrailError(
            f"catalog snapshot fields are invalid (extra={sorted(extra)}, missing={sorted(missing)})"
        )
    if snapshot.get("source") != CURRENT_STATE_SOURCE:
        raise GuardrailError(f"catalog source must be exactly {CURRENT_STATE_SOURCE!r}")
    if snapshot.get("complete") is not True:
        raise GuardrailError("catalog snapshot must be explicitly complete")
    fetched_at = snapshot.get("fetched_at")
    if not isinstance(fetched_at, str):
        raise GuardrailError("catalog fetched_at must be an ISO-8601 timestamp")
    try:
        parsed = dt.datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise GuardrailError("catalog fetched_at must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise GuardrailError("catalog fetched_at must include a timezone")

    total_pages = _positive_int(snapshot.get("total_pages"), "catalog total_pages")
    pages_fetched = snapshot.get("pages_fetched")
    if not isinstance(pages_fetched, list) or any(isinstance(item, bool) or not isinstance(item, int) for item in pages_fetched):
        raise GuardrailError("catalog pages_fetched must be an integer list")
    if pages_fetched != list(range(1, total_pages + 1)):
        raise GuardrailError("catalog pages_fetched must contain every page exactly once in order")
    articles_raw = snapshot.get("articles")
    if not isinstance(articles_raw, list):
        raise GuardrailError("catalog articles must be a list")
    total_count = _positive_int(snapshot.get("total_count"), "catalog total_count", allow_zero=True)
    if total_count != len(articles_raw):
        raise GuardrailError("catalog total_count does not match the supplied articles")
    articles = [_normalize_catalog_article(article) for article in articles_raw]
    ids = [article["id"] for article in articles]
    if len(ids) != len(set(ids)):
        raise GuardrailError("catalog snapshot contains duplicate article IDs")
    return {
        "source": CURRENT_STATE_SOURCE,
        "fetched_at": parsed.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "complete": True,
        "total_pages": total_pages,
        "pages_fetched": list(pages_fetched),
        "total_count": total_count,
        "articles": sorted(articles, key=lambda article: (article["title"].casefold(), article["id"])),
    }


def validate_mcp_article_snapshot(
    snapshot: Mapping[str, Any], config: Mapping[str, Any]
) -> dict[str, Any]:
    extra = set(snapshot) - MCP_ARTICLE_SNAPSHOT_FIELDS
    missing = MCP_ARTICLE_SNAPSHOT_FIELDS - set(snapshot)
    if extra or missing:
        raise GuardrailError(
            f"MCP article snapshot fields are invalid (extra={sorted(extra)}, missing={sorted(missing)})"
        )
    if snapshot.get("source") != MCP_ARTICLE_SOURCE:
        raise GuardrailError(f"MCP article source must be exactly {MCP_ARTICLE_SOURCE!r}")
    if snapshot.get("complete") is not True:
        raise GuardrailError("MCP article snapshot must be explicitly complete")
    fetched_at = snapshot.get("fetched_at")
    if not isinstance(fetched_at, str):
        raise GuardrailError("MCP article fetched_at must be an ISO-8601 timestamp")
    try:
        parsed = dt.datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise GuardrailError("MCP article fetched_at must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise GuardrailError("MCP article fetched_at must include a timezone")

    value = snapshot.get("article")
    if not isinstance(value, dict):
        raise GuardrailError("MCP article snapshot must contain one article object")
    extra = set(value) - MCP_ARTICLE_FIELDS
    missing = MCP_ARTICLE_FIELDS - set(value)
    if extra or missing:
        raise GuardrailError(
            f"MCP article fields are invalid (extra={sorted(extra)}, missing={sorted(missing)})"
        )
    article_id = str(normalize_id(value.get("id"), "MCP article ID"))
    content_id = str(normalize_id(value.get("content_id"), "MCP content ID"))
    workspace_id = str(value.get("workspace_id") or "").strip()
    if not workspace_id or workspace_id != str(config["workspace_id"]):
        raise GuardrailError("MCP article belongs to a different or unknown workspace")
    title = value.get("title")
    if not isinstance(title, str) or not title.strip():
        raise GuardrailError("MCP article title must be a non-empty string")
    description = value.get("description") or ""
    if not isinstance(description, str):
        raise GuardrailError("MCP article description must be a string or null")
    body = value.get("body")
    if not isinstance(body, str):
        raise GuardrailError("MCP article body must be a string")
    if body:
        validate_html(body)
    state = value.get("state")
    if state not in {"draft", "published"}:
        raise GuardrailError("MCP article state must be 'draft' or 'published'")
    parent_id = _catalog_optional_id(value.get("parent_id"), "MCP parent ID")
    parent_type = value.get("parent_type")
    if parent_type not in {None, "collection", "section"}:
        raise GuardrailError("MCP parent_type must be 'collection', 'section', or null")
    if (parent_id is None) != (parent_type is None):
        raise GuardrailError("MCP parent_id and parent_type must be provided together")
    return {
        "source": MCP_ARTICLE_SOURCE,
        "fetched_at": parsed.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "id": article_id,
        "content_id": content_id,
        "workspace_id": workspace_id,
        "title": title.strip(),
        "description": description.strip(),
        "body": body,
        "author_id": normalize_id(value.get("author_id"), "MCP author ID"),
        "state": state,
        "created_at": _catalog_timestamp(value.get("created_at"), "MCP created_at"),
        "updated_at": _catalog_timestamp(value.get("updated_at"), "MCP updated_at"),
        "has_unpublished_changes": None,
        "draft_updated_at": None,
        "parent_ids": [] if parent_id is None else [parent_id],
        "parent_type": parent_type,
        "default_locale": "en",
        "url": _catalog_url(value.get("url")),
    }


def _local_overlays(store: Path, manifest: Mapping[str, Any]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    by_remote_id: dict[str, dict[str, Any]] = {}
    local_only: list[dict[str, Any]] = []
    for slug in sorted(manifest.get("articles", {})):
        record = get_record(manifest, slug)
        path = article_file(store, slug)
        actual_hash = sha256_text(path.read_text(encoding="utf-8")) if path.exists() else None
        if record.get("pending_write"):
            status = "pending-write"
        elif actual_hash is None:
            status = "missing-local-file"
        elif record.get("remote_hash") is None:
            status = "local-only"
        elif actual_hash != record.get("remote_hash"):
            status = "local-changes"
        elif record.get("verified"):
            status = "synced"
        else:
            status = "prepared"
        local = {
            "slug": slug,
            "file": str(path),
            "title": str(record.get("title") or ""),
            "description": str(record.get("description") or ""),
            "draft_kind": record.get("draft_kind"),
            "status": status,
            "verified": bool(record.get("verified")),
            "pending_write": bool(record.get("pending_write")),
        }
        article_id = record.get("intercom_id")
        if article_id is None:
            local_only.append(local)
            continue
        normalized_id = str(normalize_id(article_id, "local Intercom article ID"))
        if normalized_id in by_remote_id:
            raise GuardrailError(f"multiple local articles reference Intercom article {normalized_id}")
        by_remote_id[normalized_id] = local
    return by_remote_id, local_only


def _merge_current_state(
    store: Path, manifest: Mapping[str, Any], remote_articles: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    local_by_id, local_only = _local_overlays(store, manifest)
    entries = [
        {"remote": dict(remote), "local": local_by_id.pop(str(remote["id"]), None)}
        for remote in remote_articles
    ]
    entries.extend({"remote": None, "local": local} for local in local_only)
    for missing_id, local in sorted(local_by_id.items()):
        local = dict(local)
        local["status"] = "remote-missing-from-catalog"
        entries.append({"remote": {"id": missing_id}, "local": local})
    return entries


def _markdown_cell(value: Any) -> str:
    if value is None:
        return "—"
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").strip() or "—"


def render_current_state_markdown(state: Mapping[str, Any]) -> str:
    entries = state.get("articles") if isinstance(state.get("articles"), list) else []
    published = sum(1 for entry in entries if (entry.get("remote") or {}).get("state") == "published")
    drafts = sum(1 for entry in entries if (entry.get("remote") or {}).get("state") == "draft")
    local_only = sum(1 for entry in entries if entry.get("remote") is None)
    freshness = "STALE" if state.get("stale") else "fresh"
    lines = [
        "# Current Intercom Article State",
        "",
        f"Last successful MCP refresh: {_markdown_cell(state.get('last_successful_refresh_at'))} ({freshness}).",
        f"Remote articles: {published + drafts} ({published} published, {drafts} drafts). Local-only articles: {local_only}.",
    ]
    if state.get("refresh_error"):
        lines.extend(["", f"Refresh warning: {_markdown_cell(state['refresh_error'])}"])
    lines.extend([
        "",
        "| State | Title | Remote ID | Parent | Updated | Public URL | Local status |",
        "|---|---|---:|---|---:|---|---|",
    ])
    for entry in entries:
        remote = entry.get("remote") or {}
        local = entry.get("local") or {}
        state_label = remote.get("state") or "local"
        title = remote.get("title") or local.get("title")
        parent = " / ".join(
            str(value) for value in (remote.get("parent_type"), remote.get("parent_id")) if value is not None
        ) or None
        lines.append(
            "| " + " | ".join(
                _markdown_cell(value) for value in (
                    state_label,
                    title,
                    remote.get("id"),
                    parent,
                    remote.get("updated_at"),
                    remote.get("url"),
                    local.get("status"),
                )
            ) + " |"
        )
    return "\n".join(lines) + "\n"


def _load_current_state(store: Path) -> dict[str, Any]:
    state = load_json(store / CURRENT_STATE_JSON, "current article state")
    if state.get("schema_version") != CURRENT_STATE_SCHEMA_VERSION or not isinstance(state.get("articles"), list):
        raise GuardrailError("current article state schema is unsupported")
    return state


def _write_current_state(store: Path, state: Mapping[str, Any]) -> None:
    atomic_write_json(store / CURRENT_STATE_JSON, state)
    atomic_write_text(store / CURRENT_STATE_MARKDOWN, render_current_state_markdown(state))


def _remote_articles_from_state(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    articles: list[dict[str, Any]] = []
    for entry in state.get("articles", []):
        remote = entry.get("remote") if isinstance(entry, dict) else None
        if isinstance(remote, dict) and set(CATALOG_ARTICLE_FIELDS) <= set(remote):
            articles.append({field: remote.get(field) for field in CATALOG_ARTICLE_FIELDS})
    return articles


def _refresh_current_state_if_present(store: Path, manifest: Mapping[str, Any]) -> None:
    if not (store / CURRENT_STATE_JSON).exists():
        return
    state = _load_current_state(store)
    state["articles"] = _merge_current_state(store, manifest, _remote_articles_from_state(state))
    state["rendered_at"] = utc_now()
    _write_current_state(store, state)


def import_current_state(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    snapshot = validate_catalog_snapshot(load_json(Path(args.snapshot).expanduser().resolve(), "catalog snapshot"))
    with store_lock(store):
        manifest = load_manifest(store)
        state = {
            "schema_version": CURRENT_STATE_SCHEMA_VERSION,
            "source": CURRENT_STATE_SOURCE,
            "complete": True,
            "stale": False,
            "last_successful_refresh_at": snapshot["fetched_at"],
            "last_refresh_attempt_at": utc_now(),
            "refresh_error": None,
            "total_pages": snapshot["total_pages"],
            "pages_fetched": snapshot["pages_fetched"],
            "remote_total": snapshot["total_count"],
            "articles": _merge_current_state(store, manifest, snapshot["articles"]),
            "rendered_at": utc_now(),
        }
        _write_current_state(store, state)
    return {
        "current_state_file": str(store / CURRENT_STATE_JSON),
        "overview_file": str(store / CURRENT_STATE_MARKDOWN),
        "remote_articles": snapshot["total_count"],
        "stale": False,
    }


def mark_current_state_stale(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    reason = redact(str(args.reason).strip(), environ.get(TOKEN_ENV)).replace("\n", " ")[:300]
    if not reason:
        raise GuardrailError("a stale-state reason is required")
    with store_lock(store):
        if (store / CURRENT_STATE_JSON).exists():
            state = _load_current_state(store)
            manifest = load_manifest(store)
            state["articles"] = _merge_current_state(store, manifest, _remote_articles_from_state(state))
        else:
            state = {
                "schema_version": CURRENT_STATE_SCHEMA_VERSION,
                "source": CURRENT_STATE_SOURCE,
                "complete": False,
                "last_successful_refresh_at": None,
                "articles": [],
            }
        state.update(
            stale=True,
            last_refresh_attempt_at=utc_now(),
            refresh_error=reason,
            rendered_at=utc_now(),
        )
        _write_current_state(store, state)
    return {
        "current_state_file": str(store / CURRENT_STATE_JSON),
        "overview_file": str(store / CURRENT_STATE_MARKDOWN),
        "stale": True,
        "reason": reason,
    }


def render_current_state(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    with store_lock(store):
        state = _load_current_state(store)
        manifest = load_manifest(store)
        state["articles"] = _merge_current_state(store, manifest, _remote_articles_from_state(state))
        state["rendered_at"] = utc_now()
        _write_current_state(store, state)
    return {
        "current_state_file": str(store / CURRENT_STATE_JSON),
        "overview_file": str(store / CURRENT_STATE_MARKDOWN),
        "remote_articles": state.get("remote_total", 0),
        "stale": bool(state.get("stale")),
    }


def require_fresh_current_state(store: Path) -> dict[str, Any]:
    state = _load_current_state(store)
    if state.get("source") != CURRENT_STATE_SOURCE or state.get("complete") is not True or state.get("stale") is not False:
        raise GuardrailError("a complete, fresh Intercom MCP article overview is required before a draft write")
    return state


def article_file(store: Path, slug: str) -> Path:
    validate_slug(slug)
    return store / "articles" / f"{slug}.html"


def get_record(manifest: Mapping[str, Any], slug: str) -> dict[str, Any]:
    validate_slug(slug)
    record = manifest.get("articles", {}).get(slug)
    if not isinstance(record, dict):
        raise GuardrailError(f"article is not in the manifest: {slug}")
    return record


def remote_snapshot(article: Mapping[str, Any]) -> dict[str, Any]:
    snapshot = {field: article.get(field) for field in REMOTE_COMPARE_FIELDS}
    snapshot["id"] = str(article.get("id", ""))
    snapshot["content_id"] = str(normalize_id(article.get("content_id"), "remote content ID"))
    snapshot["workspace_id"] = str(article.get("workspace_id", ""))
    snapshot["description"] = article.get("description") or ""
    snapshot["body"] = article.get("body") or ""
    snapshot["author_id"] = normalize_id(article.get("author_id"), "remote author ID")
    snapshot["parent_ids"] = normalize_id_list(article.get("parent_ids") or [])
    return snapshot


def selected_snapshot(snapshot: Mapping[str, Any], fields: Sequence[str]) -> dict[str, Any]:
    return {field: snapshot.get(field) for field in fields}


def validate_remote_article(article: Mapping[str, Any], config: Mapping[str, Any]) -> dict[str, Any]:
    if str(article.get("workspace_id")) != str(config["workspace_id"]):
        raise GuardrailError("Intercom response belongs to a different workspace")
    if not ARTICLE_ID_RE.fullmatch(str(article.get("id", ""))):
        raise GuardrailError("Intercom response has no valid article ID")
    snapshot = remote_snapshot(article)
    validate_html(snapshot["body"])
    return snapshot


def require_token(environ: Mapping[str, str]) -> str:
    token = environ.get(TOKEN_ENV, "").strip()
    if not token:
        raise GuardrailError(f"{TOKEN_ENV} is required for Intercom API access")
    return token


def build_article_payload(record: Mapping[str, Any], body: str) -> dict[str, Any]:
    payload = {
        "title": str(record["title"]),
        "description": str(record.get("description") or ""),
        "body": body,
        "author_id": normalize_id(record["author_id"], "author ID"),
        "state": "draft",
        "parent_ids": normalize_id_list(record.get("collection_ids") or []),
    }
    assert_safe_request("POST", "/articles", payload)
    return payload


def build_staged_payload(record: Mapping[str, Any], body: str) -> dict[str, Any]:
    payload = {
        "title": str(record["title"]),
        "description": str(record.get("description") or ""),
        "body": body,
        "author_id": normalize_id(record["author_id"], "author ID"),
    }
    article_id = normalize_id(record["intercom_id"], "article ID")
    assert_safe_request("PUT", f"/articles/{article_id}/draft", payload)
    return payload


def assert_safe_request(method: str, path: str, payload: Mapping[str, Any] | None) -> None:
    method = method.upper()
    if any(key in (payload or {}) for key in FORBIDDEN_PAYLOAD_KEYS):
        raise GuardrailError("payload contains a forbidden publication, scheduling, or scope field")
    if method == "GET" and payload is None and (WRITE_PATH_RE.fullmatch(path) or DRAFT_PATH_RE.fullmatch(path)):
        return
    if method == "POST" and path == "/articles" and payload is not None:
        allowed = {"title", "description", "body", "author_id", "state", "parent_ids"}
        required = {"title", "body", "author_id", "state"}
    elif method == "PUT" and WRITE_PATH_RE.fullmatch(path) and payload is not None:
        allowed = {"title", "description", "body", "author_id", "state", "parent_ids"}
        required = {"title", "body", "author_id", "state"}
    elif method == "PUT" and DRAFT_PATH_RE.fullmatch(path) and payload is not None:
        allowed = {"title", "description", "body", "author_id"}
        required = {"title", "body", "author_id"}
    else:
        raise GuardrailError(f"HTTP request is outside the draft-only allowlist: {method} {path}")
    extra = set(payload) - allowed
    missing = required - set(payload)
    if extra or missing:
        raise GuardrailError(f"unsafe payload fields (extra={sorted(extra)}, missing={sorted(missing)})")
    if "state" in payload and payload["state"] != "draft":
        raise GuardrailError("article state must be exactly 'draft'")


class IntercomClient:
    def __init__(self, api_base: str, token: str, timeout: float = 20.0):
        self.api_base = validate_api_base(api_base)
        self.token = token
        self.timeout = timeout

    def request(
        self,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
        *,
        allow_statuses: Iterable[int] = (),
    ) -> tuple[int, dict[str, Any] | None]:
        assert_safe_request(method, path, payload)
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Intercom-Version": API_VERSION,
        }
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(self.api_base + path, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                value = json.loads(raw) if raw else None
                if value is not None and not isinstance(value, dict):
                    raise ApiError(
                        "Intercom returned a non-object JSON response",
                        ambiguous=method in {"POST", "PUT"},
                    )
                return response.status, value
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            if exc.code in set(allow_statuses):
                return exc.code, None
            labels = {
                400: "request rejected", 401: "authentication failed", 403: "permission denied",
                404: "article or endpoint not found", 422: "request could not be staged",
                429: "rate limited",
            }
            label = labels.get(exc.code, "server failure" if exc.code >= 500 else "request failed")
            detail = redact(raw, self.token)
            ambiguous = method in {"POST", "PUT"} and (exc.code == 429 or exc.code >= 500)
            raise ApiError(
                f"Intercom {label} (HTTP {exc.code})" + (f": {detail}" if detail else ""),
                status=exc.code,
                ambiguous=ambiguous,
            ) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ApiError(
                f"Intercom network failure: {redact(str(exc), self.token)}",
                ambiguous=method in {"POST", "PUT"},
            ) from exc
        except json.JSONDecodeError as exc:
            raise ApiError("Intercom returned invalid JSON", ambiguous=method in {"POST", "PUT"}) from exc

    def get_article(self, article_id: Any) -> dict[str, Any]:
        article_id = normalize_id(article_id, "article ID")
        _, value = self.request("GET", f"/articles/{article_id}")
        if not isinstance(value, dict):
            raise ApiError("Intercom returned an empty article response")
        return value

    def get_draft(self, article_id: Any) -> dict[str, Any] | None:
        article_id = normalize_id(article_id, "article ID")
        status, value = self.request("GET", f"/articles/{article_id}/draft", allow_statuses={404})
        return None if status == 404 else value

    def create_article(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        _, value = self.request("POST", "/articles", payload)
        if not isinstance(value, dict):
            raise ApiError("Intercom returned an empty create response", ambiguous=True)
        return value

    def update_draft_article(self, article_id: Any, payload: Mapping[str, Any]) -> dict[str, Any]:
        article_id = normalize_id(article_id, "article ID")
        _, value = self.request("PUT", f"/articles/{article_id}", payload)
        if not isinstance(value, dict):
            raise ApiError("Intercom returned an empty update response", ambiguous=True)
        return value

    def stage_live_draft(self, article_id: Any, payload: Mapping[str, Any]) -> dict[str, Any]:
        article_id = normalize_id(article_id, "article ID")
        _, value = self.request("PUT", f"/articles/{article_id}/draft", payload)
        if not isinstance(value, dict):
            raise ApiError("Intercom returned an empty staged-draft response", ambiguous=True)
        return value


def setup_store(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    config = {
        "schema_version": SCHEMA_VERSION,
        "api_base": validate_api_base(args.api_base),
        "workspace_id": str(args.workspace_id).strip(),
        "default_author_id": normalize_id(args.default_author_id, "default author ID"),
        "default_locale": "en",
        "editor_url_template": derive_editor_url_template(args.sample_content_id, args.sample_editor_url),
        "created_at": utc_now(),
    }
    if not config["workspace_id"]:
        raise GuardrailError("workspace ID must not be empty")
    with store_lock(store):
        config_path = store / "config.json"
        manifest_path = store / "manifest.json"
        if config_path.exists() and not args.replace:
            raise GuardrailError(f"config already exists; pass --replace to replace it: {config_path}")
        store.mkdir(parents=True, exist_ok=True)
        (store / "articles").mkdir(exist_ok=True)
        if not manifest_path.exists():
            atomic_write_json(manifest_path, empty_manifest())
        atomic_write_json(config_path, config)
    return {"config_file": str(config_path), "store": str(store), "editor_url_template": config["editor_url_template"]}


def new_article(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    config = load_config(store)
    slug = validate_slug(args.slug)
    with store_lock(store):
        manifest = load_manifest(store, create=True)
        if slug in manifest["articles"]:
            raise GuardrailError(f"article already exists in manifest: {slug}")
        path = article_file(store, slug)
        if path.exists():
            raise GuardrailError(f"article file already exists: {path}")
        body = "<p>Replace this text with the article body.</p>\n"
        timestamp = utc_now()
        record = {
            "slug": slug,
            "file": f"articles/{slug}.html",
            "title": args.title.strip(),
            "description": (args.description or "").strip(),
            "collection_ids": normalize_id_list(args.collection_id or []),
            "locale": "en",
            "author_id": normalize_id(args.author_id or config["default_author_id"], "author ID"),
            "intercom_id": None,
            "draft_kind": "new",
            "baseline": None,
            "local_hash": sha256_text(body),
            "remote_hash": None,
            "verified": False,
            "pending_write": None,
            "comparison_review": None,
            "created_at": timestamp,
            "updated_at": timestamp,
            "last_pushed_at": None,
        }
        if not record["title"]:
            raise GuardrailError("title must not be empty")
        atomic_write_text(path, body)
        manifest["articles"][slug] = record
        atomic_write_json(store / "manifest.json", manifest)
        _refresh_current_state_if_present(store, manifest)
    return {"local_file": str(path), "slug": slug, "validated": False}


def _ensure_no_remote_draft(client: IntercomClient, article: Mapping[str, Any]) -> None:
    if "has_unpublished_changes" not in article or "draft_updated_at" not in article:
        raise GuardrailError("Preview draft markers are unavailable; refusing to stage a live revision")
    if article.get("has_unpublished_changes") or article.get("draft_updated_at") is not None:
        raise GuardrailError("published article already has unpublished changes")
    draft = client.get_draft(article["id"])
    if draft is not None:
        raise GuardrailError("published article already has a staged draft")


def begin_article(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    config = load_config(store)
    token = require_token(environ)
    client = IntercomClient(config["api_base"], token, timeout=args.timeout)
    article_id = normalize_id(args.article_id, "article ID")
    remote = client.get_article(article_id)
    snapshot = validate_remote_article(remote, config)
    if snapshot["state"] not in {"draft", "published"}:
        raise GuardrailError(f"unsupported remote article state: {snapshot['state']!r}")
    if snapshot["state"] == "draft":
        if remote.get("has_unpublished_changes") not in {None, False}:
            raise GuardrailError("never-published article has an unexpected unpublished-change marker")
        draft_kind = "never_published"
    else:
        _ensure_no_remote_draft(client, remote)
        draft_kind = "published_revision"

    slug = validate_slug(args.slug) if args.slug else slugify(snapshot["title"])
    path = article_file(store, slug)
    body = snapshot["body"]
    timestamp = utc_now()
    record = {
        "slug": slug,
        "file": f"articles/{slug}.html",
        "title": snapshot["title"],
        "description": snapshot["description"],
        "collection_ids": snapshot["parent_ids"],
        "locale": "en",
        "author_id": snapshot["author_id"],
        "intercom_id": str(article_id),
        "draft_kind": draft_kind,
        "baseline": snapshot,
        "local_hash": sha256_text(body),
        "remote_hash": sha256_text(body),
        "verified": True,
        "pending_write": None,
        "comparison_review": None,
        "created_at": timestamp,
        "updated_at": timestamp,
        "last_pushed_at": None,
    }
    with store_lock(store):
        manifest = load_manifest(store, create=True)
        if slug in manifest["articles"] or path.exists():
            raise GuardrailError(f"local article already exists; choose a new slug: {slug}")
        atomic_write_text(path, body)
        manifest["articles"][slug] = record
        atomic_write_json(store / "manifest.json", manifest)
        _refresh_current_state_if_present(store, manifest)
    return {"local_file": str(path), "article_id": str(article_id), "draft_kind": draft_kind}


def _load_mcp_article_file(path_value: str, config: Mapping[str, Any]) -> dict[str, Any]:
    path = Path(path_value).expanduser().resolve()
    return validate_mcp_article_snapshot(load_json(path, "MCP article snapshot"), config)


def begin_mcp_article(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    config = load_config(store)
    snapshot = _load_mcp_article_file(args.snapshot, config)
    if snapshot["state"] != "draft":
        raise GuardrailError(
            "Intercom MCP cannot safely stage a revision to a published article; prepare it locally only"
        )
    slug = validate_slug(args.slug) if args.slug else slugify(snapshot["title"])
    path = article_file(store, slug)
    body = snapshot["body"]
    timestamp = utc_now()
    record = {
        "slug": slug,
        "file": f"articles/{slug}.html",
        "title": snapshot["title"],
        "description": snapshot["description"],
        "collection_ids": snapshot["parent_ids"],
        "locale": "en",
        "author_id": snapshot["author_id"],
        "intercom_id": snapshot["id"],
        "draft_kind": "never_published",
        "baseline": snapshot,
        "local_hash": sha256_text(body),
        "remote_hash": sha256_text(body),
        "verified": True,
        "pending_write": None,
        "comparison_review": None,
        "created_at": timestamp,
        "updated_at": timestamp,
        "last_pushed_at": None,
    }
    with store_lock(store):
        manifest = load_manifest(store, create=True)
        if slug in manifest["articles"] or path.exists():
            raise GuardrailError(f"local article already exists; choose a new slug: {slug}")
        atomic_write_text(path, body)
        manifest["articles"][slug] = record
        atomic_write_json(store / "manifest.json", manifest)
        _refresh_current_state_if_present(store, manifest)
    return {"local_file": str(path), "article_id": snapshot["id"], "draft_kind": "never_published"}


def _mcp_write_arguments(record: Mapping[str, Any], body: str) -> dict[str, Any]:
    collection_ids = normalize_id_list(record.get("collection_ids") or [])
    if len(collection_ids) > 1:
        raise GuardrailError("Intercom MCP supports at most one article parent")
    arguments: dict[str, Any] = {
        "title": str(record["title"]),
        "description": str(record.get("description") or ""),
        "body": body,
        "state": "draft",
    }
    if collection_ids:
        baseline = record.get("baseline") or {}
        parent_type = baseline.get("parent_type") if baseline.get("parent_ids") == collection_ids else "collection"
        arguments.update(parent_id=collection_ids[0], parent_type=parent_type or "collection")
    return arguments


def prepare_mcp_write(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    if not args.confirm_draft_write:
        raise GuardrailError(
            "prepare-mcp-write requires --confirm-draft-write after explicit user authorization"
        )
    store = resolve_store(args.store, environ)
    config = load_config(store)
    with store_lock(store):
        manifest = load_manifest(store)
        record, body, path = validate_local(store, args.slug, manifest)
        if record.get("pending_write"):
            raise GuardrailError("a pending or ambiguous prior write blocks further writes; inspect status")
        screenshot_manifest = _assert_screenshot_bundle_approved(store, args.slug, body)
        require_fresh_current_state(store)
        kind = record.get("draft_kind")
        arguments = _mcp_write_arguments(record, body)
        comparison_file: Path | None = None
        if kind == "new":
            operation = "create_article"
            article_id = None
        elif kind == "never_published":
            if not args.snapshot:
                raise GuardrailError("a fresh get_article MCP snapshot is required before updating a draft")
            current = _load_mcp_article_file(args.snapshot, config)
            article_id = str(normalize_id(record.get("intercom_id"), "article ID"))
            if current["id"] != article_id:
                raise GuardrailError("MCP baseline snapshot is for a different article")
            if current["state"] != "draft":
                raise GuardrailError("the target article is no longer a never-published draft")
            baseline = record.get("baseline")
            if not isinstance(baseline, dict):
                raise GuardrailError("missing MCP begin baseline")
            _assert_baseline_unchanged(
                current, baseline, REMOTE_COMPARE_FIELDS, "remote article changed after begin-mcp"
            )
            if current.get("parent_type") != baseline.get("parent_type"):
                raise GuardrailError("remote article parent changed after begin-mcp")
            if not record.get("collection_ids") and baseline.get("parent_ids"):
                raise GuardrailError("Intercom MCP cannot remove an article parent")
            comparison_file = _require_current_comparison(store, args.slug, record, body, path)
            arguments["id"] = article_id
            operation = "update_article"
        elif kind == "published_revision":
            raise GuardrailError(
                "Intercom MCP has no safe staged-revision operation for published articles"
            )
        else:
            raise GuardrailError(f"unsupported draft kind: {kind!r}")

        record["pending_write"] = {
            "phase": "prepared",
            "provider": "intercom-mcp",
            "operation": operation,
            "request_hash": stable_hash(arguments),
            "prepared_at": utc_now(),
            "article_id": article_id,
        }
        if screenshot_manifest:
            record["pending_write"]["screenshot_bundle_sha256"] = (
                screenshot_manifest["approval"]["bundle_sha256"]
            )
        atomic_write_json(store / "manifest.json", manifest)
    result = {
        "local_file": str(path),
        "operation": operation,
        "arguments": arguments,
        "article_id": article_id,
        "draft_kind": kind,
        "comparison_file": str(comparison_file) if comparison_file else None,
    }
    if screenshot_manifest:
        result.update(
            screenshots=_screenshot_tasks(screenshot_manifest),
            screenshot_review_gallery=screenshot_manifest["review"]["accessible_gallery"],
        )
    return result


def verify_mcp_write(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    config = load_config(store)
    snapshot = _load_mcp_article_file(args.snapshot, config)
    with store_lock(store):
        manifest = load_manifest(store)
        record, body, path = validate_local(store, args.slug, manifest)
        pending = record.get("pending_write")
        if not isinstance(pending, dict) or pending.get("provider") != "intercom-mcp":
            raise GuardrailError("no prepared Intercom MCP write is awaiting verification")
        try:
            if snapshot["state"] != "draft":
                raise GuardrailError("article did not read back as a draft")
            expected_id = pending.get("article_id")
            if expected_id is not None and snapshot["id"] != str(expected_id):
                raise GuardrailError("read-back returned a different article ID")
            expected = _mcp_write_arguments(record, body)
            if pending.get("operation") == "update_article":
                expected["id"] = str(record["intercom_id"])
            if stable_hash(expected) != pending.get("request_hash"):
                raise GuardrailError("local article changed after the MCP write was prepared")
            screenshot_manifest = load_screenshot_manifest(store, args.slug, required=False)
            if screenshot_manifest:
                if screenshot_manifest.get("state") != "approved":
                    raise GuardrailError("screenshot approval changed after the MCP write was prepared")
                if (
                    screenshot_manifest.get("approval", {}).get("bundle_sha256")
                    != pending.get("screenshot_bundle_sha256")
                ):
                    raise GuardrailError("screenshot bundle changed after the MCP write was prepared")
            mismatches: list[str] = []
            for field in ("title", "description"):
                if snapshot.get(field, "") != expected.get(field, ""):
                    mismatches.append(field)
            expected_parent = expected.get("parent_id")
            actual_parent = snapshot["parent_ids"][0] if snapshot["parent_ids"] else None
            if actual_parent != expected_parent:
                mismatches.append("parent")
            if not html_equivalent(body, snapshot["body"]):
                mismatches.append("body")
            if mismatches:
                raise GuardrailError(f"MCP read-back mismatch for: {', '.join(mismatches)}")
        except BaseException as exc:
            pending.update(phase="ambiguous", error=redact(str(exc), None), failed_at=utc_now())
            atomic_write_json(store / "manifest.json", manifest)
            raise

        returned_body = snapshot["body"]
        atomic_write_text(path, returned_body)
        result_kind = "new" if record.get("draft_kind") == "new" else "never_published"
        timestamp = utc_now()
        screenshot_pending = screenshot_manifest is not None
        record.update(
            author_id=snapshot["author_id"],
            intercom_id=snapshot["id"],
            draft_kind="never_published",
            baseline=snapshot,
            local_hash=sha256_text(returned_body),
            remote_hash=sha256_text(returned_body),
            verified=not screenshot_pending,
            pending_write=None,
            comparison_review=None,
            updated_at=timestamp,
            last_pushed_at=timestamp,
        )
        if screenshot_manifest:
            fixed_baseline = {
                field: snapshot.get(field)
                for field in SCREENSHOT_BASELINE_FIELDS
            }
            screenshot_manifest["staged_baseline"] = {
                "snapshot": fixed_baseline,
                "sha256": stable_hash(fixed_baseline),
                "staged_at": timestamp,
            }
            screenshot_manifest["state"] = "manual_upload_pending"
            screenshot_manifest["updated_at"] = timestamp
            for shot in screenshot_manifest["screenshots"]:
                if shot["state"] == "approved":
                    shot["state"] = "manual_upload_pending"
            record["screenshots"] = {
                "state": "manual_upload_pending",
                "manifest": f"{SCREENSHOT_DIR}/{args.slug}/manifest.json",
            }
            atomic_write_json(screenshot_manifest_path(store, args.slug), screenshot_manifest)
        atomic_write_json(store / "manifest.json", manifest)
        current_state = _load_current_state(store)
        current_state["articles"] = _merge_current_state(
            store, manifest, _remote_articles_from_state(current_state)
        )
        current_state.update(
            stale=True,
            last_refresh_attempt_at=utc_now(),
            refresh_error="Intercom draft changed; refresh the article overview through MCP before another write.",
            rendered_at=utc_now(),
        )
        _write_current_state(store, current_state)
    result = {
        "local_file": str(path),
        "article_id": snapshot["id"],
        "draft_kind": result_kind,
        "verified": not screenshot_pending,
        "editor_url": editor_url(config, snapshot["content_id"]),
    }
    if screenshot_manifest:
        result.update(
            text_write_verified=True,
            screenshot_state="manual_upload_pending",
            screenshots=_screenshot_tasks(screenshot_manifest),
        )
    return result


def _placeholder_semantic_events(body: str) -> list[tuple[Any, ...]]:
    events = list(canonical_html(body))
    output: list[tuple[Any, ...]] = []
    index = 0
    while index < len(events):
        five = events[index:index + 5]
        three = events[index:index + 3]
        parsed: tuple[str, str] | None = None
        consumed = 0
        if (
            len(five) == 5
            and five[0] == ("start", "p", ())
            and five[1] == ("start", "em", ())
            and five[2][0] == "text"
            and five[3] == ("end", "em")
            and five[4] == ("end", "p")
        ):
            parsed = parse_screenshot_placeholder(str(five[2][1]))
            consumed = 5 if parsed else 0
        if (
            parsed is None
            and len(three) == 3
            and three[0] == ("start", "em", ())
            and three[1][0] == "text"
            and three[2] == ("end", "em")
        ):
            parsed = parse_screenshot_placeholder(str(three[1][1]))
            consumed = 3 if parsed else 0
        if parsed:
            output.append(("screenshot-slot", parsed[0], parsed[1]))
            index += consumed
            continue
        output.append(events[index])
        index += 1
    return output


class _RawImageCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.images: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "img":
            self.images.append({name.lower(): value or "" for name, value in attrs})

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)


def _raw_images(body: str) -> list[dict[str, str]]:
    parser = _RawImageCollector()
    parser.feed(body)
    parser.close()
    return parser.images


def _intercom_image_details(
    event: tuple[Any, ...], raw_attrs: Mapping[str, str] | None = None
) -> tuple[str, str] | None:
    if len(event) != 3 or event[:2] != ("start", "img"):
        return None
    attrs = dict(raw_attrs or dict(event[2]))
    source = attrs.get("src", "")
    alt_text = attrs.get("alt", "")
    parsed = urllib.parse.urlsplit(source)
    if (
        parsed.scheme != "https"
        or (parsed.hostname or "").lower() not in INTERCOM_IMAGE_HOSTS
        or parsed.username
        or parsed.password
    ):
        raise GuardrailError("reconciled screenshots must use an allowlisted Intercom image host")
    return source, alt_text


def reconcile_screenshot_events(
    staged_body: str,
    remote_body: str,
    screenshot_manifest: Mapping[str, Any],
) -> list[dict[str, str]]:
    expected = _placeholder_semantic_events(staged_body)
    actual = _placeholder_semantic_events(remote_body)
    raw_images = _raw_images(remote_body)
    raw_image_index = 0
    if len(expected) != len(actual):
        raise GuardrailError("editor body structure changed or screenshot count is incorrect")
    reconciled: list[dict[str, str]] = []
    shot_ids: set[str] = set()
    for position, (expected_event, actual_event) in enumerate(zip(expected, actual), start=1):
        raw_image: Mapping[str, str] | None = None
        if len(actual_event) == 3 and actual_event[:2] == ("start", "img"):
            if raw_image_index >= len(raw_images):
                raise GuardrailError("editor image parsing was inconsistent")
            raw_image = raw_images[raw_image_index]
            raw_image_index += 1
        if expected_event[0] != "screenshot-slot":
            if expected_event != actual_event:
                raise GuardrailError(
                    f"editor prose, metadata-adjacent HTML, existing image, or image order changed at event {position}"
                )
            continue
        shot_id = str(expected_event[1])
        if shot_id in shot_ids:
            raise GuardrailError(f"duplicate staged screenshot placeholder: {shot_id}")
        shot_ids.add(shot_id)
        shot = _shot_by_id(screenshot_manifest, shot_id)
        image = _intercom_image_details(actual_event, raw_image)
        must_reconcile = shot["status"] == "required" or bool(shot.get("sha256"))
        if image is None:
            if not must_reconcile and actual_event == expected_event:
                continue
            raise GuardrailError(f"{shot_id} was not replaced by exactly one Intercom-hosted image")
        source, alt_text = image
        if alt_text != shot["alt_text"]:
            raise GuardrailError(f"{shot_id} alt text does not exactly match the approved plan")
        stable_source = urllib.parse.urlunsplit(
            (*urllib.parse.urlsplit(source)[:3], "", "")
        )
        reconciled.append({
            "id": shot_id,
            "source": source,
            "stable_source": stable_source,
            "alt_text": alt_text,
            "sha256": str(shot.get("sha256") or ""),
        })
    required_ids = {
        shot["id"] for shot in screenshot_manifest["screenshots"]
        if shot["status"] == "required"
    }
    reconciled_ids = {item["id"] for item in reconciled}
    if not required_ids <= reconciled_ids:
        raise GuardrailError("not every required screenshot was reconciled")
    if raw_image_index != len(raw_images):
        raise GuardrailError("editor contains an unexpected extra image")
    return reconciled


def _download_intercom_png(url: str, *, timeout: float) -> bytes:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or (parsed.hostname or "").lower() not in INTERCOM_IMAGE_HOSTS:
        raise GuardrailError("screenshot download host is not allowlisted")
    request = urllib.request.Request(
        url,
        headers={"Accept": "image/png", "User-Agent": "ZenoSupportScreenshotReconciler/1"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            final_url = response.geturl()
            final_host = (urllib.parse.urlsplit(final_url).hostname or "").lower()
            if final_host not in INTERCOM_IMAGE_HOSTS:
                raise GuardrailError("screenshot download redirected to a non-Intercom host")
            value = response.read(MAX_SCREENSHOT_BYTES + 1)
    except GuardrailError:
        raise
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise GuardrailError("could not download an Intercom screenshot for hash reconciliation") from exc
    _validate_png(value)
    return value


def reconcile_editor_screenshots(
    args: argparse.Namespace, environ: Mapping[str, str]
) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    config = load_config(store)
    snapshot = _load_mcp_article_file(args.snapshot, config)
    with store_lock(store):
        manifest = load_manifest(store)
        record, local_body, path = validate_local(store, args.slug, manifest)
        screenshot_manifest = load_screenshot_manifest(store, args.slug)
        assert screenshot_manifest is not None
        if screenshot_manifest["state"] != "manual_upload_pending":
            raise GuardrailError("screenshots are not awaiting manual Intercom editor upload")
        staged = screenshot_manifest.get("staged_baseline")
        if not isinstance(staged, dict) or not isinstance(staged.get("snapshot"), dict):
            raise GuardrailError("staged screenshot baseline is missing")
        expected = staged["snapshot"]
        if stable_hash(expected) != staged.get("sha256"):
            raise GuardrailError("staged screenshot baseline is stale or changed")
        current_baseline = record.get("baseline")
        current_fixed = {
            field: current_baseline.get(field)
            for field in expected
        } if isinstance(current_baseline, dict) else None
        if current_fixed != expected or local_body != expected["body"]:
            raise GuardrailError("local article or baseline changed after placeholder staging")
        if snapshot["state"] != "draft":
            raise GuardrailError("screenshot reconciliation is allowed only for a verified draft")
        immutable_fields = SCREENSHOT_IMMUTABLE_FIELDS
        changed = [field for field in immutable_fields if snapshot.get(field) != expected.get(field)]
        if changed:
            raise GuardrailError(
                f"editor metadata or draft identity changed during manual upload: {', '.join(changed)}"
            )
        images = reconcile_screenshot_events(
            str(expected["body"]), snapshot["body"], screenshot_manifest
        )
        for image in images:
            shot = _shot_by_id(screenshot_manifest, image["id"])
            downloaded = _download_intercom_png(image["source"], timeout=args.timeout)
            digest = hashlib.sha256(downloaded).hexdigest()
            if digest != shot.get("sha256"):
                raise GuardrailError(f"{image['id']} does not match the approved PNG")
        timestamp = utc_now()
        returned_body = snapshot["body"]
        atomic_write_text(path, returned_body)
        record.update(
            baseline=snapshot,
            local_hash=sha256_text(returned_body),
            remote_hash=sha256_text(returned_body),
            verified=True,
            pending_write=None,
            comparison_review=None,
            updated_at=timestamp,
        )
        record["screenshots"] = {
            "state": "reconciled", "manifest": f"{SCREENSHOT_DIR}/{args.slug}/manifest.json"
        }
        reconciled_ids = {image["id"] for image in images}
        for shot in screenshot_manifest["screenshots"]:
            if shot["id"] in reconciled_ids:
                shot["state"] = "reconciled"
        screenshot_manifest.update(
            state="reconciled",
            article_body_sha256=sha256_text(returned_body),
            reconciliation={
                "reconciled_at": timestamp,
                "snapshot_sha256": stable_hash({
                    field: snapshot.get(field) for field in (*immutable_fields, "body")
                }),
                "images": [
                    {
                        "id": image["id"],
                        "stable_source": image["stable_source"],
                        "alt_text": image["alt_text"],
                        "sha256": image["sha256"],
                    }
                    for image in images
                ],
            },
            updated_at=timestamp,
        )
        atomic_write_json(screenshot_manifest_path(store, args.slug), screenshot_manifest)
        atomic_write_json(store / "manifest.json", manifest)
    return {
        "local_file": str(path),
        "article_id": snapshot["id"],
        "draft_kind": "never_published",
        "verified": True,
        "screenshot_state": "reconciled",
        "editor_url": editor_url(config, snapshot["content_id"]),
        "screenshots": _screenshot_tasks(screenshot_manifest),
    }


def import_markdown_command(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    source = Path(args.input).expanduser().resolve()
    try:
        markdown = source.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise GuardrailError(f"Markdown handoff is missing: {source}") from exc
    with store_lock(store):
        manifest = load_manifest(store)
        record = get_record(manifest, args.slug)
        screenshot_manifest = load_screenshot_manifest(store, args.slug, required=False)
        if screenshot_manifest and screenshot_manifest["state"] == "manual_upload_pending":
            raise GuardrailError(
                "manual screenshot upload is pending; reconcile before replacing local article HTML"
            )
        body = markdown_to_intercom_html(markdown, str(record.get("title") or ""))
        path = article_file(store, args.slug)
        atomic_write_text(path, body)
        record.update(
            local_hash=sha256_text(body),
            verified=False,
            comparison_review=None,
            updated_at=utc_now(),
        )
        atomic_write_json(store / "manifest.json", manifest)
        _refresh_current_state_if_present(store, manifest)
    return {
        "local_file": str(path),
        "slug": args.slug,
        "source_file": str(source),
        "converted": True,
        "valid": True,
    }


def validate_local(store: Path, slug: str, manifest: Mapping[str, Any] | None = None) -> tuple[dict[str, Any], str, Path]:
    manifest = load_manifest(store) if manifest is None else manifest
    record = get_record(manifest, slug)
    path = article_file(store, slug)
    try:
        body = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise GuardrailError(f"article file is missing: {path}") from exc
    if not str(record.get("title", "")).strip():
        raise GuardrailError("article title must not be empty")
    if record.get("locale") != "en":
        raise GuardrailError("only English/default-locale content is supported")
    normalize_id(record.get("author_id"), "author ID")
    normalize_id_list(record.get("collection_ids") or [])
    validate_html(body)
    return record, body, path


def validate_command(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    record, body, path = validate_local(store, args.slug)
    return {
        "local_file": str(path),
        "slug": args.slug,
        "valid": True,
        "local_hash": sha256_text(body),
        "draft_kind": record["draft_kind"],
    }


def _comparison_data(record: Mapping[str, Any], body: str, path: Path) -> dict[str, Any]:
    baseline = record.get("baseline") or {}
    metadata_before = {
        "title": baseline.get("title", ""),
        "description": baseline.get("description", ""),
        "author_id": baseline.get("author_id"),
        "collection_ids": baseline.get("parent_ids", []),
    }
    metadata_after = {
        "title": record["title"],
        "description": record.get("description", ""),
        "author_id": record["author_id"],
        "collection_ids": record.get("collection_ids", []),
    }
    baseline_body = baseline.get("body") or ""
    old_lines = baseline_body.splitlines(keepends=True)
    new_lines = body.splitlines(keepends=True)
    metadata_before_lines = json.dumps(
        metadata_before, indent=2, sort_keys=True, ensure_ascii=False
    ).splitlines(keepends=True)
    metadata_after_lines = json.dumps(
        metadata_after, indent=2, sort_keys=True, ensure_ascii=False
    ).splitlines(keepends=True)
    metadata_diff = "".join(
        difflib.unified_diff(
            metadata_before_lines,
            metadata_after_lines,
            fromfile="existing-metadata.json",
            tofile="updated-metadata.json",
        )
    )
    html_diff = "".join(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile="existing-intercom.html",
            tofile=path.name,
        )
    )
    return {
        "changed": metadata_before != metadata_after or old_lines != new_lines,
        "metadata_before": metadata_before,
        "metadata_after": metadata_after,
        "metadata_diff": metadata_diff,
        "baseline_body": baseline_body,
        "proposed_body": body,
        "html_diff": html_diff,
    }


def _comparison_fingerprint(data: Mapping[str, Any]) -> dict[str, str]:
    return {
        "baseline_body_sha256": sha256_text(str(data["baseline_body"])),
        "proposed_body_sha256": sha256_text(str(data["proposed_body"])),
        "metadata_before_sha256": stable_hash(data["metadata_before"]),
        "metadata_after_sha256": stable_hash(data["metadata_after"]),
        "changes_sha256": stable_hash(
            {
                "changed": data["changed"],
                "metadata_diff": data["metadata_diff"],
                "html_diff": data["html_diff"],
            }
        ),
    }


def _display_metadata(value: Any) -> str:
    if value in (None, "", []):
        return "—"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def _render_comparison(record: Mapping[str, Any], data: Mapping[str, Any]) -> str:
    before = data["metadata_before"]
    after = data["metadata_after"]
    changed_fields = [field for field in before if before[field] != after[field]]
    metadata_rows = []
    labels = {
        "title": "Title",
        "description": "Description",
        "author_id": "Author ID",
        "collection_ids": "Collection IDs",
    }
    for field, label in labels.items():
        state = ' class="changed"' if field in changed_fields else ""
        metadata_rows.append(
            f"<tr{state}><th>{html_lib.escape(label)}</th>"
            f"<td>{html_lib.escape(_display_metadata(before[field]))}</td>"
            f"<td>{html_lib.escape(_display_metadata(after[field]))}</td></tr>"
        )
    html_diff = str(data["html_diff"])
    additions = sum(
        1 for line in html_diff.splitlines() if line.startswith("+") and not line.startswith("+++")
    )
    removals = sum(
        1 for line in html_diff.splitlines() if line.startswith("-") and not line.startswith("---")
    )
    baseline_body = str(data["baseline_body"]) or '<p class="local-empty-state">No existing article body.</p>'
    proposed_body = str(data["proposed_body"])
    existing_title = html_lib.escape(_display_metadata(before["title"]))
    updated_title = html_lib.escape(_display_metadata(after["title"]))
    existing_description = html_lib.escape(_display_metadata(before["description"]))
    updated_description = html_lib.escape(_display_metadata(after["description"]))
    metadata_diff = html_lib.escape(str(data["metadata_diff"]) or "No metadata changes.")
    source_diff = html_lib.escape(html_diff or "No HTML source changes.")
    status = "Changes detected" if data["changed"] else "No changes detected"
    draft_kind = str(record.get("draft_kind") or "")
    existing_label = "Existing Intercom draft" if draft_kind == "never_published" else "Existing article"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Article update review — {updated_title}</title>
  <style>
    :root {{ color-scheme: light; --ink:#17212b; --muted:#667085; --line:#d0d5dd; --panel:#fff;
      --canvas:#f4f6f8; --brand:#4457ff; --added:#e8f7ed; --removed:#fff0ee; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--canvas); color:var(--ink); font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    main {{ max-width:1600px; margin:0 auto; padding:32px; }}
    h1,h2,h3,p {{ margin-top:0; }}
    .review-header,.metadata,.diffs {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:24px; margin-bottom:24px; }}
    .eyebrow {{ color:var(--brand); font-size:12px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }}
    .summary {{ color:var(--muted); max-width:900px; }}
    .stats {{ display:flex; flex-wrap:wrap; gap:10px; }}
    .stat {{ border:1px solid var(--line); border-radius:999px; padding:5px 10px; background:#fff; }}
    .stat.added {{ background:var(--added); }} .stat.removed {{ background:var(--removed); }}
    table {{ width:100%; border-collapse:collapse; }}
    th,td {{ padding:11px 12px; border-bottom:1px solid #eaecf0; text-align:left; vertical-align:top; }}
    thead th {{ color:var(--muted); font-size:12px; text-transform:uppercase; }}
    tbody th {{ width:150px; }} tr.changed {{ background:#fff8df; }}
    .comparison {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:20px; align-items:start; margin-bottom:24px; }}
    .version {{ min-width:0; background:var(--panel); border:1px solid var(--line); border-radius:14px; overflow:hidden; }}
    .version > header {{ padding:20px 22px; border-bottom:1px solid var(--line); background:#fafafa; }}
    .version.updated {{ border-color:#aab2ff; box-shadow:0 0 0 2px rgba(68,87,255,.08); }}
    .version.updated > header {{ background:#f1f3ff; }}
    .badge {{ display:inline-block; margin-bottom:10px; border-radius:999px; padding:4px 9px; background:#e9ecf0; font-size:12px; font-weight:700; }}
    .updated .badge {{ color:#2839ce; background:#dfe3ff; }}
    .description {{ color:var(--muted); white-space:pre-wrap; }}
    .article-content {{ padding:28px; min-height:360px; overflow-wrap:anywhere; }}
    .article-content img,.article-content iframe {{ max-width:100%; }}
    .article-content table {{ display:block; overflow-x:auto; }}
    .article-content pre {{ overflow-x:auto; padding:14px; background:#f8f8f8; border-radius:8px; }}
    .local-empty-state {{ color:var(--muted); font-style:italic; }}
    details {{ border:1px solid var(--line); border-radius:10px; margin-top:12px; background:#fff; }}
    summary {{ cursor:pointer; padding:13px 15px; font-weight:700; }}
    details pre {{ margin:0; padding:16px; border-top:1px solid var(--line); overflow:auto; background:#101828; color:#f2f4f7; font:12px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace; white-space:pre; }}
    .notice {{ color:var(--muted); font-size:13px; margin-bottom:0; }}
    @media (max-width:900px) {{ main {{ padding:18px; }} .comparison {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
<main>
  <section class="review-header">
    <p class="eyebrow">Local Intercom article comparison</p>
    <h1>{updated_title}</h1>
    <p class="summary">Review the existing Intercom content beside the proposed local draft. This is a local content preview, not an exact reproduction of Intercom’s editor chrome.</p>
    <div class="stats">
      <span class="stat">{html_lib.escape(status)}</span>
      <span class="stat">{len(changed_fields)} metadata field(s) changed</span>
      <span class="stat added">+{additions} HTML line(s)</span>
      <span class="stat removed">−{removals} HTML line(s)</span>
    </div>
  </section>
  <section class="metadata">
    <h2>Metadata comparison</h2>
    <table>
      <thead><tr><th>Field</th><th>Existing</th><th>Updated</th></tr></thead>
      <tbody>{''.join(metadata_rows)}</tbody>
    </table>
  </section>
  <section class="comparison">
    <article class="version existing">
      <header><span class="badge">{html_lib.escape(existing_label)}</span><h2>{existing_title}</h2><p class="description">{existing_description}</p></header>
      <div class="article-content">{baseline_body}</div>
    </article>
    <article class="version updated">
      <header><span class="badge">Updated local draft</span><h2>{updated_title}</h2><p class="description">{updated_description}</p></header>
      <div class="article-content">{proposed_body}</div>
    </article>
  </section>
  <section class="diffs">
    <h2>Exact source changes</h2>
    <p class="notice">The comparison panes show the local rendered result. The diffs below are the exact metadata and HTML source changes that will be submitted.</p>
    <details><summary>Metadata diff</summary><pre>{metadata_diff}</pre></details>
    <details open><summary>HTML diff</summary><pre>{source_diff}</pre></details>
  </section>
</main>
</body>
</html>
"""


def _comparison_paths(store: Path, slug: str) -> tuple[Path, Path]:
    root = store / COMPARISON_DIR / validate_slug(slug)
    return root / "comparison.html", root / "comparison.json"


def _accessible_comparison_paths(review_copy_dir: Path, slug: str) -> tuple[Path, Path]:
    root = review_copy_dir / validate_slug(slug)
    return root / "comparison.html", root / "comparison.json"


def _write_comparison(
    store: Path,
    slug: str,
    record: MutableMapping[str, Any],
    data: Mapping[str, Any],
    local_file: Path,
    review_copy_dir: Path | None = None,
) -> tuple[Path, Path, dict[str, Any]]:
    comparison_file, metadata_file = _comparison_paths(store, slug)
    rendered = _render_comparison(record, data)
    atomic_write_text(comparison_file, rendered)
    fingerprint = _comparison_fingerprint(data)
    metadata = {
        "schema_version": COMPARISON_SCHEMA_VERSION,
        "kind": "intercom-article-local-comparison",
        "slug": slug,
        "generated_at": utc_now(),
        "local_file": str(local_file),
        "comparison_file": str(comparison_file),
        "changed": data["changed"],
        "metadata_before": data["metadata_before"],
        "metadata_after": data["metadata_after"],
        "metadata_diff": data["metadata_diff"],
        "html_diff": data["html_diff"],
        **fingerprint,
        "comparison_sha256": sha256_text(rendered),
    }
    atomic_write_json(metadata_file, metadata)
    review = {
        **fingerprint,
        "comparison_sha256": metadata["comparison_sha256"],
        "comparison_metadata_sha256": sha256_text(metadata_file.read_text(encoding="utf-8")),
        "generated_at": metadata["generated_at"],
    }
    if review_copy_dir is not None:
        accessible_file, accessible_metadata_file = _accessible_comparison_paths(
            review_copy_dir, slug
        )
        metadata_text = metadata_file.read_text(encoding="utf-8")
        atomic_write_text(accessible_file, rendered)
        atomic_write_text(accessible_metadata_file, metadata_text)
        accessible_hash = sha256_text(accessible_file.read_text(encoding="utf-8"))
        accessible_metadata_hash = sha256_text(
            accessible_metadata_file.read_text(encoding="utf-8")
        )
        if (
            accessible_hash != review["comparison_sha256"]
            or accessible_metadata_hash != review["comparison_metadata_sha256"]
        ):
            raise GuardrailError("the workspace-accessible comparison copy does not match")
        review.update(
            {
                "accessible_comparison_file": str(accessible_file),
                "accessible_comparison_metadata_file": str(accessible_metadata_file),
                "accessible_comparison_sha256": accessible_hash,
                "accessible_comparison_metadata_sha256": accessible_metadata_hash,
            }
        )
    record["comparison_review"] = review
    return comparison_file, metadata_file, review


def _require_current_comparison(
    store: Path,
    slug: str,
    record: Mapping[str, Any],
    body: str,
    local_file: Path,
) -> Path:
    review = record.get("comparison_review")
    if not isinstance(review, dict):
        raise GuardrailError(
            f"a fresh local comparison is required before updating this draft; run diff {slug} and review it"
        )
    data = _comparison_data(record, body, local_file)
    fingerprint = _comparison_fingerprint(data)
    if any(review.get(key) != value for key, value in fingerprint.items()):
        raise GuardrailError(
            f"the local comparison is stale because the article changed; rerun diff {slug} and review it again"
        )
    comparison_file, metadata_file = _comparison_paths(store, slug)
    try:
        comparison_hash = sha256_text(comparison_file.read_text(encoding="utf-8"))
        metadata_hash = sha256_text(metadata_file.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GuardrailError(
            f"the local comparison artifact is missing; rerun diff {slug} and review it again"
        ) from exc
    if (
        comparison_hash != review.get("comparison_sha256")
        or metadata_hash != review.get("comparison_metadata_sha256")
    ):
        raise GuardrailError(
            f"the local comparison artifact changed; rerun diff {slug} and review it again"
        )
    accessible_file_raw = review.get("accessible_comparison_file")
    accessible_metadata_raw = review.get("accessible_comparison_metadata_file")
    if accessible_file_raw or accessible_metadata_raw:
        if not accessible_file_raw or not accessible_metadata_raw:
            raise GuardrailError(
                f"the workspace-accessible comparison record is incomplete; rerun diff {slug}"
            )
        accessible_file = Path(str(accessible_file_raw))
        accessible_metadata_file = Path(str(accessible_metadata_raw))
        try:
            accessible_hash = sha256_text(accessible_file.read_text(encoding="utf-8"))
            accessible_metadata_hash = sha256_text(
                accessible_metadata_file.read_text(encoding="utf-8")
            )
        except FileNotFoundError as exc:
            raise GuardrailError(
                f"the workspace-accessible comparison is missing; rerun diff {slug} and review it again"
            ) from exc
        if (
            accessible_hash != review.get("accessible_comparison_sha256")
            or accessible_metadata_hash
            != review.get("accessible_comparison_metadata_sha256")
            or accessible_hash != comparison_hash
            or accessible_metadata_hash != metadata_hash
        ):
            raise GuardrailError(
                f"the workspace-accessible comparison changed; rerun diff {slug} and review it again"
            )
    return comparison_file


def diff_command(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    review_copy_dir = resolve_review_copy_dir(args.review_copy_dir)
    with store_lock(store):
        manifest = load_manifest(store)
        record, body, path = validate_local(store, args.slug, manifest)
        data = _comparison_data(record, body, path)
        comparison_file, metadata_file, review = _write_comparison(
            store, args.slug, record, data, path, review_copy_dir
        )
        atomic_write_json(store / "manifest.json", manifest)
    return {
        "local_file": str(path),
        "changed": data["changed"],
        "metadata_before": data["metadata_before"],
        "metadata_after": data["metadata_after"],
        "metadata_diff": data["metadata_diff"],
        "html_diff": data["html_diff"],
        "comparison_file": str(comparison_file),
        "comparison_metadata_file": str(metadata_file),
        "comparison_sha256": review["comparison_sha256"],
        "accessible_comparison_file": review.get("accessible_comparison_file"),
        "accessible_comparison_metadata_file": review.get(
            "accessible_comparison_metadata_file"
        ),
        "accessible_comparison_sha256": review.get("accessible_comparison_sha256"),
    }


def _payload_matches(article: Mapping[str, Any], payload: Mapping[str, Any], config: Mapping[str, Any]) -> str:
    snapshot = validate_remote_article(article, config)
    mismatches: list[str] = []
    for field in ("title", "description", "author_id"):
        expected = payload.get(field, "")
        actual = snapshot.get(field, "")
        if actual != expected:
            mismatches.append(field)
    if "parent_ids" in payload and snapshot["parent_ids"] != payload["parent_ids"]:
        mismatches.append("parent_ids")
    if not html_equivalent(str(payload["body"]), snapshot["body"]):
        mismatches.append("body")
    if mismatches:
        raise GuardrailError(f"read-back mismatch for: {', '.join(mismatches)}")
    return snapshot["body"]


def _write_intent(record: MutableMapping[str, Any], method: str, path: str, payload: Mapping[str, Any]) -> None:
    if record.get("pending_write"):
        raise GuardrailError("a pending or ambiguous prior write blocks further writes")
    record["pending_write"] = {
        "phase": "prepared",
        "method": method,
        "path": path,
        "request_hash": stable_hash(payload),
        "prepared_at": utc_now(),
    }


def _record_write_failure(
    store: Path,
    manifest: MutableMapping[str, Any],
    record: MutableMapping[str, Any],
    exc: BaseException,
    token: str,
    *,
    retain: bool,
) -> None:
    if retain:
        pending = record.get("pending_write") or {}
        pending.update(phase="ambiguous", error=redact(str(exc), token), failed_at=utc_now())
        record["pending_write"] = pending
    else:
        record["pending_write"] = None
    atomic_write_json(store / "manifest.json", manifest)


def _assert_baseline_unchanged(
    current: Mapping[str, Any], baseline: Mapping[str, Any], fields: Sequence[str], message: str
) -> None:
    for field in fields:
        if field == "body":
            if not html_equivalent(str(current.get(field) or ""), str(baseline.get(field) or "")):
                raise GuardrailError(message)
        elif current.get(field) != baseline.get(field):
            raise GuardrailError(message)


def push_draft(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    if not args.confirm_draft_write:
        raise GuardrailError("push-draft requires --confirm-draft-write after explicit user authorization")
    store = resolve_store(args.store, environ)
    config = load_config(store)
    token = require_token(environ)
    client = IntercomClient(config["api_base"], token, timeout=args.timeout)

    with store_lock(store):
        require_fresh_current_state(store)
        manifest = load_manifest(store)
        record, body, path = validate_local(store, args.slug, manifest)
        if load_screenshot_manifest(store, args.slug, required=False):
            raise GuardrailError(
                "screenshot-managed articles must be staged through prepare-mcp-write and verify-mcp-write"
            )
        if record.get("pending_write"):
            raise GuardrailError("a pending or ambiguous prior write blocks further writes; inspect status")
        kind = record.get("draft_kind")
        article_id = record.get("intercom_id")
        if kind == "new":
            payload = build_article_payload(record, body)
            method, remote_path = "POST", "/articles"
        elif kind == "never_published":
            article_id = normalize_id(article_id, "article ID")
            current = validate_remote_article(client.get_article(article_id), config)
            baseline = record.get("baseline")
            if not isinstance(baseline, dict):
                raise GuardrailError("missing begin baseline")
            _assert_baseline_unchanged(current, baseline, REMOTE_COMPARE_FIELDS, "remote article changed after begin")
            if current["state"] != "draft" or current.get("has_unpublished_changes") not in {None, False}:
                raise GuardrailError("article is no longer a clean never-published draft")
            payload = build_article_payload(record, body)
            method, remote_path = "PUT", f"/articles/{article_id}"
            assert_safe_request(method, remote_path, payload)
        elif kind == "published_revision":
            article_id = normalize_id(article_id, "article ID")
            current_raw = client.get_article(article_id)
            current = validate_remote_article(current_raw, config)
            baseline = record.get("baseline")
            if not isinstance(baseline, dict):
                raise GuardrailError("missing begin baseline")
            _assert_baseline_unchanged(current, baseline, LIVE_COMPARE_FIELDS, "published article changed after begin")
            if record.get("collection_ids", []) != baseline.get("parent_ids", []):
                raise GuardrailError("collection changes cannot be staged for a live article")
            _ensure_no_remote_draft(client, current_raw)
            payload = build_staged_payload(record, body)
            method, remote_path = "PUT", f"/articles/{article_id}/draft"
        else:
            raise GuardrailError(f"unsupported draft kind: {kind!r}")

        _write_intent(record, method, remote_path, payload)
        atomic_write_json(store / "manifest.json", manifest)
        write_accepted = False
        try:
            if kind == "new":
                response = client.create_article(payload)
                write_accepted = True
                article_id = normalize_id(response.get("id"), "created article ID")
                record["pending_write"]["article_id"] = str(article_id)
                atomic_write_json(store / "manifest.json", manifest)
                verified = client.get_article(article_id)
                snapshot = validate_remote_article(verified, config)
                if snapshot["state"] != "draft":
                    raise GuardrailError("created article did not read back as a draft")
                returned_body = _payload_matches(verified, payload, config)
                result_kind = "new"
                result_snapshot = snapshot
                record["draft_kind"] = "never_published"
                record["intercom_id"] = str(article_id)
                record["baseline"] = snapshot
            elif kind == "never_published":
                client.update_draft_article(article_id, payload)
                write_accepted = True
                verified = client.get_article(article_id)
                snapshot = validate_remote_article(verified, config)
                if snapshot["state"] != "draft":
                    raise GuardrailError("updated article did not remain a draft")
                returned_body = _payload_matches(verified, payload, config)
                result_kind = "never_published"
                result_snapshot = snapshot
                record["baseline"] = snapshot
            else:
                live_before = selected_snapshot(record["baseline"], LIVE_COMPARE_FIELDS)
                client.stage_live_draft(article_id, payload)
                write_accepted = True
                staged = client.get_draft(article_id)
                if staged is None:
                    raise GuardrailError("staged draft was not available during read-back")
                staged_snapshot = validate_remote_article(staged, config)
                if not staged.get("has_unpublished_changes"):
                    raise GuardrailError("Intercom did not mark the staged draft as unpublished changes")
                returned_body = _payload_matches(staged, payload, config)
                live_after = validate_remote_article(client.get_article(article_id), config)
                if selected_snapshot(live_after, LIVE_COMPARE_FIELDS) != live_before:
                    raise GuardrailError("published article changed while staging its draft")
                record["staged_draft_hash"] = sha256_text(returned_body)
                record["staged_draft_updated_at"] = staged_snapshot.get("draft_updated_at")
                result_kind = "published_revision"
                result_snapshot = staged_snapshot
        except BaseException as exc:
            retain = write_accepted or not isinstance(exc, ApiError) or exc.ambiguous
            _record_write_failure(store, manifest, record, exc, token, retain=retain)
            raise

        atomic_write_text(path, returned_body)
        timestamp = utc_now()
        record.update(
            local_hash=sha256_text(returned_body),
            remote_hash=sha256_text(returned_body),
            verified=True,
            pending_write=None,
            updated_at=timestamp,
            last_pushed_at=timestamp,
        )
        atomic_write_json(store / "manifest.json", manifest)
        current_state = _load_current_state(store)
        current_state["articles"] = _merge_current_state(
            store, manifest, _remote_articles_from_state(current_state)
        )
        current_state.update(
            stale=True,
            last_refresh_attempt_at=utc_now(),
            refresh_error="Intercom draft changed; refresh the article overview through MCP before another write.",
            rendered_at=utc_now(),
        )
        _write_current_state(store, current_state)
        return {
            "local_file": str(path),
            "article_id": str(article_id),
            "draft_kind": result_kind,
            "verified": True,
            "editor_url": editor_url(config, result_snapshot["content_id"]),
        }


def status_command(args: argparse.Namespace, environ: Mapping[str, str]) -> dict[str, Any]:
    store = resolve_store(args.store, environ)
    config = load_config(store)
    manifest = load_manifest(store)
    slugs = [validate_slug(args.slug)] if args.slug else sorted(manifest["articles"])
    output: list[dict[str, Any]] = []
    client: IntercomClient | None = None
    if args.remote:
        client = IntercomClient(config["api_base"], require_token(environ), timeout=args.timeout)
    for slug in slugs:
        record, body, path = validate_local(store, slug, manifest)
        baseline = record.get("baseline") if isinstance(record.get("baseline"), dict) else {}
        content_id = baseline.get("content_id")
        if content_id is None and record.get("intercom_id") and (store / CURRENT_STATE_JSON).exists():
            state = _load_current_state(store)
            for entry in state.get("articles", []):
                remote = entry.get("remote") if isinstance(entry, dict) else None
                if isinstance(remote, dict) and str(remote.get("id")) == str(record["intercom_id"]):
                    content_id = remote.get("content_id")
                    break
        item: dict[str, Any] = {
            "slug": slug,
            "local_file": str(path),
            "article_id": record.get("intercom_id"),
            "draft_kind": record.get("draft_kind"),
            "valid": True,
            "local_changed": sha256_text(body) != record.get("remote_hash"),
            "verified": bool(record.get("verified")),
            "pending_write": record.get("pending_write"),
            "editor_url": editor_url(config, content_id) if content_id is not None else None,
        }
        screenshot_manifest = load_screenshot_manifest(store, slug, required=False)
        if screenshot_manifest:
            item["screenshot_state"] = screenshot_manifest["state"]
            item["screenshots"] = _screenshot_tasks_for_review(screenshot_manifest)
        if client and record.get("intercom_id"):
            remote = validate_remote_article(client.get_article(record["intercom_id"]), config)
            item["remote_state"] = remote["state"]
            item["remote_matches_baseline"] = remote == record.get("baseline")
            item["has_unpublished_changes"] = remote.get("has_unpublished_changes")
        output.append(item)
    return {"store": str(store), "articles": output}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Own local article HTML and prepare verified draft-only Intercom MCP operations."
    )
    parser.add_argument("--store", help="content store (default: INTERCOM_ARTICLES_HOME or ~/Documents/Intercom Articles)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    setup = subparsers.add_parser("setup", help="create provider-neutral workspace configuration")
    setup.add_argument("--api-base", default=DEFAULT_API_BASE)
    setup.add_argument("--workspace-id", required=True)
    setup.add_argument("--default-author-id", required=True)
    setup.add_argument("--sample-content-id", required=True)
    setup.add_argument("--sample-editor-url", required=True)
    setup.add_argument("--replace", action="store_true")
    setup.set_defaults(handler=setup_store)

    new = subparsers.add_parser("new", help="create a new local article draft")
    new.add_argument("slug")
    new.add_argument("--title", required=True)
    new.add_argument("--description", default="")
    new.add_argument("--author-id")
    new.add_argument("--collection-id", action="append", default=[])
    new.set_defaults(handler=new_article)

    begin = subparsers.add_parser("begin", help="capture an existing article baseline for local editing")
    begin.add_argument("article_id")
    begin.add_argument("--slug")
    begin.add_argument("--timeout", type=float, default=20.0)
    begin.set_defaults(handler=begin_article)

    begin_mcp = subparsers.add_parser(
        "begin-mcp", help="capture an existing draft baseline from a normalized Intercom MCP snapshot"
    )
    begin_mcp.add_argument("--snapshot", required=True, help="path to a normalized get_article snapshot")
    begin_mcp.add_argument("--slug")
    begin_mcp.set_defaults(handler=begin_mcp_article)

    validate = subparsers.add_parser("validate", help="validate local metadata and HTML")
    validate.add_argument("slug")
    validate.set_defaults(handler=validate_command)

    diff = subparsers.add_parser(
        "diff", help="write a local side-by-side comparison and diff against the begin baseline"
    )
    diff.add_argument("slug")
    diff.add_argument(
        "--review-copy-dir",
        help="absolute active-workspace directory for a hash-bound, user-accessible comparison copy",
    )
    diff.set_defaults(handler=diff_command)

    import_markdown = subparsers.add_parser(
        "import-markdown", help="convert a constrained Markdown handoff into canonical local HTML"
    )
    import_markdown.add_argument("slug")
    import_markdown.add_argument("--input", required=True, help="path to the reviewed Markdown handoff")
    import_markdown.set_defaults(handler=import_markdown_command)

    import_state = subparsers.add_parser(
        "import-current-state", help="import a complete normalized Intercom MCP article snapshot"
    )
    import_state.add_argument("--snapshot", required=True, help="path to the normalized JSON snapshot")
    import_state.set_defaults(handler=import_current_state)

    stale_state = subparsers.add_parser(
        "mark-current-state-stale", help="retain the last overview while recording a failed MCP refresh"
    )
    stale_state.add_argument("--reason", required=True)
    stale_state.set_defaults(handler=mark_current_state_stale)

    render_state = subparsers.add_parser(
        "render-current-state", help="rebuild the overview with current local article status"
    )
    render_state.set_defaults(handler=render_current_state)

    push = subparsers.add_parser("push-draft", help="explicitly create or update an Intercom draft")
    push.add_argument("slug")
    push.add_argument("--confirm-draft-write", action="store_true")
    push.add_argument("--timeout", type=float, default=20.0)
    push.set_defaults(handler=push_draft)

    prepare_mcp = subparsers.add_parser(
        "prepare-mcp-write", help="prepare an explicitly approved create_article or update_article call"
    )
    prepare_mcp.add_argument("slug")
    prepare_mcp.add_argument("--snapshot", help="fresh normalized get_article snapshot for an existing draft")
    prepare_mcp.add_argument("--confirm-draft-write", action="store_true")
    prepare_mcp.set_defaults(handler=prepare_mcp_write)

    verify_mcp = subparsers.add_parser(
        "verify-mcp-write", help="verify an MCP draft write from a normalized get_article read-back"
    )
    verify_mcp.add_argument("slug")
    verify_mcp.add_argument("--snapshot", required=True, help="normalized post-write get_article snapshot")
    verify_mcp.set_defaults(handler=verify_mcp_write)

    init_shots = subparsers.add_parser(
        "init-screenshots", help="validate and initialize a structured screenshot capture plan"
    )
    init_shots.add_argument("slug")
    init_shots.add_argument("--plan", required=True, help="absolute path to the screenshot plan JSON")
    init_shots.set_defaults(handler=init_screenshots)

    register_shot = subparsers.add_parser(
        "register-screenshot", help="validate and register one Browser-plugin PNG capture"
    )
    register_shot.add_argument("slug")
    register_shot.add_argument("shot_id")
    register_shot.add_argument("--input", required=True, help="absolute path to a captured PNG")
    register_shot.add_argument(
        "--capture-metadata", required=True, help="absolute path to capture metadata JSON"
    )
    register_shot.set_defaults(handler=register_screenshot)

    review_shots = subparsers.add_parser(
        "review-screenshots", help="create hash-bound screenshot copies and a local review gallery"
    )
    review_shots.add_argument("slug")
    review_shots.add_argument(
        "--review-copy-dir",
        required=True,
        help="absolute active-workspace .context/intercom-article-screenshots directory",
    )
    review_shots.set_defaults(handler=review_screenshots)

    approve_shots = subparsers.add_parser(
        "approve-screenshots", help="record explicit approval of unchanged screenshot review artifacts"
    )
    approve_shots.add_argument("slug")
    approve_shots.add_argument("--confirm-screenshot-approval", action="store_true")
    approve_shots.set_defaults(handler=approve_screenshots)

    reconcile_shots = subparsers.add_parser(
        "reconcile-editor-screenshots",
        help="verify manual Intercom image insertion against the staged placeholder baseline",
    )
    reconcile_shots.add_argument("slug")
    reconcile_shots.add_argument("--snapshot", required=True, help="fresh normalized get_article snapshot")
    reconcile_shots.add_argument("--timeout", type=float, default=20.0)
    reconcile_shots.set_defaults(handler=reconcile_editor_screenshots)

    status = subparsers.add_parser("status", help="show local status, optionally with authenticated remote state")
    status.add_argument("slug", nargs="?")
    status.add_argument("--remote", action="store_true")
    status.add_argument("--timeout", type=float, default=20.0)
    status.set_defaults(handler=status_command)
    return parser


def execute(argv: Sequence[str] | None = None, environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    args = build_parser().parse_args(argv)
    env = os.environ if environ is None else environ
    return args.handler(args, env)


def main(argv: Sequence[str] | None = None, *, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    try:
        result = execute(argv)
    except GuardrailError as exc:
        print(json.dumps({"ok": False, "error": redact(str(exc), os.environ.get(TOKEN_ENV))}), file=stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=False), file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

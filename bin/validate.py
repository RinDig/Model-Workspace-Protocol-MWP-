#!/usr/bin/env python3
"""Check an ICM repo against the rules it declares about itself.

Sources of truth:
  _core/CONVENTIONS.md  -- Patterns 1-15, Naming Conventions, Quality Guardrails
  README.md             -- the PR checklist

Usage:
  python3 bin/validate.py [repo_root] [--strict]

By default, style rules (line length, em dashes, file naming) skip bundled
skills/ content, which is copied verbatim from upstream per Pattern 9 and is
not the repo's to reformat. --strict checks everything.

Exits 0 if all rules pass, 1 otherwise.
"""

import collections
import os
import re
import sys

EM_DASH = chr(0x2014)  # by codepoint: the rule forbids the literal
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv"}
# Filenames the spec itself mandates in non-lowercase form.
NAME_EXEMPT = {"CLAUDE.md", "CONTEXT.md", "CONVENTIONS.md", "README.md", "SKILL.md",
               "LICENSE", "LICENSE.txt", "_core", ".gitkeep", ".gitignore", ".github"}
LOWER_RE = re.compile(r"^[a-z0-9]+([-._][a-z0-9]+)*$")
STAGE_RE = re.compile(r"^\d{2}-[a-z0-9]+(-[a-z0-9]+)*$")
# A path ref containing any of these is resolved at run time, not check time.
RUNTIME_MARKERS = ("{{", "[", "*")
PLACEHOLDER_LINKS = re.compile(
    r"\]\(\s*(link-to-\S*|TODO|TBD|url|example\.com\S*|#?)\s*\)", re.I)

results = []


def rule(name, violations, note=""):
    results.append((name, list(violations), note))


def walk_files(root, ext=None, skip_vendored=False):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            p = os.path.join(dp, f)
            r = os.path.relpath(p, root)
            if skip_vendored and re.search(r"(^|/)skills/", "/" + r.replace(os.sep, "/")):
                continue
            if ext and not f.endswith(ext):
                continue
            yield r, p


def walk_dirs(root, skip_vendored=False):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for d in dn:
            p = os.path.join(dp, d)
            r = os.path.relpath(p, root)
            if skip_vendored and re.search(r"(^|/)skills/", "/" + r.replace(os.sep, "/")):
                continue
            yield r, p


def read(p):
    with open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def sections(text):
    return [ln[3:].strip() for ln in text.splitlines() if ln.startswith("## ")]


def inputs_rows(text):
    """Yield cell-lists for each data row of the '## Inputs' table."""
    inside = False
    for ln in text.splitlines():
        if ln.startswith("## "):
            inside = ln.strip() == "## Inputs"
            continue
        if not inside or not ln.startswith("|"):
            continue
        if re.fullmatch(r"\|[-: |]+\|", ln.strip()):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells and cells[0] in ("Source", "File"):
            continue
        yield cells


def is_stage_context(rel):
    return os.path.basename(rel) == "CONTEXT.md" and "/stages/" in "/" + rel.replace(os.sep, "/")


def main(root, strict):
    root = os.path.abspath(root)
    V = not strict  # skip vendored skills/ for style rules unless --strict

    # -- Quality Guardrails -------------------------------------------------
    rule("CONTEXT.md under 80 lines",
         ["%s (%d)" % (r, len(read(p).splitlines()))
          for r, p in walk_files(root, ".md") if os.path.basename(r) == "CONTEXT.md"
          and len(read(p).splitlines()) > 80])

    L3 = ("references", "shared", "brand-vault", "design-system", "skills")
    rule("Reference files under 200 lines",
         ["%s (%d)" % (r, len(read(p).splitlines()))
          for r, p in walk_files(root, ".md", skip_vendored=V)
          if any("/%s/" % d in "/" + r.replace(os.sep, "/") for d in L3)
          and len(read(p).splitlines()) > 200])

    rule("No em dashes (U+2014)",
         ["%s (%d)" % (r, read(p).count(EM_DASH))
          for r, p in walk_files(root, (".md", ".txt", ".py", ".js", ".tsx"), skip_vendored=V)
          if EM_DASH in read(p)])

    rule("Empty persistent folders carry .gitkeep",
         [r for r, p in walk_dirs(root) if not os.listdir(p)])

    # -- Naming Conventions -------------------------------------------------
    rule("No spaces in file or folder names",
         sorted({r for r, _ in walk_files(root) if " " in r}
                | {r for r, _ in walk_dirs(root) if " " in r}))

    rule("Names are lowercase-with-hyphens",
         sorted({r for r, _ in list(walk_files(root, skip_vendored=V))
                 + list(walk_dirs(root, skip_vendored=V))
                 if os.path.basename(r) not in NAME_EXEMPT
                 and not LOWER_RE.match(os.path.basename(r))}))

    rule("Stage folders use a zero-padded numeric prefix",
         [r for r, _ in walk_dirs(root)
          if re.search(r"(^|/)stages/[^/]+$", r.replace(os.sep, "/"))
          and not STAGE_RE.match(os.path.basename(r))])

    # -- Pattern 1: stage contracts ----------------------------------------
    bad = []
    for r, p in walk_files(root, ".md"):
        if not is_stage_context(r):
            continue
        s = sections(read(p))
        try:
            if not s.index("Inputs") < s.index("Process") < s.index("Outputs"):
                bad.append("%s: out of order %s" % (r, s))
        except ValueError:
            bad.append("%s: missing Inputs/Process/Outputs, has %s" % (r, s))
    rule("Stage CONTEXT.md has Inputs, Process, Outputs in order", bad)

    # -- Pattern 4: every Inputs row names a section scope ------------------
    rule("Inputs rows carry a Section/Scope value",
         ["%s: %s" % (r, cells[:2])
          for r, p in walk_files(root, ".md") if is_stage_context(r)
          for cells in inputs_rows(read(p)) if len(cells) < 4 or not cells[2]])

    # -- Pattern 3: one-way cross-references --------------------------------
    edges = collections.defaultdict(set)
    for r, p in walk_files(root, ".md"):
        m = re.search(r"(workspaces/[^/]+)/stages/(\d{2}-[a-z0-9-]+)/",
                      "/" + r.replace(os.sep, "/") + "/")
        if not m:
            continue
        ws, src = m.group(1), m.group(2)
        for tgt in set(re.findall(r"\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*", read(p))):
            if tgt != src and os.path.isdir(os.path.join(root, ws, "stages", tgt)):
                edges[(ws, src)].add(tgt)
    rule("Stage cross-references are one-way",
         sorted({"%s: %s <-> %s" % (ws, *sorted([s, t]))
                 for (ws, s), ts in edges.items() for t in ts
                 if s in edges.get((ws, t), ())}))

    # -- Pattern 2 / PR checklist: no committed stage outputs ---------------
    rule("Output folders contain only .gitkeep",
         ["%s: %s" % (r, sorted(set(os.listdir(p)) - {".gitkeep"}))
          for r, p in walk_dirs(root) if os.path.basename(r) == "output"
          and set(os.listdir(p)) - {".gitkeep"}])

    # -- Inputs-table paths actually resolve --------------------------------
    # The filesystem is the orchestration layer, so a wrong path here is an
    # uncaught bug. Per-run outputs are gitignored by design and are skipped.
    bad = []
    for r, p in walk_files(root, ".md"):
        if not is_stage_context(r):
            continue
        base = os.path.dirname(p)
        for cells in inputs_rows(read(p)):
            for ref in re.findall(r"`([^`]+)`", cells[1] if len(cells) > 1 else ""):
                ref = ref.strip()
                if not ref or ref.startswith("http"):
                    continue
                if not ("/" in ref or ref.endswith(".md")):
                    continue
                if any(m in ref for m in RUNTIME_MARKERS):
                    continue
                if re.search(r"/output/", ref):        # gitignored per-run artifact
                    continue
                if not os.path.exists(os.path.normpath(os.path.join(base, ref))):
                    bad.append("%s -> %s" % (r, ref))
    rule("Inputs-table paths resolve", bad)

    # -- Every workspace is registered in both routing tables ---------------
    ws_dir = os.path.join(root, "workspaces")
    bad = []
    if os.path.isdir(ws_dir):
        readme = read(os.path.join(root, "README.md")) if os.path.exists(
            os.path.join(root, "README.md")) else ""
        claude = read(os.path.join(root, "CLAUDE.md")) if os.path.exists(
            os.path.join(root, "CLAUDE.md")) else ""
        for w in sorted(os.listdir(ws_dir)):
            if not os.path.isdir(os.path.join(ws_dir, w)):
                continue
            missing = [n for n, t in (("README.md", readme), ("CLAUDE.md", claude))
                       if w not in t]
            if missing:
                bad.append("%s: absent from %s" % (w, ", ".join(missing)))
    rule("Every workspace is registered in README and root CLAUDE.md", bad)

    # -- No placeholder link targets ----------------------------------------
    rule("Markdown links have real targets",
         ["%s: %s" % (r, m.group(0))
          for r, p in walk_files(root, ".md", skip_vendored=V)
          for m in PLACEHOLDER_LINKS.finditer(read(p))])

    # -- Folders named in the README exist ----------------------------------
    # Catches docs describing a layout the tree does not have.
    bad = []
    readme_path = os.path.join(root, "README.md")
    if os.path.exists(readme_path):
        real = {os.path.basename(r) for r, _ in walk_dirs(root)}
        for name in sorted(set(re.findall(r"^\s{2,}([a-z_][a-z0-9_-]*)/\s+#",
                                          read(readme_path), re.M))):
            if name not in real:
                bad.append("README describes %s/ but no such directory exists" % name)
    rule("Directories described in the README exist", bad)

    # -- report -------------------------------------------------------------
    failed = 0
    for name, bad, note in results:
        if bad:
            failed += 1
            print("FAIL  %-52s %d" % (name, len(bad)))
            for b in bad[:6]:
                print("        - %s" % b)
            if len(bad) > 6:
                print("        ... and %d more" % (len(bad) - 6))
        else:
            print("PASS  %s" % name)
    print("\n%d/%d rules passed%s" % (len(results) - failed, len(results),
                                      "" if strict else "  (skills/ skipped; --strict to include)"))
    return 1 if failed else 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    sys.exit(main(args[0] if args else ".", "--strict" in sys.argv))

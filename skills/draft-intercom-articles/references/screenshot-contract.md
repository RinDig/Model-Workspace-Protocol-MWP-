# Screenshot capture and reconciliation contract

Use this contract only after the article Markdown has been reviewed and accepted. V1 covers the Zeno web app. Word add-in screenshots remain manual.

## Article placeholders

Use one unique placeholder for every planned image:

```text
[Screenshot: shot-01 | concise description]
```

Put the placeholder immediately after the text or numbered step it illustrates. IDs must use `shot-` followed by at least two digits and must appear in ascending article order. Do not use Markdown images or embed a local file in article HTML.

## Capture plan

Pass an absolute JSON path to `init-screenshots <slug> --plan <path>`. The plan must contain exactly these fields:

```json
{
  "schema_version": 1,
  "allowed_origins": ["https://demo.zeno.law"],
  "workspace_sentinel": "Zeno Support Screenshot Demo",
  "screenshots": [
    {
      "id": "shot-01",
      "placement": "Immediately after step 1",
      "capture_goal": "Show the Files menu with New folder visible",
      "expected_ui_labels": ["Files", "New folder"],
      "framing": "Crop the menu and surrounding context with 16px padding",
      "alt_text": "The Files menu in Zeno with New folder selected",
      "setup_notes": "Use the pre-seeded synthetic onboarding matter",
      "status": "required"
    }
  ]
}
```

The plan IDs must match the article placeholders exactly and in order. `status` is `required` or `optional`. Required screenshots block approval until captured and completion until reconciliation. When an optional screenshot is not captured, `approve-screenshots` removes only its placeholder before staging, invalidates any earlier article comparison, and reports the omitted ID.

## Capture metadata

Capture through the Browser plugin at an allowlisted origin only. Register each PNG with an absolute metadata JSON path:

```json
{
  "origin": "https://demo.zeno.law",
  "path": "/files",
  "workspace_sentinel": "Zeno Support Screenshot Demo",
  "sentinel_visible": true,
  "locale": "en",
  "theme": "light",
  "viewport": {"width": 1440, "height": 900},
  "expected_ui_labels_visible": ["Files", "New folder"],
  "unexpected_sensitive_data": false,
  "durable_mutations": [],
  "browser_plugin": true,
  "clip": {"x": 120, "y": 90, "width": 760, "height": 620, "padding": 16}
}
```

Never include cookies, authentication headers, tokens, browser storage, credentials, full URLs with query parameters, or customer data. Navigation and opening reversible controls are allowed. Creating, editing, deleting, sending, uploading, or otherwise durably mutating product data is forbidden. Stop immediately if unexpected personal or customer data appears; do not attempt automatic redaction.

Captures must be unannotated PNGs, in English, light theme, and within a 1440×900 viewport. Crop to the relevant region with consistent padding.

## Local lifecycle

The helper uses these states:

1. `planned`
2. `captured`
3. `approved`
4. `manual_upload_pending`
5. `reconciled`

Canonical PNGs and the screenshot manifest live under `<article-store>/screenshots/<slug>/`. `review-screenshots` creates hash-bound copies and a gallery under the supplied active-workspace `.context/intercom-article-screenshots/<slug>/`. A recapture invalidates the complete screenshot approval.

Run:

```bash
python3 "$SKILL_DIR/scripts/intercom_articles.py" --store "$ARTICLE_STORE" \
  init-screenshots <slug> --plan <absolute-plan.json>
python3 "$SKILL_DIR/scripts/intercom_articles.py" --store "$ARTICLE_STORE" \
  register-screenshot <slug> shot-01 --input <absolute.png> \
  --capture-metadata <absolute-capture.json>
python3 "$SKILL_DIR/scripts/intercom_articles.py" --store "$ARTICLE_STORE" \
  review-screenshots <slug> \
  --review-copy-dir <absolute-workspace>/.context/intercom-article-screenshots
python3 "$SKILL_DIR/scripts/intercom_articles.py" --store "$ARTICLE_STORE" \
  approve-screenshots <slug> --confirm-screenshot-approval
```

Approval is a separate human checkpoint after visually inspecting the gallery.

## Staging and reconciliation

After the existing exact draft-write approval, `prepare-mcp-write` returns visible placeholders plus ordered PNG paths, placement instructions, and exact alt text. Call the returned Intercom MCP operation unchanged. `verify-mcp-write` verifies the text-only draft and moves the workflow to `manual_upload_pending`.

The user then opens the returned authenticated editor link, replaces each required placeholder with exactly one approved PNG using Intercom's native upload or paste flow, and sets the exact alt text. Intercom documents device upload, paste, and image alt text in [Format an article](https://www.intercom.com/help/en/articles/56978-format-an-article). Do not automate editor mutations. While upload is pending, the helper blocks another article write or Markdown import that could invalidate the baseline.

After the user finishes, fetch a fresh `get_article` snapshot and run:

```bash
python3 "$SKILL_DIR/scripts/intercom_articles.py" --store "$ARTICLE_STORE" \
  reconcile-editor-screenshots <slug> --snapshot <absolute-readback.json>
```

Reconciliation requires:

- the same draft, workspace, title, description, author, parent, and locale;
- unchanged prose, HTML semantics, existing images, and image order;
- one allowlisted Intercom-hosted image in every required placeholder position;
- exact approved alt text;
- downloaded PNG bytes matching the locally approved SHA-256 hash.

Documented `div.intercom-container` wrappers, `height: auto` image styles, heading normalization, and changing signed Intercom CDN query parameters are accepted. Missing, extra, reordered, substituted, externally hosted, or incorrectly described images fail closed. A published target always fails.

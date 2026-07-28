---
name: capture-zeno-support-screenshots
description: "Capture, register, review, and approve clean Zeno web-app screenshots for an accepted Intercom support article. Use when a screenshot plan and `[Screenshot: shot-01 | description]` placeholders are ready, before the article is staged as a draft. Operate only in the allowlisted synthetic demo tenant through the Browser plugin; never mutate product data or capture customer information."
---

# Capture Zeno Support Screenshots

Turn an accepted support article's structured screenshot plan into approved, hash-bound PNGs. Hand the approved bundle back to `$manage-zeno-support-content` and `$draft-intercom-articles`; never write to Intercom.

Read `$draft-intercom-articles/references/screenshot-contract.md` before any capture. Use `$control-in-app-browser` for all browser work and follow its complete setup and browser documentation.

## Guardrails

- Work only on the Zeno web app. Word add-in screenshots remain manual.
- Use only a pre-seeded synthetic demo tenant whose exact HTTPS origin appears in the capture plan.
- Confirm the visible demo-workspace sentinel from the plan before every capture. A matching URL alone is insufficient.
- Never inspect, export, log, or persist cookies, credentials, authentication headers, tokens, local storage, session storage, or browser profiles.
- Never create, edit, upload, send, delete, invite, save, submit, or otherwise durably mutate product data. Navigation and opening reversible controls are allowed.
- Stop immediately if unexpected personal, customer, matter, document, conversation, or production data appears. Do not capture it and do not attempt automatic redaction.
- Never annotate, blur, watermark, or synthesize the product UI.
- Keep temporary and review artifacts under the active workspace's gitignored `.context` directory. Keep canonical images only in the configured article store.

## 1. Validate the Accepted Inputs

Require:

- the accepted article slug and canonical local HTML;
- the structured screenshot plan JSON;
- the complete Legal suitability record already accepted by the article workflow;
- an absolute active-workspace path.

Run:

```bash
python3 "$DRAFT_SKILL_DIR/scripts/intercom_articles.py" \
  --store "$ARTICLE_STORE" init-screenshots "$SLUG" \
  --plan "$ABSOLUTE_PLAN_JSON"
```

Stop if plan IDs do not match the article placeholders exactly and in order. Do not repair or reorder an accepted plan silently.

## 2. Preflight the Demo Tenant

Connect through the Browser plugin. Reuse its existing signed-in session without inspecting its authentication state.

For every screenshot:

1. Set or verify a 1440×900 viewport.
2. Navigate only to an allowlisted plan origin.
3. Verify English UI and light theme from visible page state.
4. Find the exact visible demo-workspace sentinel.
5. Confirm every planned expected UI label is visible.
6. Inspect the relevant region for unexpected personal or customer data.

If any check fails, stop before taking a screenshot and report the exact failed precondition. Do not switch to a production tenant, another origin, standalone Playwright, Computer Use, or automatic redaction.

## 3. Reach the Capture State Safely

Follow the plan's setup notes using navigation and reversible UI opening only. Examples include visiting a route, changing a visible tab, opening a menu, expanding a panel, or opening an existing synthetic record.

Do not type into a form, toggle a persisted setting, upload a file, create synthetic data on demand, or click any control that may save or submit. If the required view depends on a durable action, stop and request that the demo tenant be pre-seeded.

Reconfirm the origin and sentinel after navigation.

## 4. Capture and Register Each PNG

Capture the smallest useful UI region with consistent padding. Keep enough surrounding context for orientation. Use a clean PNG with no cursor, tooltip unrelated to the task, browser chrome, annotation, or redaction.

Write the temporary PNG and a capture metadata JSON under:

```text
<active-workspace>/.context/intercom-article-screenshots/<slug>/captures/
```

The metadata must exactly follow the screenshot contract. Store only an origin and origin-relative path without query parameters. Record `durable_mutations` as an empty list and `unexpected_sensitive_data` as `false` only after visually confirming both.

Register immediately:

```bash
python3 "$DRAFT_SKILL_DIR/scripts/intercom_articles.py" \
  --store "$ARTICLE_STORE" register-screenshot "$SLUG" "$SHOT_ID" \
  --input "$ABSOLUTE_PNG" \
  --capture-metadata "$ABSOLUTE_CAPTURE_JSON"
```

Registration validates the PNG, dimensions, plan origin, sentinel, labels, viewport, safe-action declaration, and capture metadata. Any recapture invalidates approval for the complete bundle.

## 5. Create the Review Gallery

After all required screenshots are captured, run:

```bash
python3 "$DRAFT_SKILL_DIR/scripts/intercom_articles.py" \
  --store "$ARTICLE_STORE" review-screenshots "$SLUG" \
  --review-copy-dir \
  "$ACTIVE_WORKSPACE/.context/intercom-article-screenshots"
```

Return the gallery link plus every ordered PNG link, placement, exact alt text, required/optional status, dimensions, and SHA-256 hash. Ask for a dedicated visual approval of this exact bundle. Article content approval and Intercom write approval do not count.

## 6. Record Explicit Approval

Only after the user affirmatively approves the exact gallery, run:

```bash
python3 "$DRAFT_SKILL_DIR/scripts/intercom_articles.py" \
  --store "$ARTICLE_STORE" approve-screenshots "$SLUG" \
  --confirm-screenshot-approval
```

Do not approve on the user's behalf. The helper verifies that canonical images, workspace copies, and gallery have not changed.
If an optional screenshot was not captured, approval removes only that optional placeholder and returns its ID. Tell the manager to rerun the article validation and comparison before draft-write approval.

## Completion

Return:

- screenshot state `approved`;
- the workspace-accessible review gallery;
- ordered PNG links;
- placement instructions and exact alt text;
- the approved bundle hash;
- confirmation that the screenshots came from the allowlisted synthetic demo tenant without durable mutations;
- the handoff back to `$manage-zeno-support-content`.

Do not claim the article is staged, reconciled, or published.

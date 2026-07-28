from __future__ import annotations

import binascii
import importlib.util
import json
import struct
import tempfile
import unittest
import zlib
from argparse import Namespace
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "scripts" / "intercom_articles.py"
SPEC = importlib.util.spec_from_file_location("intercom_articles_screenshots", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def png(width: int = 8, height: int = 6, rgb: tuple[int, int, int] = (22, 85, 140)) -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
        )

    scanline = b"\x00" + bytes(rgb) * width
    raw = scanline * height
    return (
        MODULE.PNG_SIGNATURE
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


class ScreenshotWorkflowTest(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.store = self.root / "store"
        self.slug = "test-article"
        self.body = (
            "<h2>Open settings</h2>\n"
            "<p>Select <strong>Settings</strong>.</p>\n"
            "<p><em>[Screenshot: shot-01 | Settings panel]</em></p>\n"
        )
        (self.store / "articles").mkdir(parents=True)
        (self.store / "articles" / f"{self.slug}.html").write_text(
            self.body, encoding="utf-8"
        )
        MODULE.atomic_write_json(
            self.store / "config.json",
            {
                "api_base": "https://api.intercom.io",
                "workspace_id": "workspace-1",
                "default_author_id": 123,
                "default_locale": "en",
                "editor_url_template": "https://app.intercom.com/a/knowledge-hub/folder/{content_id}",
            },
        )
        self.record = {
            "slug": self.slug,
            "file": f"articles/{self.slug}.html",
            "title": "Test article",
            "description": "Test description",
            "collection_ids": [456],
            "locale": "en",
            "author_id": 123,
            "intercom_id": "789",
            "draft_kind": "never_published",
            "baseline": None,
            "local_hash": MODULE.sha256_text(self.body),
            "remote_hash": None,
            "verified": False,
            "pending_write": None,
            "comparison_review": None,
        }
        MODULE.atomic_write_json(
            self.store / "manifest.json",
            {"schema_version": 1, "articles": {self.slug: self.record}},
        )
        self.plan = {
            "schema_version": 1,
            "allowed_origins": ["https://demo.zeno.law"],
            "workspace_sentinel": "Zeno Support Screenshot Demo",
            "screenshots": [
                {
                    "id": "shot-01",
                    "placement": "After the Settings step",
                    "capture_goal": "Show the Settings panel",
                    "expected_ui_labels": ["Settings", "Profile"],
                    "framing": "Crop the settings panel with 16px padding",
                    "alt_text": "The Settings panel in Zeno",
                    "setup_notes": "Use the pre-seeded synthetic matter.",
                    "status": "required",
                }
            ],
        }
        self.plan_file = self.root / "plan.json"
        MODULE.atomic_write_json(self.plan_file, self.plan)
        self.capture_file = self.root / "shot.png"
        self.capture_file.write_bytes(png(600, 500))
        self.capture_metadata = {
            "origin": "https://demo.zeno.law",
            "path": "/settings",
            "workspace_sentinel": "Zeno Support Screenshot Demo",
            "sentinel_visible": True,
            "locale": "en",
            "theme": "light",
            "viewport": {"width": 1440, "height": 900},
            "expected_ui_labels_visible": ["Settings", "Profile"],
            "unexpected_sensitive_data": False,
            "durable_mutations": [],
            "browser_plugin": True,
            "clip": {"x": 100, "y": 100, "width": 600, "height": 500, "padding": 16},
        }
        self.capture_metadata_file = self.root / "capture.json"
        MODULE.atomic_write_json(self.capture_metadata_file, self.capture_metadata)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def args(self, **values: object) -> Namespace:
        return Namespace(store=str(self.store), **values)

    def init(self) -> dict[str, object]:
        return MODULE.init_screenshots(
            self.args(slug=self.slug, plan=str(self.plan_file)), {}
        )

    def register(self) -> dict[str, object]:
        return MODULE.register_screenshot(
            self.args(
                slug=self.slug,
                shot_id="shot-01",
                input=str(self.capture_file),
                capture_metadata=str(self.capture_metadata_file),
            ),
            {},
        )

    def review_and_approve(self) -> dict[str, object]:
        review_root = self.root / "workspace" / ".context" / "intercom-article-screenshots"
        MODULE.review_screenshots(
            self.args(slug=self.slug, review_copy_dir=str(review_root)), {}
        )
        return MODULE.approve_screenshots(
            self.args(slug=self.slug, confirm_screenshot_approval=True), {}
        )

    def test_plan_requires_exact_order_unique_ids_and_all_fields(self) -> None:
        self.init()
        duplicate = json.loads(json.dumps(self.plan))
        duplicate["screenshots"].append(dict(duplicate["screenshots"][0]))
        with self.assertRaisesRegex(MODULE.GuardrailError, "duplicate screenshot ID"):
            MODULE.validate_screenshot_plan(duplicate)
        bad_placeholder = self.body.replace("shot-01", "shot-02")
        (self.store / "articles" / f"{self.slug}.html").write_text(
            bad_placeholder, encoding="utf-8"
        )
        with self.assertRaisesRegex(MODULE.GuardrailError, "exactly match"):
            self.init()

    def test_png_integrity_dimensions_and_traversal_are_enforced(self) -> None:
        self.assertEqual(MODULE._validate_png(png()), (8, 6))
        corrupt = bytearray(png())
        corrupt[-5] ^= 1
        with self.assertRaisesRegex(MODULE.GuardrailError, "checksum|IEND"):
            MODULE._validate_png(bytes(corrupt))
        with self.assertRaisesRegex(MODULE.GuardrailError, "1440x900"):
            MODULE._validate_png(png(1441, 1))
        with self.assertRaisesRegex(MODULE.GuardrailError, "traversal"):
            MODULE._resolve_safe_input(
                str(self.root / "folder" / ".." / "plan.json"), "test input"
            )

    def test_capture_metadata_blocks_origin_auth_mutation_and_sensitive_data(self) -> None:
        plan = MODULE.validate_screenshot_plan(self.plan)
        shot = plan["screenshots"][0]
        valid = MODULE.validate_capture_metadata(self.capture_metadata, plan, shot)
        self.assertEqual(valid["origin"], "https://demo.zeno.law")
        for field, value, message in (
            ("origin", "https://customer.zeno.law", "not allowlisted"),
            ("durable_mutations", ["created matter"], "mutations"),
            ("unexpected_sensitive_data", True, "personal or customer data"),
        ):
            altered = dict(self.capture_metadata)
            altered[field] = value
            with self.assertRaisesRegex(MODULE.GuardrailError, message):
                MODULE.validate_capture_metadata(altered, plan, shot)
        altered = dict(self.capture_metadata)
        altered["token"] = "secret"
        with self.assertRaisesRegex(MODULE.GuardrailError, "authentication-related"):
            MODULE.validate_capture_metadata(altered, plan, shot)

    def test_review_copy_is_hash_bound_and_approval_is_invalidated_by_recapture(self) -> None:
        self.init()
        registered = self.register()
        approved = self.review_and_approve()
        self.assertEqual(approved["state"], "approved")
        accessible = Path(approved["screenshots"][0]["png_file"])
        self.assertIn(registered["sha256"][:12], accessible.name)
        self.assertEqual(accessible.read_bytes(), self.capture_file.read_bytes())
        gallery = Path(approved["review_gallery"]).read_text(encoding="utf-8")
        for expected in (
            "Settings, Profile",
            "Crop the settings panel with 16px padding",
            "Use the pre-seeded synthetic matter.",
            "https://demo.zeno.law",
            "Zeno Support Screenshot Demo",
        ):
            self.assertIn(expected, gallery)
        second = self.root / "second.png"
        second.write_bytes(png(600, 500, rgb=(200, 20, 40)))
        self.capture_file = second
        recaptured = self.register()
        self.assertTrue(recaptured["approval_invalidated"])
        state = MODULE.load_screenshot_manifest(self.store, self.slug)
        self.assertEqual(state["state"], "captured")
        self.assertIsNone(state["approval"])

    def test_changed_accessible_copy_blocks_approval(self) -> None:
        self.init()
        self.register()
        review_root = self.root / "workspace" / ".context" / "intercom-article-screenshots"
        result = MODULE.review_screenshots(
            self.args(slug=self.slug, review_copy_dir=str(review_root)), {}
        )
        Path(result["screenshots"][0]["png_file"]).write_bytes(
            png(600, 500, rgb=(1, 2, 3))
        )
        with self.assertRaisesRegex(MODULE.GuardrailError, "workspace screenshot copy changed"):
            MODULE.approve_screenshots(
                self.args(slug=self.slug, confirm_screenshot_approval=True), {}
            )

    def test_uncaptured_optional_placeholder_is_removed_before_staging(self) -> None:
        optional = dict(self.plan["screenshots"][0])
        optional.update(
            id="shot-02",
            placement="After the optional explanation",
            capture_goal="Show optional details",
            alt_text="Optional details in Zeno",
            status="optional",
        )
        self.plan["screenshots"].append(optional)
        MODULE.atomic_write_json(self.plan_file, self.plan)
        optional_body = self.body + (
            "<p><em>[Screenshot: shot-02 | Optional details]</em></p>\n"
        )
        (self.store / "articles" / f"{self.slug}.html").write_text(
            optional_body, encoding="utf-8"
        )
        self.init()
        self.register()
        approved = self.review_and_approve()
        self.assertEqual(approved["omitted_optional_ids"], ["shot-02"])
        staged_body = (
            self.store / "articles" / f"{self.slug}.html"
        ).read_text(encoding="utf-8")
        self.assertNotIn("shot-02", staged_body)
        self.assertIn("shot-01", staged_body)

    def test_intercom_wrappers_and_expiring_signatures_normalize(self) -> None:
        first = (
            '<div class="intercom-container"><img '
            'src="https://downloads.intercomcdn.com/i/o/1/image.png?expires=1&signature=a" '
            'alt="Existing" width="400" height="300" style="height: auto;"></div>'
        )
        second = (
            '<div class="intercom-container"><img '
            'src="https://downloads.intercomcdn.com/i/o/1/image.png?expires=2&signature=b" '
            'alt="Existing" width="400" height="300" style="height:auto"></div>'
        )
        self.assertTrue(MODULE.html_equivalent(first, second))
        MODULE.validate_html(first)

    def test_every_allowlisted_intercom_cdn_host_is_accepted(self) -> None:
        self.init()
        state = MODULE.load_screenshot_manifest(self.store, self.slug)
        for host in sorted(MODULE.INTERCOM_IMAGE_HOSTS):
            with self.subTest(host=host):
                remote = self.body.replace(
                    '<p><em>[Screenshot: shot-01 | Settings panel]</em></p>',
                    '<div class="intercom-container"><img '
                    f'src="https://{host}/i/o/new.png?expires=10&signature=x" '
                    'alt="The Settings panel in Zeno" width="8" height="6" '
                    'style="height: auto;"></div>',
                )
                reconciled = MODULE.reconcile_screenshot_events(
                    self.body, remote, state
                )
                self.assertEqual(reconciled[0]["id"], "shot-01")

    def test_reconciliation_accepts_one_for_one_image_and_existing_images(self) -> None:
        self.init()
        self.register()
        self.review_and_approve()
        screenshot_manifest = MODULE.load_screenshot_manifest(self.store, self.slug)
        existing = (
            '<div class="intercom-container"><img '
            'src="https://downloads.intercomcdn.com/i/o/existing.png?signature=old" '
            'alt="Existing image" width="20" height="20" style="height: auto;"></div>'
        )
        staged = existing + self.body
        remote = (
            existing.replace("signature=old", "signature=new")
            + self.body.replace(
                '<p><em>[Screenshot: shot-01 | Settings panel]</em></p>',
                '<div class="intercom-container"><img '
                'src="https://downloads.intercomcdn.com/i/o/new.png?expires=10&signature=x" '
                'alt="The Settings panel in Zeno" width="8" height="6" '
                'style="height: auto;"></div>',
            )
        )
        reconciled = MODULE.reconcile_screenshot_events(
            staged, remote, screenshot_manifest
        )
        self.assertEqual([item["id"] for item in reconciled], ["shot-01"])
        self.assertIn("signature=x", reconciled[0]["source"])
        self.assertNotIn("?", reconciled[0]["stable_source"])

    def test_reconciliation_rejects_missing_extra_reordered_substituted_or_changed_content(self) -> None:
        self.init()
        self.register()
        self.review_and_approve()
        state = MODULE.load_screenshot_manifest(self.store, self.slug)
        image = (
            '<div class="intercom-container"><img '
            'src="https://downloads.intercomcdn.com/i/o/new.png?signature=x" '
            'alt="The Settings panel in Zeno" width="8" height="6" '
            'style="height: auto;"></div>'
        )
        valid = self.body.replace(
            '<p><em>[Screenshot: shot-01 | Settings panel]</em></p>', image
        )
        cases = (
            (self.body, "not replaced"),
            (valid + image, "count|structure"),
            (valid.replace("Select", "Choose"), "prose"),
            (valid.replace("The Settings panel in Zeno", "Another image"), "alt text"),
            (valid.replace("downloads.intercomcdn.com", "example.com"), "allowlisted"),
        )
        for remote, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(MODULE.GuardrailError, message):
                    MODULE.reconcile_screenshot_events(self.body, remote, state)

    def test_reconciliation_rejects_actual_two_image_reordering(self) -> None:
        second = dict(self.plan["screenshots"][0])
        second.update(
            id="shot-02",
            placement="After the second step",
            capture_goal="Show the profile panel",
            alt_text="The Profile panel in Zeno",
        )
        self.plan["screenshots"].append(second)
        MODULE.atomic_write_json(self.plan_file, self.plan)
        staged = self.body + (
            "<p><em>[Screenshot: shot-02 | Profile panel]</em></p>\n"
        )
        (self.store / "articles" / f"{self.slug}.html").write_text(
            staged, encoding="utf-8"
        )
        self.init()
        state = MODULE.load_screenshot_manifest(self.store, self.slug)

        def image(name: str, alt: str) -> str:
            return (
                '<div class="intercom-container"><img '
                f'src="https://downloads.intercomcdn.com/i/o/{name}.png?signature=x" '
                f'alt="{alt}" width="8" height="6" style="height: auto;"></div>'
            )

        first_image = image("settings", "The Settings panel in Zeno")
        second_image = image("profile", "The Profile panel in Zeno")
        valid = staged.replace(
            '<p><em>[Screenshot: shot-01 | Settings panel]</em></p>', first_image
        ).replace(
            '<p><em>[Screenshot: shot-02 | Profile panel]</em></p>', second_image
        )
        self.assertEqual(
            [item["id"] for item in MODULE.reconcile_screenshot_events(staged, valid, state)],
            ["shot-01", "shot-02"],
        )
        reordered = staged.replace(
            '<p><em>[Screenshot: shot-01 | Settings panel]</em></p>', second_image
        ).replace(
            '<p><em>[Screenshot: shot-02 | Profile panel]</em></p>', first_image
        )
        with self.assertRaisesRegex(MODULE.GuardrailError, "alt text"):
            MODULE.reconcile_screenshot_events(staged, reordered, state)

    def _snapshot(self, body: str, *, state: str = "draft") -> dict[str, object]:
        return {
            "source": "intercom-mcp:get_article",
            "fetched_at": "2026-07-28T12:00:00+00:00",
            "complete": True,
            "article": {
                "id": "789",
                "content_id": "900",
                "workspace_id": "workspace-1",
                "title": "Test article",
                "description": "Test description",
                "body": body,
                "author_id": "123",
                "state": state,
                "created_at": 100,
                "updated_at": 200,
                "parent_id": "456",
                "parent_type": "collection",
                "url": None,
            },
        }

    def _make_pending(self) -> tuple[dict[str, object], Path]:
        self.init()
        self.register()
        self.review_and_approve()
        normalized = MODULE.validate_mcp_article_snapshot(
            self._snapshot(self.body), MODULE.load_config(self.store)
        )
        fixed = {
            field: normalized.get(field)
            for field in MODULE.SCREENSHOT_BASELINE_FIELDS
        }
        screenshots = MODULE.load_screenshot_manifest(self.store, self.slug)
        screenshots["state"] = "manual_upload_pending"
        screenshots["staged_baseline"] = {
            "snapshot": fixed,
            "sha256": MODULE.stable_hash(fixed),
            "staged_at": "2026-07-28T12:00:00+00:00",
        }
        for shot in screenshots["screenshots"]:
            shot["state"] = "manual_upload_pending"
        MODULE.atomic_write_json(
            MODULE.screenshot_manifest_path(self.store, self.slug), screenshots
        )
        manifest = MODULE.load_manifest(self.store)
        manifest["articles"][self.slug]["baseline"] = normalized
        manifest["articles"][self.slug]["screenshots"] = {
            "state": "manual_upload_pending",
            "manifest": f"screenshots/{self.slug}/manifest.json",
        }
        MODULE.atomic_write_json(self.store / "manifest.json", manifest)
        return normalized, self.root / "readback.json"

    def test_reconcile_command_hash_checks_and_marks_complete(self) -> None:
        _, snapshot_file = self._make_pending()
        image = (
            '<div class="intercom-container"><img '
            'src="https://downloads.intercomcdn.com/i/o/new.png?expires=10&signature=x" '
            'alt="The Settings panel in Zeno" width="8" height="6" '
            'style="height: auto;"></div>'
        )
        remote = self.body.replace(
            '<p><em>[Screenshot: shot-01 | Settings panel]</em></p>', image
        )
        MODULE.atomic_write_json(snapshot_file, self._snapshot(remote))
        with mock.patch.object(
            MODULE, "_download_intercom_png", return_value=png(600, 500)
        ):
            result = MODULE.reconcile_editor_screenshots(
                self.args(slug=self.slug, snapshot=str(snapshot_file), timeout=2.0), {}
            )
        self.assertTrue(result["verified"])
        self.assertEqual(result["screenshot_state"], "reconciled")
        manifest = MODULE.load_manifest(self.store)
        self.assertTrue(manifest["articles"][self.slug]["verified"])
        self.assertIn("intercom-container", (self.store / "articles" / f"{self.slug}.html").read_text())

    def test_reconcile_command_rejects_substituted_bytes_published_and_stale_baseline(self) -> None:
        _, snapshot_file = self._make_pending()
        image = (
            '<div class="intercom-container"><img '
            'src="https://downloads.intercomcdn.com/i/o/new.png?signature=x" '
            'alt="The Settings panel in Zeno" width="8" height="6" '
            'style="height: auto;"></div>'
        )
        remote = self.body.replace(
            '<p><em>[Screenshot: shot-01 | Settings panel]</em></p>', image
        )
        MODULE.atomic_write_json(snapshot_file, self._snapshot(remote))
        with mock.patch.object(
            MODULE,
            "_download_intercom_png",
            return_value=png(600, 500, rgb=(9, 9, 9)),
        ):
            with self.assertRaisesRegex(MODULE.GuardrailError, "does not match"):
                MODULE.reconcile_editor_screenshots(
                    self.args(slug=self.slug, snapshot=str(snapshot_file), timeout=2.0), {}
                )
        MODULE.atomic_write_json(snapshot_file, self._snapshot(remote, state="published"))
        with self.assertRaisesRegex(MODULE.GuardrailError, "verified draft"):
            MODULE.reconcile_editor_screenshots(
                self.args(slug=self.slug, snapshot=str(snapshot_file), timeout=2.0), {}
            )
        for field, value in (
            ("description", "Changed in editor"),
            ("created_at", 999),
            ("url", "https://example.com/changed"),
            ("parent_id", "999"),
        ):
            altered = self._snapshot(remote)
            altered["article"][field] = value
            MODULE.atomic_write_json(snapshot_file, altered)
            with self.subTest(metadata_field=field):
                with self.assertRaisesRegex(
                    MODULE.GuardrailError, "metadata or draft identity changed"
                ):
                    MODULE.reconcile_editor_screenshots(
                        self.args(
                            slug=self.slug,
                            snapshot=str(snapshot_file),
                            timeout=2.0,
                        ),
                        {},
                    )
        MODULE.atomic_write_json(snapshot_file, self._snapshot(remote))
        screenshots = MODULE.load_screenshot_manifest(self.store, self.slug)
        screenshots["staged_baseline"]["sha256"] = "0" * 64
        MODULE.atomic_write_json(
            MODULE.screenshot_manifest_path(self.store, self.slug), screenshots
        )
        with self.assertRaisesRegex(MODULE.GuardrailError, "stale or changed"):
            MODULE.reconcile_editor_screenshots(
                self.args(slug=self.slug, snapshot=str(snapshot_file), timeout=2.0), {}
            )

    def test_manual_upload_pending_blocks_new_write_preparation(self) -> None:
        self._make_pending()
        with self.assertRaisesRegex(MODULE.GuardrailError, "reconcile"):
            MODULE._assert_screenshot_bundle_approved(self.store, self.slug, self.body)

    def test_prepare_and_verify_stage_placeholders_then_lock_manual_upload(self) -> None:
        self.init()
        self.register()
        approved = self.review_and_approve()
        manifest = MODULE.load_manifest(self.store)
        record = manifest["articles"][self.slug]
        record.update(
            draft_kind="new",
            intercom_id=None,
            baseline=None,
            comparison_review=None,
        )
        MODULE.atomic_write_json(self.store / "manifest.json", manifest)
        MODULE.atomic_write_json(
            self.store / MODULE.CURRENT_STATE_JSON,
            {
                "schema_version": 1,
                "source": MODULE.CURRENT_STATE_SOURCE,
                "complete": True,
                "stale": False,
                "articles": [],
            },
        )
        prepared = MODULE.prepare_mcp_write(
            self.args(
                slug=self.slug,
                snapshot=None,
                confirm_draft_write=True,
            ),
            {},
        )
        self.assertEqual(prepared["operation"], "create_article")
        self.assertIn("[Screenshot: shot-01 | Settings panel]", prepared["arguments"]["body"])
        self.assertEqual(
            prepared["screenshots"][0]["png_file"],
            approved["screenshots"][0]["png_file"],
        )
        readback = self.root / "staged-readback.json"
        MODULE.atomic_write_json(readback, self._snapshot(self.body))
        verified = MODULE.verify_mcp_write(
            self.args(slug=self.slug, snapshot=str(readback)), {}
        )
        self.assertTrue(verified["text_write_verified"])
        self.assertFalse(verified["verified"])
        self.assertEqual(verified["screenshot_state"], "manual_upload_pending")
        with self.assertRaisesRegex(MODULE.GuardrailError, "reconcile"):
            MODULE.prepare_mcp_write(
                self.args(
                    slug=self.slug,
                    snapshot=None,
                    confirm_draft_write=True,
                ),
                {},
            )

    def test_parser_exposes_all_deterministic_screenshot_commands(self) -> None:
        parser = MODULE.build_parser()
        help_text = parser.format_help()
        for command in (
            "init-screenshots",
            "register-screenshot",
            "review-screenshots",
            "approve-screenshots",
            "reconcile-editor-screenshots",
        ):
            self.assertIn(command, help_text)


if __name__ == "__main__":
    unittest.main()

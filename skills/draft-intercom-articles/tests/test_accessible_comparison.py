from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "intercom_articles.py"
SPEC = importlib.util.spec_from_file_location("intercom_articles", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AccessibleComparisonTest(unittest.TestCase):
    def test_workspace_copy_is_identical_and_guarded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            store = root / "store"
            review_copy_dir = root / "workspace" / ".context" / "intercom-article-reviews"
            local_file = store / "articles" / "test-article.html"
            MODULE.atomic_write_text(local_file, "<p>Updated body.</p>\n")
            record = {
                "title": "Test Article",
                "description": "Updated description.",
                "author_id": 123,
                "collection_ids": [],
                "draft_kind": "never_published",
                "baseline": {
                    "title": "Test Article",
                    "description": "",
                    "author_id": 123,
                    "parent_ids": [],
                    "body": "<p>Existing body.</p>",
                },
            }
            data = MODULE._comparison_data(
                record, local_file.read_text(encoding="utf-8"), local_file
            )

            comparison_file, metadata_file, review = MODULE._write_comparison(
                store,
                "test-article",
                record,
                data,
                local_file,
                review_copy_dir,
            )

            accessible_file = Path(review["accessible_comparison_file"])
            accessible_metadata_file = Path(
                review["accessible_comparison_metadata_file"]
            )
            self.assertEqual(
                comparison_file.read_bytes(), accessible_file.read_bytes()
            )
            self.assertEqual(
                metadata_file.read_bytes(), accessible_metadata_file.read_bytes()
            )
            self.assertEqual(
                comparison_file,
                MODULE._require_current_comparison(
                    store,
                    "test-article",
                    record,
                    local_file.read_text(encoding="utf-8"),
                    local_file,
                ),
            )

            accessible_file.write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(
                MODULE.GuardrailError, "workspace-accessible comparison changed"
            ):
                MODULE._require_current_comparison(
                    store,
                    "test-article",
                    record,
                    local_file.read_text(encoding="utf-8"),
                    local_file,
                )


if __name__ == "__main__":
    unittest.main()

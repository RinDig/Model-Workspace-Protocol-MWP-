from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "intercom_articles.py"
SPEC = importlib.util.spec_from_file_location("intercom_articles", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HtmlEquivalenceTest(unittest.TestCase):
    def test_intercom_editor_normalization_is_equivalent(self) -> None:
        local = (
            "<h2>Steps</h2>"
            "<ol><li>Select <strong>Export</strong>."
            "<p><em>[Screenshot: Export]</em></p></li></ol>"
        )
        remote = (
            '<p class="no-margin"></p>'
            '<h1 id="h_adda7afd88">Steps</h1>'
            '<p class="no-margin"></p>'
            "<ol><li><p class=\"no-margin\">Select <b>Export</b>.</p>"
            '<p class="no-margin"><i>[Screenshot: Export]</i></p></li></ol>'
            '<p class="no-margin"></p>'
        )

        self.assertTrue(MODULE.html_equivalent(local, remote))

    def test_meaningful_text_change_is_not_equivalent(self) -> None:
        self.assertFalse(
            MODULE.html_equivalent(
                "<p>Export one chat.</p>",
                '<p class="no-margin">Export every chat.</p>',
            )
        )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "install_support_skills.py"
SPEC = importlib.util.spec_from_file_location("install_support_skills", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class InstallSupportSkillsTest(unittest.TestCase):
    def test_dry_run_validates_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "skills"
            result = MODULE.install(
                Path(__file__).parents[1] / "skills", target, dry_run=True
            )
            self.assertTrue(result["dry_run"])
            self.assertFalse(target.exists())
            self.assertEqual(
                [item["name"] for item in result["skills"]],
                list(MODULE.SKILL_NAMES),
            )

    def test_install_backs_up_and_replaces_exact_trees(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "skills"
            source = Path(__file__).parents[1] / "skills"
            first = MODULE.install(source, target, dry_run=False)
            self.assertEqual(first["installed"], list(MODULE.SKILL_NAMES))
            for name in MODULE.SKILL_NAMES:
                self.assertEqual(
                    MODULE.tree_hash(source / name),
                    MODULE.tree_hash(target / name),
                )
            modified = target / "draft-intercom-articles" / "SKILL.md"
            original = modified.read_text(encoding="utf-8")
            modified.write_text(original + "\nlocal modification\n", encoding="utf-8")
            second = MODULE.install(source, target, dry_run=False)
            backup = Path(second["backup"])
            self.assertTrue(
                (backup / "draft-intercom-articles" / "SKILL.md")
                .read_text(encoding="utf-8")
                .endswith("local modification\n")
            )
            self.assertEqual(
                MODULE.tree_hash(source / "draft-intercom-articles"),
                MODULE.tree_hash(target / "draft-intercom-articles"),
            )

    def test_target_root_and_symlinked_skill_are_rejected(self) -> None:
        source = Path(__file__).parents[1] / "skills"
        with self.assertRaisesRegex(MODULE.InstallError, "filesystem root"):
            MODULE.resolve_roots(str(source), "/")
        with tempfile.TemporaryDirectory() as directory:
            fake_source = Path(directory) / "source"
            fake_source.mkdir()
            (fake_source / MODULE.SKILL_NAMES[0]).symlink_to(
                source / MODULE.SKILL_NAMES[0], target_is_directory=True
            )
            with self.assertRaisesRegex(MODULE.InstallError, "unsafe"):
                MODULE.validate_skill(
                    fake_source / MODULE.SKILL_NAMES[0], MODULE.SKILL_NAMES[0]
                )


if __name__ == "__main__":
    unittest.main()

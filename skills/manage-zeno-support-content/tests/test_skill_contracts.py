from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILLS = Path(__file__).parents[2]


def skill(name: str) -> str:
    return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")


class SkillContractTest(unittest.TestCase):
    def test_coordinator_routes_to_all_specialized_skills(self) -> None:
        manager = skill("manage-zeno-support-content")
        for name in (
            "$analyze-intercom-faqs",
            "$zeno-support-article-v1",
            "$capture-zeno-support-screenshots",
            "$draft-intercom-articles",
        ):
            self.assertIn(name, manager)
        self.assertIn("known article, feature guide, revision, or single FAQ", manager)
        self.assertIn("FAQ discovery from closed conversations", manager)

    def test_every_content_handoff_has_a_target_and_review_fields(self) -> None:
        writer = skill("zeno-support-article-v1")
        manager = skill("manage-zeno-support-content")
        required = (
            "Target mode:",
            "Target article ID:",
            "Legal classification:",
            "Legal suitability status:",
            "Legal approval record:",
            "Legal scope constraints:",
            "Canonical legal sources:",
            "Demo tenant allowed origins:",
            "Demo workspace sentinel:",
            "Title:",
            "Description:",
            "Article archetype:",
            "Markdown body:",
            "Suggested placement:",
            "Verification items:",
            "Screenshot plan:",
        )
        for field in required:
            self.assertIn(field, writer)
            self.assertIn(field, manager)

    def test_legal_nature_content_is_gated_across_the_workflow(self) -> None:
        manager = skill("manage-zeno-support-content")
        writer = skill("zeno-support-article-v1")
        draft = skill("draft-intercom-articles")
        for content in (manager, writer, draft):
            self.assertIn("Legal suitability record", content)
            self.assertIn("legal-nature", content)
            self.assertIn("approved for Support", content)
            self.assertIn("Legal scope constraints:", content)
            self.assertIn("Canonical legal sources:", content)
        self.assertIn("do not produce customer-facing article copy", manager)
        self.assertIn("stop before writing an H1, article body, or staging handoff", writer)
        self.assertIn("do not run `new`, `begin-mcp`, `import-markdown`", draft)
        self.assertIn("do not substitute for Legal suitability approval", writer)
        self.assertIn("do not substitute for Legal suitability approval", draft)

    def test_remote_write_requires_a_fresh_exact_approval(self) -> None:
        manager = skill("manage-zeno-support-content")
        draft = skill("draft-intercom-articles")
        self.assertIn("fresh affirmative reply for that exact article", manager)
        self.assertIn("Earlier drafting approval does not count", draft)
        self.assertIn("--confirm-draft-write", draft)
        self.assertIn("accessible_comparison_file", manager)
        self.assertIn("accessible_comparison_file", draft)
        self.assertIn("--review-copy-dir", manager)
        self.assertIn("--review-copy-dir", draft)

    def test_mcp_article_writes_are_draft_only_and_published_updates_are_forbidden(self) -> None:
        manager = skill("manage-zeno-support-content")
        draft = skill("draft-intercom-articles")
        faq = skill("analyze-intercom-faqs")
        for content in (manager, draft):
            self.assertIn("create_article", content)
            self.assertIn("update_article", content)
            self.assertIn("state: draft", content)
            self.assertRegex(content, r"Never call `update_article` for a published article")
        self.assertRegex(faq, r"Never call MCP `create_article` or `update_article`")
        self.assertIn("`list_articles`, `search_articles`, and `get_article`", manager)

    def test_faq_candidates_remain_separate_and_private(self) -> None:
        faq = skill("analyze-intercom-faqs")
        self.assertIn("Do not combine candidates", faq)
        self.assertIn("Never interpret one candidate's approval as approval for another", faq)
        self.assertIn("Strip source IDs and all private metadata", faq)
        self.assertIn("$manage-zeno-support-content", faq)

    def test_snapshot_contract_forbids_article_bodies(self) -> None:
        contract = (
            SKILLS
            / "draft-intercom-articles"
            / "references"
            / "current-state-contract.md"
        ).read_text(encoding="utf-8")
        self.assertIn('"source": "intercom-mcp:list_articles"', contract)
        self.assertIn("Never include `body`, `body_markdown`", contract)

    def test_parallel_review_claims_use_stable_thread_identity(self) -> None:
        manager = skill("manage-zeno-support-content")
        self.assertIn("nodeRepl.requestMeta.threadId", manager)
        self.assertIn("ACTIVE-REVIEW-CLAIMS.json", manager)
        self.assertIn("Never identify a review owner by workspace name", manager)
        self.assertIn("claimed by a different thread ID", manager)
        self.assertIn("immediately before each material boundary", manager)

    def test_screenshot_workflow_has_separate_capture_upload_and_reconciliation_gates(self) -> None:
        manager = skill("manage-zeno-support-content")
        writer = skill("zeno-support-article-v1")
        draft = skill("draft-intercom-articles")
        capture = skill("capture-zeno-support-screenshots")
        for command in (
            "init-screenshots",
            "register-screenshot",
            "review-screenshots",
            "approve-screenshots",
            "reconcile-editor-screenshots",
        ):
            self.assertIn(command, draft + capture + manager)
        self.assertIn("[Screenshot: shot-01 | concise description]", writer)
        self.assertIn("**screenshot plan**", writer.lower())
        self.assertIn("manual_upload_pending", manager)
        self.assertIn("manual_upload_pending", draft)
        self.assertIn("pre-seeded synthetic demo tenant", capture)
        self.assertIn("Never automate image insertion", draft)
        self.assertIn("workflow as complete only", manager)


class ReviewClaimsTest(unittest.TestCase):
    SCRIPT = (
        SKILLS / "manage-zeno-support-content" / "scripts" / "review_claims.py"
    )

    def run_claims(
        self, registry: Path, *arguments: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(self.SCRIPT),
                *arguments,
                "--registry",
                str(registry),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def claim(
        self, registry: Path, thread_id: str, article_id: str
    ) -> subprocess.CompletedProcess[str]:
        return self.run_claims(
            registry,
            "claim",
            "--thread-id",
            thread_id,
            "--article-id",
            article_id,
            "--title",
            f"Article {article_id}",
            "--workspace",
            str(registry.parent),
        )

    def test_second_thread_cannot_claim_an_owned_article(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory) / "claims.json"
            first = self.claim(registry, "thread-a", "16039622")
            second = self.claim(registry, "thread-b", "16039622")

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 2, second.stderr)
            result = json.loads(second.stdout)
            self.assertEqual(result["status"], "claimed_by_other_thread")
            self.assertEqual(result["claim"]["thread_id"], "thread-a")

    def test_thread_cannot_claim_two_articles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory) / "claims.json"
            first = self.claim(registry, "thread-a", "16039622")
            second = self.claim(registry, "thread-a", "16039561")

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 3, second.stderr)
            self.assertEqual(
                json.loads(second.stdout)["status"],
                "thread_already_has_active_claim",
            )

    def test_reclaim_is_idempotent_and_release_requires_owner(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory) / "claims.json"
            first = self.claim(registry, "thread-a", "16039622")
            repeated = self.claim(registry, "thread-a", "16039622")
            rejected_release = self.run_claims(
                registry,
                "release",
                "--thread-id",
                "thread-b",
                "--article-id",
                "16039622",
            )
            accepted_release = self.run_claims(
                registry,
                "release",
                "--thread-id",
                "thread-a",
                "--article-id",
                "16039622",
            )

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(repeated.returncode, 0, repeated.stderr)
            self.assertEqual(
                json.loads(repeated.stdout)["status"], "already_owned_by_thread"
            )
            self.assertEqual(rejected_release.returncode, 4)
            self.assertEqual(accepted_release.returncode, 0)

            status = self.run_claims(
                registry,
                "status",
                "--thread-id",
                "thread-a",
                "--article-id",
                "16039622",
            )
            self.assertEqual(status.returncode, 0)
            self.assertEqual(json.loads(status.stdout)["status"], "unclaimed")

    def test_simultaneous_claims_have_exactly_one_winner(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            registry = Path(directory) / "claims.json"
            processes = []
            for index in range(8):
                processes.append(
                    subprocess.Popen(
                        [
                            sys.executable,
                            str(self.SCRIPT),
                            "claim",
                            "--thread-id",
                            f"thread-{index}",
                            "--article-id",
                            "16039561",
                            "--title",
                            "How Sharing and Visibility Work in Zeno",
                            "--workspace",
                            directory,
                            "--registry",
                            str(registry),
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                )

            results = [process.communicate() for process in processes]
            return_codes = [process.returncode for process in processes]
            self.assertEqual(return_codes.count(0), 1, results)
            self.assertEqual(return_codes.count(2), 7, results)

            registry_data = json.loads(registry.read_text(encoding="utf-8"))
            self.assertEqual(list(registry_data["claims"]), ["16039561"])


if __name__ == "__main__":
    unittest.main()

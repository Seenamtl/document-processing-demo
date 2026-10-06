import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from document_lab.core import EvidenceValidator, Candidate, Chunk, run_pipeline


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        (self.directory / "policy.txt").write_text(
            "Customers may request a refund within 30 days of payment.\n"
            "Employees must use unique passwords.", encoding="utf-8")

    def test_retrieval_preserves_source_and_answer(self):
        result = run_pipeline(self.directory, "How many days to request a refund?")
        self.assertEqual(result["status"], "supported_excerpt")
        self.assertIn("30 days", result["answer"])
        self.assertEqual(result["evidence"][0]["source"], "policy.txt")

    def test_unknown_question_abstains(self):
        result = run_pipeline(self.directory, "Explain quantum gravity")
        self.assertEqual(result["status"], "abstained")
        self.assertEqual(result["evidence"], [])

    def test_fabricated_answer_rejected(self):
        chunk = Chunk("one", "policy.txt", "Refunds within 30 days.", [])
        candidate = Candidate("retrieve", "Refunds within 90 days.", ["one"], 1.0)
        self.assertEqual(EvidenceValidator().run((candidate, [chunk]))["status"], "abstained")

    def test_unknown_citation_rejected(self):
        candidate = Candidate("retrieve", "Invented answer", ["missing"], 1.0)
        self.assertEqual(EvidenceValidator().run((candidate, []))["status"], "abstained")

    def test_overview_keeps_evidence(self):
        result = run_pipeline(self.directory, "Give an overview")
        self.assertEqual(result["route"], "overview")
        self.assertEqual(len(result["evidence"]), 2)

    def test_empty_corpus_abstains(self):
        (self.directory / "policy.txt").unlink()
        self.assertEqual(run_pipeline(self.directory, "refund")["status"], "abstained")

    def test_empty_question_rejected(self):
        with self.assertRaises(ValueError):
            run_pipeline(self.directory, " ")


if __name__ == "__main__":
    unittest.main()

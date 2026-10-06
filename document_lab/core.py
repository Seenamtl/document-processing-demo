"""Three deterministic agents with explicit evidence and abstention."""
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path
import re
from time import perf_counter
from typing import Generic, TypeVar

Input = TypeVar("Input")
Output = TypeVar("Output")
STOPWORDS = set("a an the is are do does i we you to of for in on how what many have can please".split())


def terms(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower())) - STOPWORDS


class BaseAgent(ABC, Generic[Input, Output]):
    @abstractmethod
    def run(self, value: Input) -> Output:
        """Process one typed input."""


@dataclass(frozen=True)
class Chunk:
    id: str
    source: str
    text: str
    tags: list[str]


@dataclass(frozen=True)
class Candidate:
    route: str
    answer: str
    evidence_ids: list[str]
    overlap_score: float


class DocumentProcessor(BaseAgent[Path, list[Chunk]]):
    def run(self, directory: Path) -> list[Chunk]:
        if not directory.is_dir():
            raise ValueError("Documents path must be an existing directory")
        chunks = []
        for file in sorted(directory.iterdir()):
            if not file.is_file() or file.suffix.lower() not in {".txt", ".md"}:
                continue
            text = file.read_text(encoding="utf-8")
            sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
            for index, sentence in enumerate(sentences):
                sentence = sentence.strip()
                if not sentence:
                    continue
                words = terms(sentence)
                tags = [tag for tag, keys in {
                    "billing": {"refund", "payment", "invoice"},
                    "security": {"password", "access", "security"},
                }.items() if words & keys]
                chunks.append(Chunk(f"{file.name}:{index + 1}", file.name, sentence, tags))
        return chunks


class RequestRouter(BaseAgent[tuple[str, list[Chunk]], Candidate]):
    def run(self, value: tuple[str, list[Chunk]]) -> Candidate:
        question, chunks = value
        query = terms(question)
        if not question.strip():
            raise ValueError("Question must not be empty")
        if "overview" in query:
            chosen = chunks[:3]
            return Candidate("overview", "\n".join(c.text for c in chosen),
                             [c.id for c in chosen], 0.0)
        ranked = sorted(chunks, key=lambda c: len(query & terms(c.text)), reverse=True)
        if not ranked or not query or not (query & terms(ranked[0].text)):
            return Candidate("retrieve", "", [], 0.0)
        best = ranked[0]
        return Candidate("retrieve", best.text, [best.id],
                         len(query & terms(best.text)) / len(query))


class EvidenceValidator(BaseAgent[tuple[Candidate, list[Chunk]], dict]):
    def run(self, value: tuple[Candidate, list[Chunk]]) -> dict:
        candidate, chunks = value
        sources = {c.id: c for c in chunks}
        evidence = [sources[i] for i in candidate.evidence_ids if i in sources]
        supported = bool(evidence) and len(evidence) == len(candidate.evidence_ids)
        expected = "\n".join(c.text for c in evidence)
        supported = supported and candidate.answer == expected
        return {
            "status": "supported_excerpt" if supported else "abstained",
            "answer": candidate.answer if supported else "No supported answer found in these documents.",
            "route": candidate.route,
            "overlap_score": candidate.overlap_score,
            "evidence": [asdict(c) for c in evidence] if supported else [],
        }


def run_pipeline(directory: Path, question: str) -> dict:
    logs = []

    def execute(name, agent, value):
        start = perf_counter()
        output = agent.run(value)
        logs.append({"agent": name, "duration_ms": round((perf_counter() - start) * 1000, 3)})
        return output

    chunks = execute("DocumentProcessor", DocumentProcessor(), directory)
    candidate = execute("RequestRouter", RequestRouter(), (question, chunks))
    result = execute("EvidenceValidator", EvidenceValidator(), (candidate, chunks))
    return {"question": question, "chunks_ingested": len(chunks), **result, "logs": logs}

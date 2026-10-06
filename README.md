# Sina Document Processing Demo

A small, runnable Python portfolio project exploring document ingestion, request routing, and evidence checking through three modular agents.

This is an independent learning prototype. It is not an implementation delivered for a previous employer, and it does not include company code, internal documents, or credentials. The included documents are fictional.

## Run

Requires Python 3.10 or newer. No external dependencies or API keys are required.

```sh
python -m document_lab --documents examples --question "How many days do I have to request a refund?"
python -m unittest discover -s tests -v
```

You can also supply `--question "Explain quantum gravity"` to see the system abstain when it cannot find relevant evidence. Optional `--output result.json` saves the full trace.

## Architecture

`Documents → DocumentProcessor → RequestRouter → EvidenceValidator → response and evidence`

- **DocumentProcessor** loads UTF-8 `.txt` and `.md` files, splits them into sentence chunks, and assigns simple keyword tags. Source file names and chunk identifiers are preserved.
- **RequestRouter** routes requests to keyword retrieval or a document overview. Retrieval ranks chunks by query-term overlap and returns a source excerpt rather than inventing an answer.
- **EvidenceValidator** checks that a retrieved excerpt and its source identifier match the ingested evidence. It abstains on unsupported retrieval results.

The agents share a typed `BaseAgent` interface. The pipeline returns structured JSON, including route, source, tags, validation status, and timing logs.

## Honest limitations

This baseline uses deterministic rules, not an LLM, embeddings, or LangChain. Its relevance score is lexical overlap, not a confidence probability. Evidence matching validates provenance, not whether a claim is true in the real world. The overview lists excerpts and is not a generated summary. It currently reads text and Markdown only and has no cloud deployment or database.

## Next milestones

1. Add PDF parsing while preserving page references.
2. Add an optional embedding retriever and compare it against the baseline on a fixed evaluation set.
3. Add an optional LangChain/LLM adapter with environment-based credentials, explicit citations, and tests for unsupported answers.
4. Add persistent storage only after defining the data schema and access rules.

## Portfolio description

“Built a modular Python document-processing prototype with three agents for ingestion, request routing, and evidence validation. Implemented source-traceable retrieval, abstention for unsupported queries, structured execution logs, and automated tests.”

Use this description after running and understanding the project. List it under Personal Projects, not as completed company work.

## Publishing

Create an empty GitHub repository, then upload this folder's contents, or initialize a Git repository inside this folder and push it to your repository. Review everything before publishing. Do not include the reference PDFs, personal records, or `.env` files.

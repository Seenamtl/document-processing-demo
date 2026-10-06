import argparse
import json
from pathlib import Path
from .core import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="Run the document agent learning prototype")
    parser.add_argument("--documents", type=Path, required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = run_pipeline(args.documents, args.question)
        rendered = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            args.output.write_text(rendered + "\n", encoding="utf-8")
        print(rendered)
    except (ValueError, OSError) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()

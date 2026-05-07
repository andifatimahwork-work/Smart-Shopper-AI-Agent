import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import ReplaceOne

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from smartshopper_agent.embeddings import embed_many
from smartshopper_agent.mongo import get_collection
from smartshopper_agent.settings import get_settings

load_dotenv(ROOT / ".env")


def load_common_information(path: pathlib.Path) -> list[dict]:
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Common information dataset harus berupa list JSON.")
    return records


def build_documents(records: list[dict]) -> list[dict]:
    now = datetime.now(timezone.utc)
    texts = [
        f"{item['title']}\nCategory: {item['category']}\n{item['content']}"
        for item in records
    ]
    embeddings = embed_many(texts)

    documents = []
    for item, text, embedding in zip(records, texts, embeddings):
        documents.append(
            {
                "_id": item["id"],
                "title": item["title"],
                "category": item["category"],
                "content": item["content"],
                "text": text,
                "embedding": embedding,
                "updated_at": now,
            }
        )
    return documents


def store_documents(documents: list[dict]) -> None:
    settings = get_settings()
    collection = get_collection(settings["common_collection"])
    operations = [ReplaceOne({"_id": doc["_id"]}, doc, upsert=True) for doc in documents]
    if operations:
        result = collection.bulk_write(operations)
        print(
            "Stored common information:",
            f"matched={result.matched_count}",
            f"upserted={len(result.upserted_ids)}",
            f"modified={result.modified_count}",
        )


def print_vector_index_instruction() -> None:
    settings = get_settings()
    print("\nBuat Atlas Vector Search Index untuk common information:")
    print(f"Database: {settings['mongo_db']}")
    print(f"Collection: {settings['common_collection']}")
    print(f"Index name: {settings['common_vector_index']}")
    print(
        json.dumps(
            {
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": 768,
                        "similarity": "cosine",
                    }
                ]
            },
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=str(ROOT / "data" / "common_information.json"),
        help="Path ke dataset common information JSON.",
    )
    args = parser.parse_args()

    records = load_common_information(pathlib.Path(args.input))
    documents = build_documents(records)
    store_documents(documents)
    print_vector_index_instruction()


if __name__ == "__main__":
    main()

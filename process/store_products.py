import argparse
import pathlib
import sys
from datetime import datetime, timezone

import pandas as pd
from dotenv import load_dotenv
from pymongo import ReplaceOne

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from smartshopper_agent.embeddings import embed_many
from smartshopper_agent.mongo import get_collection, get_db
from smartshopper_agent.settings import get_settings

load_dotenv(ROOT / ".env")


def normalize_description(value) -> str:
    text = str(value or "")
    return text.strip("[]").strip("'").strip('"')


def build_documents(df: pd.DataFrame) -> list[dict]:
    now = datetime.now(timezone.utc)
    texts = [
        f"{row['title']}\n{normalize_description(row.get('description'))}"
        for _, row in df.iterrows()
    ]
    embeddings = embed_many(texts)

    documents = []
    for (_, row), text, embedding in zip(df.iterrows(), texts, embeddings):
        meta = {
            "asin": row.get("asin"),
            "title": row.get("title"),
            "brand": row.get("brand"),
            "price": row.get("price"),
            "gender": row.get("gender"),
            "material": row.get("material"),
            "category": row.get("category"),
        }
        documents.append(
            {
                "_id": str(row.get("asin")),
                "content": text,
                "embedding": embedding,
                "meta": meta,
                "updated_at": now,
            }
        )
    return documents


def refresh_lookup_collection(name: str, values: list[str]) -> None:
    collection = get_db()[name]
    collection.delete_many({})
    docs = [{"name": value} for value in sorted({v for v in values if v})]
    if docs:
        collection.insert_many(docs)


def store_products(documents: list[dict], reset: bool) -> None:
    settings = get_settings()
    collection = get_collection(settings["product_collection"])
    if reset:
        collection.delete_many({})

    if documents:
        collection.bulk_write(
            [ReplaceOne({"_id": doc["_id"]}, doc, upsert=True) for doc in documents],
            ordered=False,
        )

    refresh_lookup_collection(
        "materials", [doc["meta"].get("material") for doc in documents]
    )
    refresh_lookup_collection(
        "categories", [doc["meta"].get("category") for doc in documents]
    )
    print(f"Stored {len(documents)} products into {settings['product_collection']}.")


def print_vector_index_instruction() -> None:
    settings = get_settings()
    print("\nBuat Atlas Vector Search Index untuk products:")
    print(f"Database: {settings['mongo_db']}")
    print(f"Collection: {settings['product_collection']}")
    print(f"Index name: {settings['product_vector_index']}")
    print(
        """{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 768,
      "similarity": "cosine"
    }
  ]
}"""
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default=str(ROOT / "data" / "datasets.pkl"),
        help="Path ke dataset produk pickle.",
    )
    parser.add_argument("--reset", action="store_true", help="Kosongkan collection dulu.")
    args = parser.parse_args()

    df = pd.read_pickle(args.input)
    documents = build_documents(df)
    store_products(documents, reset=args.reset)
    print_vector_index_instruction()


if __name__ == "__main__":
    main()

import json
import re
from typing import Any

from .embeddings import embed_text
from .llm import generate_text
from .mongo import get_collection, get_db
from .settings import get_settings


def _vector_search(
    collection_name: str,
    index_name: str,
    query: str,
    top_k: int = 5,
    num_candidates: int = 100,
) -> list[dict[str, Any]]:
    collection = get_collection(collection_name)
    pipeline = [
        {
            "$vectorSearch": {
                "index": index_name,
                "path": "embedding",
                "queryVector": embed_text(query),
                "numCandidates": max(num_candidates, top_k * 20),
                "limit": top_k,
            }
        },
        {"$addFields": {"score": {"$meta": "vectorSearchScore"}}},
    ]
    return list(collection.aggregate(pipeline))


def _doc_value(doc: dict[str, Any], key: str, default: Any = "") -> Any:
    if key in doc:
        return doc.get(key, default)
    meta = doc.get("meta") or {}
    return meta.get(key, default)


def _extract_json(text: str) -> dict[str, Any]:
    match = re.search(r"```json\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    raw = match.group(1) if match else text
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _get_allowed_values(collection_name: str) -> list[str]:
    try:
        return [
            doc["name"]
            for doc in get_db()[collection_name].find({}, {"name": 1, "_id": 0})
            if doc.get("name")
        ]
    except Exception:
        return []


def _extract_product_filters(query: str) -> dict[str, Any]:
    materials = _get_allowed_values("materials")
    categories = _get_allowed_values("categories")
    prompt = f"""
Return only valid JSON for product filters found in the user query.
Allowed keys: category, material, gender, min_price, max_price.
Use null-free JSON and omit unknown values.
Allowed materials: {materials}
Allowed categories: {categories}
User query: {query}
"""
    try:
        return _extract_json(
            generate_text(
                "You extract concise e-commerce product filters as JSON.",
                prompt,
                temperature=0,
            )
        )
    except Exception:
        return {}


def _matches_filters(doc: dict[str, Any], filters: dict[str, Any]) -> bool:
    if not filters:
        return True

    category = filters.get("category")
    if category and str(_doc_value(doc, "category")).lower() != str(category).lower():
        return False

    material = filters.get("material")
    if material and str(_doc_value(doc, "material")).lower() != str(material).lower():
        return False

    gender = filters.get("gender")
    if gender and str(_doc_value(doc, "gender")).lower() != str(gender).lower():
        return False

    price = _doc_value(doc, "price", None)
    try:
        price = float(price)
    except (TypeError, ValueError):
        price = None

    if price is not None and filters.get("min_price") is not None:
        if price < float(filters["min_price"]):
            return False

    if price is not None and filters.get("max_price") is not None:
        if price > float(filters["max_price"]):
            return False

    return True


def retrieve_product_recommendation(query: str) -> dict[str, Any]:
    """
    Retrieve product candidates from MongoDB Atlas and generate product recommendations.

    Args:
        query: User request about products, preferences, price, material, gender, or category.

    Returns:
        Dictionary with status, answer, filters, and retrieved product summaries.
    """
    settings = get_settings()
    filters = _extract_product_filters(query)
    docs = _vector_search(
        settings["product_collection"],
        settings["product_vector_index"],
        query,
        top_k=20,
    )
    filtered_docs = [doc for doc in docs if _matches_filters(doc, filters)][:5]

    context_blocks = []
    products = []
    for i, doc in enumerate(filtered_docs, start=1):
        product = {
            "title": _doc_value(doc, "title", "Unknown product"),
            "brand": _doc_value(doc, "brand", "-"),
            "price": _doc_value(doc, "price", "-"),
            "material": _doc_value(doc, "material", "-"),
            "category": _doc_value(doc, "category", "-"),
            "content": doc.get("content", ""),
            "score": round(float(doc.get("score", 0)), 4),
        }
        products.append(product)
        context_blocks.append(
            f"{i}. {product['title']}\n"
            f"Brand: {product['brand']}\n"
            f"Price: {product['price']}\n"
            f"Material: {product['material']}\n"
            f"Category: {product['category']}\n"
            f"Description: {product['content']}"
        )

    if not context_blocks:
        return {
            "status": "success",
            "answer": "Saya belum menemukan produk yang cocok dengan kriteria itu.",
            "filters": filters,
            "products": [],
        }

    answer = generate_text(
        "You are a helpful SmartShopper product recommendation assistant.",
        "User query:\n"
        f"{query}\n\n"
        "Retrieved products:\n"
        f"{chr(10).join(context_blocks)}\n\n"
        "Answer in Indonesian. Recommend the best products in a structured list. "
        "For each product include name, price, material, category, brand, and why it fits. "
        "Do not invent products outside the retrieved context.",
    )
    return {
        "status": "success",
        "answer": answer,
        "filters": filters,
        "products": products,
    }


def retrieve_common_information(query: str) -> dict[str, Any]:
    """
    Retrieve common e-commerce information such as shipping, buying, payment, refund,
    return, cancellation, voucher, tracking, warranty, and account policies.

    Args:
        query: User question about non-product shopping process or store policy.

    Returns:
        Dictionary with status, answer, and source documents.
    """
    settings = get_settings()
    docs = _vector_search(
        settings["common_collection"],
        settings["common_vector_index"],
        query,
        top_k=5,
    )

    context_blocks = []
    sources = []
    for i, doc in enumerate(docs, start=1):
        title = doc.get("title", "Common information")
        category = doc.get("category", "-")
        content = doc.get("content", "")
        sources.append(
            {
                "title": title,
                "category": category,
                "score": round(float(doc.get("score", 0)), 4),
            }
        )
        context_blocks.append(f"{i}. {title}\nCategory: {category}\nContent: {content}")

    if not context_blocks:
        return {
            "status": "success",
            "answer": "Saya belum menemukan informasi umum yang relevan untuk pertanyaan itu.",
            "sources": [],
        }

    answer = generate_text(
        "You answer SmartShopper common e-commerce questions using retrieved policy context.",
        "User question:\n"
        f"{query}\n\n"
        "Retrieved common information:\n"
        f"{chr(10).join(context_blocks)}\n\n"
        "Answer in Indonesian, concise but complete. Use only the retrieved context. "
        "If the context is insufficient, say what information is not available.",
    )
    return {"status": "success", "answer": answer, "sources": sources}

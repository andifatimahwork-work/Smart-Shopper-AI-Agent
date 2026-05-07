# Personalized SmartShopper Assistant

SmartShopper Assistant adalah mini project Product AI untuk membantu user mendapatkan rekomendasi produk dan informasi umum seputar proses belanja online. Project ini menggunakan Google ADK untuk agent dan tools, MongoDB Atlas untuk penyimpanan data, SentenceTransformers untuk embedding, serta Groq untuk model LLM.

## Fitur

- Rekomendasi produk berdasarkan query user.
- Retrieval common information untuk pertanyaan pengiriman, pembelian, refund, retur, voucher, COD, dan customer service.
- Routing otomatis antara product recommendation dan common information.
- Data produk dan common information disimpan di MongoDB Atlas.
- Dapat dijalankan melalui ADK Web, Streamlit, FastAPI, atau Docker.

## Arsitektur Singkat

```text
User Query
  -> Google ADK Agent
  -> Product Recommendation Tool / Common Information Tool
  -> MongoDB Atlas Vector Search
  -> Groq LLM
  -> Final Answer
```

## Struktur Project

```text
SmartShopper_Batch 41/
  data/
    datasets.pkl
    common_information.json
  process/
    store_products.py
    store_common_information.py
    test_agent.py
  smartshopper_agent/
    agent.py
    runtime.py
    rag.py
    embeddings.py
    llm.py
    mongo.py
    settings.py
  website/
    website.py
    api.py
  .env.example
  requirements.txt
```

## Setup

Jalankan command dari root project:

```powershell
cd "E:\AI ML\SmartShopper_Batch 41"
```

Buat dan aktifkan virtual environment:

```powershell
python -m venv ag_env
.\ag_env\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy file environment:

```powershell
copy .env.example .env
```

Isi `.env`:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
MONGO_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority

MONGO_DB_NAME=depato_store
MONGO_PRODUCT_COLLECTION=products
MONGO_COMMON_COLLECTION=common_information
PRODUCT_VECTOR_INDEX=vector_index
COMMON_VECTOR_INDEX=common_vector_index

EMBEDDING_MODEL_NAME=sentence-transformers/all-mpnet-base-v2
GROQ_MODEL=llama-3.3-70b-versatile
ADK_MODEL=groq/meta-llama/llama-4-scout-17b-16e-instruct
```

## MongoDB Atlas

Buat database:

```text
depato_store
```

Collection yang digunakan:

- `products`
- `materials`
- `categories`
- `common_information`

Simpan data produk:

```powershell
python process/store_products.py --reset
```

Simpan common information:

```powershell
python process/store_common_information.py
```

Buat Vector Search Index untuk collection `products` dengan nama `vector_index`:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 768,
      "similarity": "cosine"
    }
  ]
}
```

Buat Vector Search Index untuk collection `common_information` dengan nama `common_vector_index`:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 768,
      "similarity": "cosine"
    }
  ]
}
```

## Menjalankan Project

ADK Web:

```powershell
adk web --port 8001
```

Pilih app `smartshopper_agent`, lalu buat session baru.

Streamlit:

```powershell
streamlit run website/website.py
```

FastAPI:

```powershell
uvicorn website.api:app --host 0.0.0.0 --port 8000 --reload
```

Docker:

```powershell
docker compose up --build
```

## Testing

Jalankan test agent:

```powershell
python process/test_agent.py
```

Contoh pertanyaan:

- `Rekomendasikan dress cotton untuk acara santai di bawah 50 dollar.`
- `Bagaimana cara refund kalau barang yang saya terima rusak?`
- `Saya mau beli atasan yang nyaman, lalu pengirimannya berapa lama?`

Expected behavior:

- Pertanyaan produk menggunakan `retrieve_product_recommendation`.
- Pertanyaan proses belanja menggunakan `retrieve_common_information`.
- Jawaban dibuat berdasarkan hasil retrieval dari MongoDB Atlas.

## File Penting

- `smartshopper_agent/agent.py`: konfigurasi ADK agent dan tools.
- `smartshopper_agent/rag.py`: logic retrieval dan generation.
- `process/store_products.py`: storing data produk ke MongoDB Atlas.
- `process/store_common_information.py`: storing common information ke MongoDB Atlas.
- `data/common_information.json`: dataset common information.
- `website/api.py`: FastAPI endpoint.
- `website/website.py`: Streamlit UI.

## Catatan

File `.env` tidak perlu diupload ke GitHub karena berisi API key dan connection string. Gunakan `.env.example` sebagai template konfigurasi.

# Personalized SmartShopper Assistant

Mini project Product AI untuk assignment Dibimbing. Project ini mengubah template mentor yang memakai Haystack menjadi implementasi berbasis Google ADK, MongoDB Atlas, SentenceTransformers, dan Groq.

## Objective Assignment

Agent harus bisa melakukan routing otomatis:

- Product Recommendation: pertanyaan tentang rekomendasi produk, harga, material, kategori, gender, style, atau preferensi produk.
- Common Information: pertanyaan umum e-commerce seperti cara beli, pengiriman, tracking, pembayaran, refund, retur, pembatalan, voucher, COD, dan customer service.

## Arsitektur

```text
User Query
  -> Google ADK Agent
      -> FunctionTool: retrieve_product_recommendation
          -> SentenceTransformer embedding
          -> MongoDB Atlas Vector Search products
          -> Groq generation
      -> FunctionTool: retrieve_common_information
          -> SentenceTransformer embedding
          -> MongoDB Atlas Vector Search common_information
          -> Groq generation
  -> Final answer
```

Catatan ADK: di Python ADK, function yang dimasukkan ke `tools=[...]` otomatis dibungkus menjadi `FunctionTool`. Definisi agent ada di `smartshopper_agent/agent.py`.

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
    *.ipynb
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
  Dockerfile
  Dockerfile.api
  docker-compose.yml
```

## Setup Tools

Semua command di README ini dijalankan dari root project:

```bat
cd /d "E:\AI ML\SmartShopper_Batch 41"
```

Path ini sengaja dibuat lebih pendek agar instalasi dependency Python di Windows tidak mudah bermasalah karena path terlalu panjang.

### 1. Python environment

```bat
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Jika memakai Command Prompt, aktivasi venv-nya:

```bat
venv\Scripts\activate.bat
```

Jika memakai PowerShell dan script activation diblokir, jalankan terminal sebagai user biasa lalu pakai:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
venv\Scripts\Activate.ps1
```

### 2. Groq

Project ini memakai Groq untuk dua kebutuhan:

- `ADK_MODEL=groq/meta-llama/llama-4-scout-17b-16e-instruct`: dipakai Google ADK agent untuk routing FunctionTool.
- `GROQ_MODEL=llama-3.3-70b-versatile`: dipakai di dalam tool RAG untuk generation jawaban setelah data berhasil diretrieve.

Langkah:

1. Buka Groq Console.
2. Buat API key.
3. Simpan di `.env` sebagai `GROQ_API_KEY`.

### 3. MongoDB Atlas

1. Buat cluster MongoDB Atlas.
2. Buat database `depato_store`.
3. Tambahkan connection string ke `.env`.

Copy template:

```bat
copy .env.example .env
```

Isi minimal:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
MONGO_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=depato_store
ADK_MODEL=groq/meta-llama/llama-4-scout-17b-16e-instruct
```

## Storing Data ke MongoDB Atlas

### 1. Store product dataset

```bat
python process/store_products.py --reset
```

Script ini:

- membaca `data/datasets.pkl`;
- membuat embedding dengan `sentence-transformers/all-mpnet-base-v2`;
- menyimpan produk ke collection `products`;
- menyimpan lookup collection `materials` dan `categories`.

### 2. Buat Vector Search Index products

Di MongoDB Atlas, buka `Atlas Search` pada collection `products`, buat index:

- Type: Vector Search
- Name: `vector_index`
- Definition:

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

### 3. Store Common Information

```bat
python process/store_common_information.py
```

Script ini membaca `data/common_information.json`, membuat embedding, lalu upsert ke collection `common_information`.

### 4. Buat Vector Search Index common information

Di MongoDB Atlas, buka `Atlas Search` pada collection `common_information`, buat index:

- Type: Vector Search
- Name: `common_vector_index`
- Definition:

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

## Menjalankan Agent

### Opsi A: Streamlit UI

```bat
streamlit run website/website.py
```

Buka:

```text
http://localhost:8501
```

### Opsi B: FastAPI

```bat
uvicorn website.api:app --host 0.0.0.0 --port 8000 --reload
```

Cek:

```text
http://localhost:8000/docs
```

Contoh request:

```bat
curl -X POST http://localhost:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"Bagaimana cara refund kalau barang rusak?\",\"user_id\":\"demo\"}"
```

Endpoint kompatibel:

- `POST /chat`
- `POST /recommend`
- `GET /health`

### Opsi C: ADK Web

Jalankan dari folder root project ini, yaitu folder yang berisi `smartshopper_agent/`:

```bat
adk web --port 8001
```

Pilih agent `smartshopper_agent` di UI ADK. Opsi ini cocok untuk menunjukkan bahwa agent mengikuti format Google ADK dengan `root_agent`.

### Opsi D: Docker Compose

```bat
docker compose up --build
```

Service:

- Streamlit: `http://localhost:8501`
- FastAPI: `http://localhost:8000`

## Testing dan Validasi

Setelah data tersimpan dan index selesai dibuat, jalankan:

```bat
python process/test_agent.py
```

Contoh skenario yang wajib diuji:

- Product: `Rekomendasikan dress cotton untuk acara santai di bawah 50 dollar.`
- Common information: `Bagaimana cara refund kalau barang yang saya terima rusak?`
- Mixed intent: `Saya mau beli atasan yang nyaman, lalu pengirimannya berapa lama?`

Validasi yang diharapkan:

- Pertanyaan produk memanggil `retrieve_product_recommendation`.
- Pertanyaan proses jual-beli memanggil `retrieve_common_information`.
- Jawaban mengambil konteks dari MongoDB Atlas, bukan jawaban bebas tanpa retrieval.

## Mapping ke Assignment Guidance

- Analisis kebutuhan: routing dipisah antara product question dan common information question di prompt agent.
- Dataset common information: tersedia di `data/common_information.json`.
- Storing data: `process/store_common_information.py` menyimpan dokumen dan embedding ke MongoDB Atlas.
- Tools Common Information: `retrieve_common_information` di `smartshopper_agent/rag.py`, dipasang ke ADK agent.
- RAG: vector search MongoDB Atlas + Groq generation. ADK agent memakai model Groq yang lebih cocok untuk routing FunctionTool.
- Integrasi AI Agent: `smartshopper_agent/agent.py` berisi `root_agent` dengan dua tools.
- Pengujian: `process/test_agent.py`, Streamlit, FastAPI, dan ADK Web.

## Catatan Keamanan

Jangan commit `.env`. Notebook mentor yang berisi contoh credential sudah diganti menjadi placeholder. Jika credential lama pernah aktif, rotate key di Groq dan MongoDB Atlas sebelum repository dipublish.

FROM python:3.10-slim

WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONUTF8=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY smartshopper_agent/ ./smartshopper_agent/
COPY website/ ./website/
COPY data/common_information.json ./data/common_information.json

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "website/website.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]

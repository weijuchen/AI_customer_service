FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# ⭐ All packages installed from the official PyPI source
# Install core dependencies first
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.5.0 \
    python-multipart \
    numpy==1.26.4 \
    pandas \
    jieba \
    requests \
    python-dotenv \
    openai

# ⭐ Install torch from the official PyTorch source (CPU version for smaller size and faster loading)
RUN pip install --no-cache-dir \
    torch==2.1.0 \
    --index-url https://download.pytorch.org/whl/cpu

# ⭐ Key step: Install fixed version of tokenizers first (to avoid version conflicts)
RUN pip install --no-cache-dir tokenizers==0.14.1

# ⭐ Install AI-related packages (preventing automatic torch upgrade)
RUN pip install --no-cache-dir \
    transformers==4.35.0 \
    sentence-transformers==2.2.2 \
    nltk \
    faiss-cpu \
    --no-deps

# Install supplementary dependencies
RUN pip install --no-cache-dir \
    huggingface-hub \
    safetensors \
    tqdm \
    scipy \
    scikit-learn \
    Pillow \
    filelock \
    regex

# Copy application code
COPY src/ ./src/
COPY faq_data/ ./faq_data/
COPY models/ ./models/

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Health check
# Critical adjustment: Restore HEALTHCHECK and set a very long start period
# Ensure AI models have sufficient time to load.
HEALTHCHECK --interval=30s --timeout=10s --start-period=600s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start command
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
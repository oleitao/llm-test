FROM python:3.10-slim

ENV STREAMLIT_PORT=8501
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Check Python version for debugging
RUN python --version

# Upgrade pip
RUN python -m pip install --upgrade pip

# Try installing with dependency resolution check first
RUN echo "Checking for dependency conflicts..." && \
    pip install --no-cache-dir --dry-run -r requirements.txt || \
    (echo "Dependency conflict detected. See above for details." && exit 1)

# Install packages
RUN pip install --no-cache-dir -r requirements.txt

# Verify installation
RUN echo "Verifying installation..." && pip check

COPY . .

# Ensure image files and data files have proper permissions
RUN chmod 644 header.jpg header.jpeg || true
RUN mkdir -p /app/data && chmod 755 /app/data

EXPOSE ${STREAMLIT_PORT}

# Use shell form to allow environment variable substitution
CMD streamlit run app.py --server.port=$STREAMLIT_PORT --server.address=0.0.0.0

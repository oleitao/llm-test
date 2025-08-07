FROM python:3.10-slim

ENV STREAMLIT_PORT=8501
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure image files have proper permissions
RUN chmod 644 header.jpg header.jpeg || true

EXPOSE ${STREAMLIT_PORT}

# Use shell form to allow environment variable substitution
CMD streamlit run app.py --server.port=$STREAMLIT_PORT --server.address=0.0.0.0

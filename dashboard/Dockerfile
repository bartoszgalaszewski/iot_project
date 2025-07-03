FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN pip install --no-cache-dir --trusted-host pypi.python.org \
    --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    -r requirements.txt

COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]

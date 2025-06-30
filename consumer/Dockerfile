FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir \
      --trusted-host pypi.python.org \
      --trusted-host pypi.org \
      --trusted-host files.pythonhosted.org \
      -r requirements.txt
COPY consumer.py .
CMD ["python", "consumer.py"]
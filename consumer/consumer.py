#!/usr/bin/env python3
import json
import time
from datetime import datetime

from kafka import KafkaConsumer
from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection
)

# --------------- Konfiguracja ----------------
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC  = os.getenv("KAFKA_TOPIC", "air_quality")

MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
COLLECTION_NAME = "env_vectors"
VECTOR_DIM = 5

# --------------- Inicjalizacja Milvus -------
connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)

if not utility.has_collection(COLLECTION_NAME):
    fields = [
        FieldSchema(name="ts", dtype=DataType.INT64, is_primary=True, description="Unix timestamp (ms)"),
        FieldSchema(name="location", dtype=DataType.VARCHAR, max_length=64, description="Location identifier"),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIM, description="Vector [PM2.5, PM10, CO2, temp, humid]")
    ]
    schema = CollectionSchema(fields, description="Environmental conditions vectors")
    collection = Collection(name=COLLECTION_NAME, schema=schema)
    # Tworzymy indeks HNSW na wektorze
    index_params = {
        "index_type": "HNSW",
        "metric_type": "L2",
        "params": {"M": 16, "efConstruction": 200}
    }
    collection.create_index(field_name="vector", index_params=index_params)
else:
    collection = Collection(name=COLLECTION_NAME)

# Załaduj kolekcję do pamięci operacyjnej
collection.load()

# --------------- Inicjalizacja konsumenta Kafka -------
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id="env-vectorizer"
)

print(f"[*] Listening for messages on topic '{KAFKA_TOPIC}' at {KAFKA_BROKER}...")

for msg in consumer:
    data = msg.value
    try:
        pm25        = float(data["pm25"])
        pm10        = float(data["pm10"])
        co2         = float(data["co2"])
        temperature = float(data["temperature"])
        humidity    = float(data["humidity"])
        location    = data.get("device", "unknown")
        ts_ms       = int(time.time() * 1000)

        vector = [pm25, pm10, co2, temperature, humidity]

        entities = [
            [ts_ms],
            [location],
            [vector]
        ]

        result = collection.insert(entities)
        print(f"[+] Inserted vector for {location} @ {datetime.fromtimestamp(ts_ms/1000)}; Milvus IDs: {result.primary_keys}")

    except KeyError as e:
        print(f"[!] Brak pola w danych: {e}; otrzymano: {data}")
    except Exception as ex:
        print(f"[!] Błąd przy wstrzykiwaniu do Milvusa: {ex}")

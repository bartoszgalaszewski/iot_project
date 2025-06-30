#!/usr/bin/env python3
import json, os, time, logging
from dotenv import load_dotenv
from confluent_kafka import Consumer, KafkaError
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, exceptions as milvus_ex

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# Stałe ze zmiennych środowiskowych
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC  = os.getenv("KAFKA_TOPIC", "air_quality")
MILVUS_HOST  = os.getenv("MILVUS_HOST", "milvus")
MILVUS_PORT  = os.getenv("MILVUS_PORT", "19530")
COLL_NAME    = os.getenv("VECTOR_COLLECTION", "env_vectors")

# 2️⃣  Funkcja z retry dla Milvusa
def wait_for_milvus(max_retries=60, delay=5):
    """Próbuje połączyć się z Milvusem aż do skutku."""
    retry = 0
    while retry < max_retries:
        try:
            connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
            logging.info("✔️  Połączono z Milvusem (%s:%s)", MILVUS_HOST, MILVUS_PORT)
            return True
        except milvus_ex.MilvusException as e:
            retry += 1
            logging.warning("Milvus nieosiągalny (%s). Próba %d/%d – czekam %ds", e, retry, max_retries, delay)
            time.sleep(delay)
    logging.error("❌  Nie udało się połączyć z Milvusem po %d próbach", max_retries)
    return False

# Konsument Kafka (łączy się nawet, gdy broker jeszcze wstaje)
consumer_conf = {
    "bootstrap.servers": KAFKA_BROKER,
    "group.id": "aqi-consumer",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
}
consumer = Consumer(consumer_conf)
consumer.subscribe([KAFKA_TOPIC])
logging.info("▶️  Subskrybuję temat %s", KAFKA_TOPIC)

# Czekamy na Milvusa, następnie przygotowujemy kolekcję
if not wait_for_milvus():
    raise SystemExit(1)

if COLL_NAME not in connections.list_collections():
    fields = [
        FieldSchema(name="id",     dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=5),
        FieldSchema(name="city",   dtype=DataType.VARCHAR, max_length=64),
        FieldSchema(name="ts",     dtype=DataType.INT64),
    ]
    Collection(name=COLL_NAME, schema=CollectionSchema(fields))
collection = Collection(COLL_NAME)

# 5 Pętla główna
while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    if msg.error():
        if msg.error().code() != KafkaError._PARTITION_EOF:
            logging.error("Błąd konsumenta Kafka: %s", msg.error())
        continue

    try:
        payload = json.loads(msg.value())
        vec = [
            payload["list"][0]["components"].get("pm2_5", 0.0),
            payload["list"][0]["components"].get("pm10", 0.0),
            payload["list"][0]["components"].get("co", 0.0),
            payload["list"][0]["components"].get("no2", 0.0),
            payload["list"][0]["components"].get("o3", 0.0),
        ]
        city = payload.get("city", "unknown")
        ts   = int(time.time() * 1000)

        collection.insert([[vec, city, ts]])
        logging.info("💾  Zapisano wektor dla %s (%s)", city, vec[:2])
        consumer.commit(msg)
    except Exception as e:
        logging.exception("Wyjątek podczas przetwarzania: %s", e)
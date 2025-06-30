# iot_project
Projekt IoT

┌──────────────┐   HTTP   ┌─────────────┐   Kafka   ┌─────────────┐   PyMilvus   ┌────────────┐
│ OpenWeather  │ ───────▶ │  Node‑RED   │ ───────▶  │  Kafka      │  ─────────▶  │ Milvus DB  │
└──────────────┘          │  flow       │           │  broker     │              └────────────┘
                          └─────────────┘           └─────────────┘                  ▲
                                                                    REST / gRPC      │
                                                                                    Query
                                                                                     │
                                                                                ┌───────────┐
                                                                                │ Streamlit │
                                                                                └───────────┘
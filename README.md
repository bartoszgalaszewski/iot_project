# 🌍  Pipeline IoT – Jakość powietrza

Kompletny przykład, który **pobiera w czasie rzeczywistym dane o zanieczyszczeniu powietrza** (OpenWeather), przesyła je przez Kafkę, zapisuje wektorowo w Milvusie i udostępnia wizualizację oraz wyszukiwanie podobieństw w apce Streamlit.

| Usługa       | Rola w systemie                                   | Port |
|--------------|---------------------------------------------------|------|
| **Node-RED** | Niskokodowy flow pobierający dane i publikujący do Kafki | `1880` |
| **Kafka**    | Broker komunikatów                                | `9092` / `2181` |
| **Milvus**   | Baza wektorowa (FAISS)                            | `19530` (gRPC) / `9091` (REST) |
| **Streamlit**| Dashboard i zapytania podobieństwa                | `8501` |

---

## ⚡️ Architektura

```mermaid
flowchart LR
    subgraph Pobieranie
        OW[OpenWeather<br>API Air-Pollution]
        NR[Node-RED<br>flow]
    end
    KB[Kafka<br>broker]
    MV[Milvus DB]
    ST[Streamlit<br>dashboard]

    OW -- "HTTP\n(JSON)" --> NR
    NR -- "Wiadomości\nKafka" --> KB
    KB -- "PyMilvus\nSDK" --> MV
    ST -- "REST / gRPC\nzapytania" --> MV

# Fluxo do Produto

```mermaid
flowchart LR
    AGENT[ScreenshotAuditAgent]
    MINIO[MinIO / S3 compatível\nstorage quente]
    API[FastAPI\nAPI central]
    PG[(PostgreSQL\naudit_sharex)]
    REDIS[(Redis\nfila e cache)]
    WORKER[Workers Python\nOCR + classificação]
    UI[UI do produto\nrevisão e investigação]
    COLD[Camada fria\nDuplicati + Google Drive]

    AGENT -->|upload screenshot| MINIO
    AGENT -->|heartbeat + confirm ingest| API
    API --> PG
    API -->|enqueue job| REDIS
    REDIS --> WORKER
    WORKER -->|lê screenshot| MINIO
    WORKER -->|grava score / OCR / regras| PG
    UI --> API
    API --> PG
    MINIO --> COLD

    subgraph Produto
        API
        PG
        REDIS
        WORKER
        UI
    end
```

## Leitura sugerida

- O `agent` envia a imagem para o `MinIO`.
- O `agent` envia telemetria e confirmação para a `FastAPI`.
- A `API` grava o estado oficial no `PostgreSQL`.
- A `API` publica jobs no `Redis`.
- Os `workers` fazem OCR, classificação e métricas.
- A UI do produto lê o resultado consolidado do backend.

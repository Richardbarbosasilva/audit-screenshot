# Visão Geral

```mermaid
flowchart TD
    USER[Usuário corporativo]
    SHAREX[ShareX]
    AGENT[ScreenshotAuditAgent\nserviço Windows]
    SQLITE[SQLite local]
    MINIO[MinIO]
    API[FastAPI]
    PG[(PostgreSQL)]
    REDIS[(Redis)]
    WORKER[Worker OCR / Scoring]
    UI[Dashboard operacional +\nproduto de revisão]
    SEM[Semaphore + Ansible + WinRM]
    GH[GitHub]
    COLD[Backup frio]

    USER --> SHAREX
    SHAREX --> AGENT
    AGENT --> SQLITE
    AGENT --> MINIO
    AGENT --> API
    API --> PG
    API --> REDIS
    REDIS --> WORKER
    WORKER --> PG
    UI --> API
    MINIO --> COLD

    GH --> SEM
    SEM --> AGENT
    SEM --> SHAREX

    subgraph Plano de Controle
        GH
        SEM
    end

    subgraph Plano de Dados
        SHAREX
        AGENT
        SQLITE
        MINIO
        API
        PG
        REDIS
        WORKER
        UI
        COLD
    end
```

## Leitura sugerida

- O plano de controle cuida de rollout, versionamento e suporte.
- O plano de dados cuida de captura, ingestão, análise e revisão.
- Essa separação é a chave para explicar por que `Semaphore` não substitui a `API` do produto.

# Fluxo Operacional

```mermaid
flowchart LR
    GH[GitHub\nversionamento e releases]
    SEM[Semaphore UI\norquestração]
    ANS[Ansible\nplaybooks]
    WRM[WinRM / PSRP\nexecução remota]

    GPO[GPO\nbootstrap mínimo]
    HOST1[Windows Endpoint\nHOSTTESTE / HOST-TEST2]
    SHAREX[ShareX\ncaptura padronizada]
    AGENT[ScreenshotAuditAgent\nserviço local]
    SQLITE[SQLite local\nfila durável]
    SPOOL[ProgramData spool\nscreenshots]

    GH --> SEM
    SEM --> ANS
    ANS --> WRM
    GPO --> WRM
    WRM --> HOST1

    HOST1 --> SHAREX
    SHAREX --> SPOOL
    AGENT --> SQLITE
    AGENT --> SPOOL

    subgraph Operação Central
        GH
        SEM
        ANS
        WRM
    end

    subgraph Endpoint Windows
        SHAREX
        SPOOL
        AGENT
        SQLITE
    end
```

## Leitura sugerida

- `GitHub` concentra código, versionamento e releases.
- `Semaphore + Ansible + WinRM` formam o plano de controle.
- `GPO` fica só como bootstrap mínimo.
- `ShareX` captura.
- `ScreenshotAuditAgent` executa o fluxo contínuo no endpoint.
- `SQLite local` garante retry e resiliência.

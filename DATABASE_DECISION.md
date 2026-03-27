# Database Decision

## Resposta curta

Para este projeto, `PostgreSQL` ja esta otimo como banco principal.

Eu nao usaria `MongoDB` agora.

## Como eu separaria as responsabilidades

- `MinIO`: binario da imagem e, no futuro, possivelmente pacotes frios intermediarios
- `PostgreSQL`: metadata, auditoria, score, revisoes, trilha de acesso, agentes, eventos de URL
- `SQLite local`: fila duravel do endpoint Windows
- `Redis dedicado`: fila/cache do backend central quando OCR, scoring e URL audit entrarem

## Por que Postgres ja resolve bem

O modelo principal aqui e relacional:

- agentes
- eventos
- event_metadata
- event_analysis
- event_rule_hits
- review_queue
- access_audit
- no futuro: browser_events, browser_rule_hits, browser_reviews

Mesmo quando aparecer payload semiestruturado, `JSONB` no Postgres costuma ser suficiente para:

- detalhes de OCR
- evidencias mascaradas
- metadata adicional de navegador
- blobs pequenos de diagnostico

## Quando MongoDB faria sentido

Eu so consideraria `MongoDB` se voces fossem guardar, em altissimo volume:

- documentos muito variaveis
- sem necessidade relacional forte
- com consulta predominantemente orientada a documento

Nao parece ser o caso agora.

## Recomendacao final

- `MongoDB`: nao subir agora
- `PostgreSQL`: manter como sistema principal da plataforma
- `Redis`: manter dedicado para a camada assíncrona futura

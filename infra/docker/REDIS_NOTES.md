# Redis Notes

## Recomendacao

Para este projeto, nao reutilize o `NEXTCLOUD-REDIS` como Redis oficial da plataforma.

Use um Redis dedicado quando entrar a fase de backend central com:

- worker assíncrono
- OCR
- scoring
- auditoria futura de URLs
- jobs agendados

## Agora

Na fase atual do agent Windows:

- `nao e obrigatorio subir Redis`
- o retry do endpoint continua em `SQLite local`

## Depois

Quando a API central entrar:

- suba o compose `redis-audit-compose.yml`
- use senha e volume próprios
- opcionalmente ative `RedisInsight` no lab para debug

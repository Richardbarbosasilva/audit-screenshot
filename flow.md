# Blueprint de Implementacao

## Objetivo

Construir uma plataforma centralizada de auditoria de screenshots corporativos com:

- captura padronizada no endpoint Windows
- trilha de auditoria com metadata e hash
- classificacao de risco baseada em OCR + regras explicaveis
- armazenamento quente para consulta operacional
- arquivamento frio para retencao prolongada
- rollout e operacao centralizada via Semaphore + Ansible + WinRM

## Escopo da Solucao

O fluxo alvo e:

1. O usuario faz um screenshot pelo ShareX corporativo.
2. O Agent local detecta o arquivo novo na pasta spool.
3. O Agent coleta metadata local, calcula hash e prepara o envio.
4. O Agent pede a API central uma autorizacao de ingestao.
5. A API cria o `event_id` e devolve URL pre-assinada para upload.
6. O Agent envia a imagem ao storage quente.
7. O Agent confirma o envio para a API.
8. A API registra o evento e publica a analise para o worker.
9. O Worker executa OCR, extracao de entidades e scoring.
10. O backend classifica o evento como baixo, medio ou alto.
11. A interface de auditoria mostra somente o que exige revisao humana.
12. Rotinas de arquivamento consolidam lotes diarios para a camada fria.

## Principios de Projeto

- O banco e a fonte de verdade; o bucket guarda o payload.
- O score precisa ser explicavel; nao basta um numero.
- O endpoint nao deve carregar segredo fixo de longo prazo.
- A analise deve mirar vazamento de dados sensiveis, nao vigilancia ampla de produtividade.
- O sistema precisa tolerar falhas de rede com fila local e retry.
- O rollout precisa ser repetivel, auditavel e reversivel.

## Arquitetura Logica

### 1. Endpoint Windows

Componentes:

- ShareX corporativo
- Screenshot Agent em Python empacotado para Windows
- servico Windows
- fila local SQLite
- diretorio de spool em `%ProgramData%\\ScreenshotAudit\\spool`
- diretorio de retry em `%ProgramData%\\ScreenshotAudit\\queue`
- logs locais rotacionados

Responsabilidades:

- monitorar a pasta de captura
- aplicar watermark operacional
- coletar metadata minima
- calcular `sha256`
- solicitar autorizacao de ingestao na API
- enviar o arquivo ao storage via URL pre-assinada
- confirmar o evento na API
- apagar temporarios apos sucesso
- manter fila local em caso de falha
- reportar heartbeat e versao do agent

### 2. Backend Central

Componentes:

- API principal em FastAPI
- worker de analise
- PostgreSQL
- storage quente S3-compativel
- fila assicrona para jobs
- painel de auditoria

Responsabilidades:

- autenticar o agent
- emitir upload pre-assinado
- persistir metadata
- disparar analise assicrona
- calcular score e nivel de risco
- registrar revisoes humanas
- manter trilha de auditoria
- expor consultas operacionais e exportacoes

### 3. Operacao e Rollout

Componentes:

- GitHub para versionamento
- Semaphore para execucao e orquestracao
- Ansible para automacao
- WinRM/PSRP para Windows
- inventario por empresa/OU

Responsabilidades:

- instalar ShareX
- instalar e atualizar Agent
- distribuir configuracoes
- executar healthchecks
- auditar hosts fora de compliance
- publicar novas versoes

## Repositorios Recomendados

Separacao inicial sugerida:

- `audit-screenshot-agent`
- `audit-screenshot-backend`
- `audit-screenshot-infra`

Se quiser simplificar no comeco:

- monorepo `audit-screenshot` com pastas `agent/`, `backend/`, `infra/`

## Entrega 1: Agent Windows

### Objetivo

Substituir o MVP local por um agent operacional e resiliente no endpoint.

### Escopo

- empacotar o agent Python
- transformar execucao em servico Windows
- ler configuracao centralizada por arquivo
- observar spool do ShareX com `watchdog`
- processar arquivos com fila SQLite
- aplicar watermark
- calcular `sha256`
- capturar metadata do host e usuario
- integrar com API de ingestao
- suportar retry com backoff
- gerar logs locais

### Estrutura sugerida

`agent/`

- `src/agent/main.py`
- `src/agent/config.py`
- `src/agent/spool_watcher.py`
- `src/agent/queue_store.py`
- `src/agent/watermark.py`
- `src/agent/collector.py`
- `src/agent/api_client.py`
- `src/agent/uploader.py`
- `src/agent/service.py`
- `src/agent/logging_conf.py`
- `tests/`

### Configuracoes do endpoint

Campos minimos:

- `tenant`
- `api_base_url`
- `agent_id`
- `auth_mode`
- `spool_dir`
- `processed_dir`
- `retry_dir`
- `log_dir`
- `watermark_enabled`
- `watermark_logo_path`
- `capture_active_window`
- `delete_local_after_success`
- `max_retry_attempts`

### Metadata minima por evento

- `event_id`
- `tenant`
- `hostname`
- `username`
- `captured_at`
- `local_ip`
- `external_ip` opcional
- `file_name`
- `file_ext`
- `file_size`
- `sha256`
- `agent_version`
- `sharex_profile_version`

### Decisoes importantes

- usar URL pre-assinada em vez de credencial S3 fixa no endpoint
- manter fila local SQLite para evitar perda em queda de rede
- nao depender de `Path.home()` ou caminho do usuario
- operar com `ProgramData`
- separar watermark visual de evidencia hash

### Criterios de aceite

- o agent inicia como servico e sobe automaticamente com o Windows
- um screenshot novo entra na fila e e processado sem intervencao manual
- queda de rede nao perde o evento
- retorno da rede drena a fila com sucesso
- API recebe metadata e confirma o upload
- arquivo local e removido apenas apos confirmacao
- logs mostram causa de falha por evento

### Dependencias de inicio

- validar WinRM/PSRP para rollout
- definir formato de autenticacao do agent
- decidir empacotamento inicial: `PyInstaller` ou `Nuitka`

## Entrega 2: API + Worker + Painel de Auditoria

### Objetivo

Criar o backend que centraliza ingestao, analise, classificacao e revisao humana.

### Escopo

- API de ingestao do agent
- emissao de upload pre-assinado
- persistencia em PostgreSQL
- fila de jobs
- worker de OCR e scoring
- painel inicial para fila de revisao
- trilha de auditoria de acesso e decisao

### Modulos principais

`backend/`

- `app/api/ingest.py`
- `app/api/events.py`
- `app/api/reviews.py`
- `app/api/agents.py`
- `app/services/presign.py`
- `app/services/risk_engine.py`
- `app/services/ocr.py`
- `app/services/entities.py`
- `app/services/policies.py`
- `app/workers/analyze_event.py`
- `app/db/models.py`
- `app/db/migrations/`

### Tabelas iniciais

#### `agents`

- `agent_id`
- `tenant`
- `hostname`
- `status`
- `agent_version`
- `last_seen_at`
- `config_version`

#### `events`

- `event_id`
- `tenant`
- `hostname`
- `username`
- `captured_at`
- `received_at`
- `object_key`
- `sha256`
- `file_size`
- `content_type`
- `status`

#### `event_metadata`

- `event_id`
- `local_ip`
- `external_ip`
- `active_window_title`
- `active_process_name`
- `sharex_profile_version`
- `agent_version`

#### `event_analysis`

- `event_id`
- `ocr_engine`
- `ocr_text_masked`
- `ocr_confidence`
- `risk_score`
- `risk_level`
- `policy_version`
- `analyzed_at`

#### `event_rule_hits`

- `id`
- `event_id`
- `rule_id`
- `rule_name`
- `category`
- `weight`
- `confidence`
- `evidence_masked`

#### `review_queue`

- `event_id`
- `assigned_to`
- `review_status`
- `review_reason`
- `reviewed_at`

#### `access_audit`

- `id`
- `actor`
- `action`
- `resource_type`
- `resource_id`
- `created_at`

### Motor de scoring

Primeira versao orientada a regras:

- OCR
- regex para dados estruturados
- dicionarios internos
- regras de contexto
- pesos por severidade
- score final explicavel

Exemplos de categorias:

- credenciais e segredos
- dados pessoais
- dados financeiros
- dados de clientes
- topologia e infraestrutura
- sistemas internos sensiveis
- presenca em canais de compartilhamento

Formula sugerida:

- `score = soma de pesos de evidencias * fator de contexto * fator de confianca`

Niveis iniciais:

- `baixo`: somente registrar
- `medio`: fila de revisao humana
- `alto`: fila prioritaria e alerta

### Regras de privacidade operacional

- nao indexar integralmente o texto de todos os eventos de baixo risco
- mascarar evidencias persistidas quando possivel
- mostrar no painel apenas o necessario para revisao
- registrar acesso ao evento e a imagem

### Criterios de aceite

- agent consegue registrar evento e receber URL pre-assinada
- upload e confirmacao persistem o evento com integridade
- worker analisa e classifica eventos
- painel lista medio/alto com justificativa do score
- revisao humana altera o status do evento
- trilha de auditoria registra acesso e decisao

## Entrega 3: Infra, CI/CD e Rollout

### Objetivo

Operacionalizar a plataforma de ponta a ponta usando a infra ja existente.

### Escopo

- repositorios no GitHub
- pipeline de build/test
- deploy do backend
- inventario Windows por empresa
- playbooks de install/update/healthcheck
- templates no Semaphore
- politicas de retencao e arquivamento

### Estrutura sugerida

`infra/`

- `ansible/inventories/`
- `ansible/group_vars/`
- `ansible/roles/sharex_install/`
- `ansible/roles/agent_install/`
- `ansible/roles/agent_config/`
- `ansible/roles/agent_healthcheck/`
- `ansible/playbooks/install_sharex.yml`
- `ansible/playbooks/install_agent.yml`
- `ansible/playbooks/update_agent.yml`
- `ansible/playbooks/healthcheck_agent.yml`
- `docker/backend-compose.yml`
- `docker/worker-compose.yml`
- `docker/observability-compose.yml`

### Inventory

Sugestao de grupos:

- `fiber_windows`
- `intlink_windows`
- `clickip_windows`
- `wire_windows`
- `pilot_group`

### Templates no Semaphore

- `install_sharex`
- `install_agent`
- `update_agent`
- `rotate_config`
- `healthcheck_agent`
- `collect_logs`
- `rollback_agent`

### Storage quente e frio

Modelo sugerido:

- storage quente: objetos individuais para operacao
- arquivamento frio: lotes diarios por empresa/data

Prefixo sugerido:

- `screenshots-hot/<tenant>/<yyyy>/<mm>/<dd>/<hostname>/<event_id>.jpg`

Pacote frio sugerido:

- `archive/<tenant>/<yyyy>/<mm>/<dd>/batch_<hhmm>.tar.zst`
- `archive/<tenant>/<yyyy>/<mm>/<dd>/manifest.ndjson`

### Retencao

- quente: 30 dias
- frio: indefinido ou conforme politica juridica
- revisao/manual: conforme SLA interno

### Observabilidade

Metricas minimas:

- eventos ingeridos por minuto
- fila local por host
- falhas de upload
- tempo de analise
- distribuicao de risco
- hosts sem heartbeat

Logs minimos:

- log do agent por host
- log de API
- log de worker
- log de acesso ao painel

### Criterios de aceite

- backend sobe de forma reproduzivel em ambiente Docker
- pipeline publica versao nova com seguranca
- rollout em lote funciona via Semaphore
- playbooks conseguem instalar e atualizar endpoints
- healthcheck identifica hosts fora de conformidade
- retencao e arquivamento executam como planejado

## Ordem Recomendada de Execucao

### Fase 0 - Preparacao

- definir repositorio ou monorepo
- definir autenticacao do agent
- definir storage quente definitivo
- validar WinRM/PSRP em piloto

### Fase 1 - Entrega 1

- endurecer o MVP para virar agent
- testar em 1 host piloto
- depois ampliar para 5 a 10 hosts

### Fase 2 - Entrega 2

- subir API basica
- integrar presign + confirmacao
- ativar worker com OCR e score inicial

### Fase 3 - Entrega 3

- publicar backend em ambiente gerenciado
- criar playbooks e templates
- expandir rollout por empresa

## Riscos e Mitigacoes

- WinRM instavel ou mal configurado
  - mitigar com piloto pequeno, Kerberos primeiro e playbooks simples

- OCR gerar muito falso positivo
  - mitigar com fase inicial baseada em poucas regras de alto valor

- volume alto de imagens
  - mitigar com empacotamento diario para a camada fria e retencao curta no quente

- excesso de invasividade operacional
  - mitigar com escopo restrito a dados sensiveis e persistencia mascarada

- falhas de rede nos endpoints
  - mitigar com fila local, retry e heartbeat

## Proximo Passo Pratico

Assim que o WinRM estiver validado, a primeira entrega deve comecar por este recorte:

1. Agent CLI funcionando localmente sem servico
2. fila SQLite + watcher + watermark + hash
3. contrato HTTP com API fake
4. empacotamento para Windows
5. instalacao piloto via WinRM/Semaphore

## Definicao de Pronto do MVP de Producao

O projeto entra em piloto real quando:

- 1 grupo pequeno de hosts instala o agent por automacao
- os eventos chegam com hash e metadata consistentes
- o backend classifica pelo menos baixo/medio/alto com justificativa
- a fila de revisao funciona
- o fluxo de retry e resiliente a falha de rede
- a retencao quente e o arquivamento frio estao operacionais

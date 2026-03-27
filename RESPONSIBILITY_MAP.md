# Responsibility Map

## Resposta curta

Este projeto tem duas camadas diferentes:

- `plano de controle`
- `plano de dados`

Misturar as duas e o que costuma gerar confusao.

## 1. Plano de controle

Responsavel por instalar, atualizar, reiniciar, validar e diagnosticar os hosts.

Componentes:

- `Semaphore UI`
- `Ansible`
- `WinRM`

### O que cada um faz

#### Semaphore UI

- dispara jobs
- guarda historico de execucao
- mostra sucesso/falha por host
- mostra stdout/stderr das tarefas
- organiza templates, inventarios e credenciais

#### Ansible

- executa a automacao
- copia binarios e configs
- instala ShareX
- instala ou atualiza o agent
- reinicia servico
- roda healthcheck
- coleta logs sob demanda

#### WinRM

- e o canal remoto usado pelo Ansible para entrar nos Windows

## 2. Plano de dados

Responsavel pelo processamento real dos screenshots e pela telemetria do produto.

Componentes:

- `ShareX`
- `Agent Windows`
- `SQLite local`
- `MinIO`
- `API`
- `PostgreSQL`
- `Redis`
- `Duplicati`

### O que cada um faz

#### ShareX

- tira o screenshot
- salva no spool local

#### Agent Windows

- roda como servico
- observa o spool
- gera watermark
- coleta metadata
- grava fila local no SQLite
- faz retry
- envia para o MinIO
- fala com a API
- envia heartbeat e status do endpoint

#### SQLite local

- fila duravel do host
- pendencias de retry
- ultimo erro local

Nao e banco central do projeto.

#### MinIO

- guarda as imagens e objetos quentes

#### API

- recebe confirmacoes do agent
- registra metadata oficial
- recebe heartbeat
- expoe status centralizado dos endpoints

#### PostgreSQL

- banco oficial da plataforma
- eventos
- revisoes
- auditoria
- heartbeats
- estado consolidado dos endpoints

#### Redis

- fila/cache do backend central
- OCR
- scoring
- jobs futuros

#### Duplicati

- backup frio
- export de lotes do MinIO para Google Drive

## O que o Ansible nao deve fazer no dia a dia

- nao deve processar screenshots
- nao deve ficar lendo spool continuamente
- nao deve ser a fonte oficial das metricas do produto
- nao deve manter o estado operacional de cada print

## O que o Agent nao deve fazer

- nao deve depender do Ansible para cada screenshot
- nao deve depender de WinRM para funcionar
- nao deve gravar a auditoria oficial so localmente

## Onde fica o versionamento do agent

O versionamento do agent fica assim:

1. voces geram uma release do agent
2. o artefato tem uma versao
3. o Semaphore/Ansible distribui essa versao para os hosts
4. o agent informa a propria versao para a API via heartbeat

Entao:

- `Ansible` distribui versao
- `Agent` reporta versao
- `API/Postgres` consolidam versao por host

## Onde fica o status dos hosts

Tem dois niveis de status:

### Status operacional do rollout

Fica no `Semaphore`:

- install deu certo?
- update falhou?
- qual host falhou?
- qual tarefa falhou?

### Status funcional do produto

Fica na `API/Postgres`:

- agent online ou offline
- ultima ingestao
- fila local estimada
- ultimo heartbeat
- ultima falha
- versao do agent

## Resumo final

- `Semaphore + Ansible + WinRM` = operacao dos hosts
- `Agent + API + Postgres + MinIO` = funcionamento do produto
- `Redis` = backend assincrono futuro
- `Duplicati` = arquivamento frio

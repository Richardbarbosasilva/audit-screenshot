# Semaphore Rollout Runbook

## Resposta curta

Se a sua direcao e substituir `GPMC + scripts em share SMB` por `Semaphore UI + Ansible + WinRM`, entao esse deve ser o desenho principal desde ja.

Nesse modelo:

- `MSI` ou `EXE` = formato de pacote
- `WinRM` = canal de execucao remota
- `Ansible` = automacao declarativa
- `Semaphore UI` = orquestracao, historico, logs e visibilidade por host
- `Agent Windows` = componente que fica rodando continuamente no endpoint

Ou seja: `MSI` nao substitui `Semaphore`, e `Semaphore` nao substitui o `agent`.

## Onde cada peca entra

### Fluxo operacional da midia

1. Usuario tira screenshot no ShareX.
2. ShareX salva no spool local.
3. Agent Windows detecta.
4. Agent aplica watermark.
5. Agent registra estado no SQLite local.
6. Agent envia para o MinIO.
7. Depois, a camada central faz analise, indexacao e backup frio.

### Fluxo de operacao

1. Semaphore dispara um job.
2. O job chama um playbook Ansible.
3. O Ansible conecta por WinRM.
4. O playbook instala/atualiza ShareX, agent, config ou servico.
5. O Semaphore mostra resultado por host: sucesso, falha, stdout/stderr e horario.

Entao o `Semaphore UI + Ansible + WinRM` entra no fluxo de operacao, nao no fluxo do screenshot.

## Por que eu nao usaria GPO como base permanente

- voce ja quer tirar a dependencia operacional de `share SMB + scripts soltos`
- logs e historico no `Semaphore` ficam muito melhores
- rollout gradual, retry e controle por host ficam mais claros
- fica mais alinhado com futuras automacoes alem do screenshot

## Onde a GPO ainda pode entrar

Somente como bootstrap minimo, se necessario:

- habilitar WinRM
- ajustar firewall
- eventualmente instalar certificado base
- eventualmente publicar um atalho ou registry basico

Mas o rollout continuo eu colocaria no `Semaphore`.

## MSI agora ou depois

### O que o MSI resolve

- instalacao padronizada
- uninstall formal
- upgrade versionado
- integracao limpa com inventario de software

### O que o MSI nao resolve

- orquestracao
- logs centralizados
- visibilidade por host
- instalacao do ShareX, que continua vindo como `EXE`
- healthcheck e coleta de diagnostico

### Recomendacao pratica

Para o piloto:

- `ShareX`: instalar como `EXE` silencioso via Ansible
- `Agent`: instalar como `EXE` do `PyInstaller` via Ansible
- `NSSM`: registrar o servico via Ansible

Depois que o agent estabilizar:

- gerar `MSI` proprio do agent com `WiX`
- continuar distribuindo esse MSI pelo `Semaphore`, usando `Ansible + WinRM`

Entao o MSI pode entrar, mas como empacotamento, nao como plataforma de rollout.

## O desenho que eu recomendo para o seu lab

### Fase 1

- OU `sharex` no AD apenas para escopo organizacional
- WinRM validado nos 2 Windows 11 e no Windows Server
- Semaphore com templates separados:
  - `install_sharex`
  - `install_agent`
  - `update_agent_config`
  - `restart_agent`
  - `healthcheck_agent`
  - `collect_agent_logs`

### Fase 2

- Agent já populando MinIO
- Duplicati ainda opcional
- backend minimo depois

### Fase 3

- API + worker + Redis dedicado da plataforma
- OCR, scoring e painel

## Como ter visibilidade por host no Semaphore

Cada template no Semaphore aponta para:

- um inventario
- um repositório
- um playbook

O output do Ansible já sai por host. Exemplo:

- `HOSTTESTE : ok=12 changed=3 failed=0`
- `HOST-TEST2 : ok=10 changed=2 failed=1`

Na pratica, a sua visao fica assim:

- qual template rodou
- quando rodou
- em quais hosts
- qual host falhou
- qual tarefa falhou
- stdout/stderr da tarefa

Para melhorar isso, os playbooks podem:

- usar `register`
- imprimir versao instalada
- consultar status do servico
- ler ultimas linhas do log

## Redis para este projeto

### Hoje

Para o agent de screenshot: `nao e necessario`.

O retry do endpoint deve continuar em `SQLite local`.

### Depois

Para o backend central:

- `Redis dedicado` faz sentido sim
- principalmente se voces forem usar fila para `OCR`, `scoring`, `rules`, `URL audit` e jobs assincronos

### Recomendacao

Nao reaproveitar o `NEXTCLOUD-REDIS` como base oficial desta plataforma.

Melhor criar algo como:

- `REDIS-AUDIT`
- database e senha proprios
- volume proprio

`RedisInsight` e opcional, mas util em laboratorio. Eu usaria para debug, nao como dependencia do produto.

## Duplicati no fluxo

O `Duplicati` nao precisa existir para comecar o piloto do agent.

O fluxo pode ser:

1. Agent sobe no MinIO
2. Depois criamos rotina de export do quente para lote local
3. Duplicati envia esse lote para Google Drive

Entao:

- `ShareX + Agent + MinIO` = primeira meta operacional
- `Duplicati` = camada seguinte
- `backend + Redis + painel` = camada seguinte

## Resumo objetivo

- se a sua estrategia e `Semaphore + Ansible + WinRM`, eu seguiria nela
- GPO fica no maximo como bootstrap auxiliar
- MSI pode existir, mas nao e o centro da arquitetura
- para o piloto, `EXE + Ansible + NSSM` e mais rapido
- quando estabilizar, encapsula o agent em `MSI`, ainda distribuido por `Semaphore`

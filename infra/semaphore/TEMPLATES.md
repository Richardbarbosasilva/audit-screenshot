# Semaphore Templates

## Project suggestion

Crie um projeto no Semaphore chamado:

- `screenshot-audit`

## Inventories

- `sharex-pilot`
- depois: `sharex-clickip`, `sharex-fiber`, `sharex-intlink`

## Environment

Variaveis comuns:

- `ANSIBLE_HOST_KEY_CHECKING=False`
- `PYTHONUNBUFFERED=1`

Credenciais:

- usuario WinRM
- senha WinRM

## Templates iniciais

### 1. win_ping

- inventory: `sharex-pilot`
- playbook: `infra/ansible/playbooks/win_ping.yml`

### 2. install_sharex

- inventory: `sharex-pilot`
- playbook: `infra/ansible/playbooks/install_sharex.yml`

### 3. install_agent

- inventory: `sharex-pilot`
- playbook: `infra/ansible/playbooks/install_agent.yml`

### 4. healthcheck_agent

- inventory: `sharex-pilot`
- playbook: `infra/ansible/playbooks/healthcheck_agent.yml`

## Como isso aparece no UI

Cada execução mostra:

- status geral
- duração
- usuário que disparou
- output por tarefa
- falha por host
- resumo final do Ansible

## Estratégia de rollout

No piloto:

- `serial: 1`

Depois:

- grupos por empresa
- rollout por lote
- healthcheck após deploy
- rollback se necessário

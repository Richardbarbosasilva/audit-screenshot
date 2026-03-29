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
- comportamento: resumo por host sem derrubar a tarefa inteira por um unico host inacessivel

### 2. install_sharex

- inventory: `sharex-pilot`
- playbook: `infra/ansible/playbooks/install_sharex.yml`
- canario pronto: `infra/ansible/playbooks/install_sharex_canary.yml`

### 3. install_agent

- inventory: `sharex-pilot`
- playbook: `infra/ansible/playbooks/install_agent.yml`
- canario pronto: `infra/ansible/playbooks/install_agent_canary.yml`

### 4. configure_sharex_spool

- inventory: `sharex-pilot`
- playbook: `infra/ansible/playbooks/configure_sharex_spool.yml`
- canario pronto: `infra/ansible/playbooks/configure_sharex_spool_canary.yml`

### 5. uninstall_lightshot

- inventory: `sharex-pilot`
- playbook: `infra/ansible/playbooks/uninstall_lightshot.yml`
- canario pronto: `infra/ansible/playbooks/uninstall_lightshot_canary.yml`

### 6. healthcheck_agent

- inventory: `sharex-pilot`
- playbook: `infra/ansible/playbooks/healthcheck_agent.yml`
- canario pronto: `infra/ansible/playbooks/healthcheck_agent_canary.yml`

## Como isso aparece no UI

Cada execução mostra:

- status geral
- duração
- usuário que disparou
- output por tarefa
- falha por host
- resumo final do Ansible

## Limites úteis no piloto

- `HOST-TEST2`: seguir com o canário funcional enquanto fechamos o auth do `HOSTTESTE`
- `HOSTTESTE`: isolar o host que ainda precisa do caminho Kerberos no executor Linux

## Estratégia de rollout

No piloto:

- `serial: 1`

Depois:

- grupos por empresa
- rollout por lote
- healthcheck após deploy
- rollback se necessário

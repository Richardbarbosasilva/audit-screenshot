# Screenshot Audit

Módulo raiz da V1 no repositório operacional do LeakGuard.

## Responsabilidade

- agent de captura
- integração com ShareX
- spool local
- instalação/atualização via Ansible
- healthcheck do agent

## Implementação atual

Ainda distribuída no root do repositório em arquivos como:

- `mock_watermark.py`
- `agent_config.json`
- `install_agent_service.ps1`
- `gpo_install_agent.ps1`
- `gpo_install_sharex.ps1`
- `infra/ansible/playbooks/install_agent.yml`
- `infra/ansible/playbooks/configure_sharex_spool.yml`

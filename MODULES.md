# Módulos do LeakGuard Infra/Agent

## Estrutura alvo

O repositório operacional do LeakGuard também passa a refletir a divisão por módulos.

Módulos raiz:

- `modules/screenshot-audit`
- `modules/web-browser-audit`
- `modules/logical-hygiene`
- `modules/shared-platform`

## Estado da V1

Na V1, o módulo ativo é `screenshot-audit`.

Os artefatos atuais ainda vivem principalmente no root por compatibilidade:

- scripts PowerShell
- binários
- configuração do agent
- playbooks e runbooks

Os diretórios em `modules/...` passam a ser a referência de ownership e evolução futura.

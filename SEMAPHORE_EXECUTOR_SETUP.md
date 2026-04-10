# Semaphore Executor Setup

## Estado atual

O container atual do Semaphore nao tem:

- `ansible`
- `pypsrp`
- `pywinrm`
- collections `ansible.windows` e `community.windows`
- toolchain Kerberos para hosts de dominio

Sem isso, o `win_ping` pelo UI nao vai funcionar ainda.

## Objetivo

Gerar uma imagem do Semaphore com o ambiente Ansible necessario para operar Windows via WinRM/PSRP e Kerberos.

## Arquivos prontos no projeto

- `infra/ansible/requirements.txt`
- `infra/ansible/collections/requirements.yml`
- `infra/docker/Dockerfile.semaphore-ansible`
- `infra/docker/krb5.conf`

## Build sugerido

No host Debian:

```bash
cd /var/www/leakguard
sudo docker build -f infra/docker/Dockerfile.semaphore-ansible -t local/semaphore-overview:ansible-v1 .
```

## Proximo passo

Depois, ajuste o compose do Semaphore para usar:

- `local/semaphore-overview:ansible-v1`

E recrie o container:

```bash
docker compose up -d --force-recreate semaphore
```

## Validacao

Dentro do container novo, estes comandos devem funcionar:

```bash
ansible --version
python3 -c "import pypsrp, winrm, kerberos"
kinit --version
ansible-galaxy collection list
```

## Ordem recomendada apos o rebuild

1. Criar projeto `leakguard` no Semaphore
2. Criar inventory `sharex-pilot`
3. Criar environment com `ansible_password`
4. Cadastrar o secret/extra var `leakguard_agent_api_bearer_token`
5. Apontar o repositório Git atualizado do `Leakguard`
6. Rodar template `win_ping`
7. Se passar, rodar `install_sharex`
8. Depois `install_agent`
9. Depois `healthcheck_agent`

Observacoes:

- o nome do grupo de variaveis no Semaphore pode ser livre
- a chave interna do secret deve ser exatamente `leakguard_agent_api_bearer_token`
- `install_agent_canary` e `healthcheck_agent_canary` rodam somente no `HOST-TEST2`

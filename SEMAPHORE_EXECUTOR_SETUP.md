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
cd /var/www/audit_screenshot
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

1. Criar projeto `screenshot-audit` no Semaphore
2. Criar inventory `sharex-pilot`
3. Criar environment com `ansible_password`
4. Apontar o repositório local ou Git
5. Rodar template `win_ping`
6. Se passar, rodar `install_sharex`
7. Depois `install_agent`
8. Depois `healthcheck_agent`

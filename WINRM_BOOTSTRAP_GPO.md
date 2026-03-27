# WinRM Bootstrap GPO

## Objetivo

Habilitar `WinRM` nos Windows 11 do piloto para que o `Semaphore + Ansible` consigam operar os hosts.

## Resposta curta

Sim, para Windows 11 cliente eu trataria `WinRM` como algo que precisa ser explicitamente habilitado no piloto.

Se voce quer evitar que `GPO` vire o mecanismo principal do projeto, use a GPO somente para este bootstrap inicial:

- habilitar WinRM
- abrir firewall
- garantir o servico automatico

Depois disso:

- install/update/healthcheck vao pelo `Semaphore`

## Escopo recomendado da GPO

Linke a GPO apenas na OU:

- `sharex`

## O que a GPO deve fazer

1. Executar um script de startup
2. Rodar `Enable-PSRemoting -Force`
3. Garantir `WinRM` como automatico
4. Abrir as regras de firewall do WinRM
5. Validar `Test-WsMan localhost`

## Caminho sugerido

Use um startup script apontando para:

- `winrm_bootstrap.ps1`

## Depois do reboot

Valide com:

- `Test-WsMan localhost` no proprio Windows
- `ansible.windows.win_ping` a partir do Semaphore/Ansible

## O que nao fazer agora

- nao usar GPO para instalar continuamente ShareX e agent se a sua meta e centralizar no Semaphore
- nao usar `TrustedHosts` se o ambiente de dominio resolver via Kerberos
- nao misturar isso com deploy da aplicacao ainda

# WinRM Pilot Checklist

## Objetivo

Validar a conectividade WinRM/PSRP entre o servidor Debian e as VMs Windows antes do rollout do agent.

## 1. Preparar cada host Windows

Rode PowerShell como administrador:

```powershell
Enable-PSRemoting -Force
Set-Service WinRM -StartupType Automatic
Start-Service WinRM
winrm quickconfig -quiet
```

## 2. Ajustes de laboratorio

Se o ambiente nao estiver usando Kerberos plenamente, para piloto de lab voce pode usar NTLM e `TrustedHosts`.

No host Windows que vai aceitar administracao remota:

```powershell
Set-Item WSMan:\localhost\Service\Auth\Kerberos $true
Set-Item WSMan:\localhost\Service\Auth\Negotiate $true
Set-Item WSMan:\localhost\Service\Auth\NTLM $true
```

No cliente ou no servidor que vai iniciar conexoes:

```powershell
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "HOST1,HOST2,HOST3" -Force
```

## 3. Portas

Para o piloto, valide:

- `5985/tcp` para HTTP
- `5986/tcp` para HTTPS se voces forem endurecer depois

## 4. Teste local no proprio Windows

```powershell
Test-WsMan
```

Teste para outro host:

```powershell
Test-WsMan NOME-OU-IP-DO-HOST
```

## 5. Teste a partir do Debian com Ansible

Instale o minimo:

```bash
python3 -m pip install --user pywinrm pypsrp
ansible-galaxy collection install ansible.windows
ansible-galaxy collection install community.windows
```

Exemplo de inventario inicial:

```ini
[pilot]
win11-client-01 ansible_host=192.168.1.10
win11-client-02 ansible_host=192.168.1.11
win-server-01 ansible_host=192.168.1.20

[pilot:vars]
ansible_connection=psrp
ansible_user=LAB\\Administrator
ansible_password=CHANGE_ME
ansible_psrp_auth=ntlm
ansible_port=5985
ansible_psrp_cert_validation=ignore
```

Teste de conectividade:

```bash
ansible pilot -i inventory.ini -m ansible.windows.win_ping
```

## 6. O que validar antes de seguir

- `win_ping` responde nos 3 hosts Windows
- servico `WinRM` fica automatico
- firewall nao bloqueia 5985
- credenciais funcionam sem login interativo
- hostname e DNS resolvem corretamente

## 7. Onde o WinRM entra no projeto

Use WinRM para:

- instalar ShareX
- copiar o agent
- instalar ou reiniciar o servico
- trocar `agent_config.json`
- coletar logs
- fazer healthcheck

Nao use WinRM para ficar puxando screenshots continuamente.

# GPO Pilot Runbook

## Resposta curta

Sim, o primeiro passo certo no lab e simular o rollout em massa.

Se a decisao estrategica for usar `Semaphore UI + Ansible + WinRM` como plano de controle principal, trate este documento como fallback ou bootstrap auxiliar, nao como arquitetura-alvo.

Mas eu nao comecaria por MSI customizado. Para este piloto, o caminho mais seguro e:

1. empacotar o agent em `exe` com `PyInstaller`
2. distribuir `ShareX` e agent por `GPO Startup Script`
3. instalar o agent como servico com `NSSM`
4. so depois, quando o layout estiver estavel, decidir se vale gerar um MSI proprio

## Por que nao travar em MSI agora

- `GPO Software Installation` trabalha melhor com `MSI`
- o `ShareX-19.0.2-setup.exe` que voce deixou no lab e um instalador `Inno Setup`
- o agent ainda esta em fase de piloto, entao mudar binario, config e layout ainda vai ser comum
- script de startup via GPO resolve os dois lados agora: `ShareX` e agent

## Estrategia recomendada para o lab

Crie uma OU piloto para os 2 Windows 11.

Exemplo:

- `OU=ScreenshotAudit-Pilot`

Crie uma share de software no dominio, por exemplo:

- `\\LAB-DC\Software$\audit-screenshot`

Sugestao de estrutura:

- `\\LAB-DC\Software$\audit-screenshot\ShareX-19.0.2-setup.exe`
- `\\LAB-DC\Software$\audit-screenshot\agent\ScreenshotAuditAgent.exe`
- `\\LAB-DC\Software$\audit-screenshot\agent\agent_config.json`
- `\\LAB-DC\Software$\audit-screenshot\agent\logo.png`
- `\\LAB-DC\Software$\audit-screenshot\tools\nssm.exe`
- `\\LAB-DC\Software$\audit-screenshot\scripts\gpo_install_sharex.ps1`
- `\\LAB-DC\Software$\audit-screenshot\scripts\gpo_install_agent.ps1`
- `\\LAB-DC\Software$\audit-screenshot\scripts\gpo_bootstrap_workstation.ps1`
- `\\LAB-DC\Software$\audit-screenshot\scripts\install_agent_service.ps1`

Permissoes minimas:

- leitura para `Domain Computers`
- escrita apenas para administradores

## O que a GPO vai fazer

No startup da maquina:

1. instalar ou atualizar o `ShareX` em modo silencioso
2. copiar binario do agent, config e logo
3. copiar `nssm.exe`
4. registrar ou atualizar o servico `ScreenshotAuditAgent`
5. iniciar o servico

## Como vincular a GPO

Use:

- `Computer Configuration`
- `Policies`
- `Windows Settings`
- `Scripts (Startup/Shutdown)`
- `Startup`

Chame:

- `powershell.exe -ExecutionPolicy Bypass -File \\LAB-DC\Software$\audit-screenshot\scripts\gpo_bootstrap_workstation.ps1`

## Sobre o ShareX

Como o instalador e `Inno Setup`, o modo silencioso esperado para piloto e:

- `/VERYSILENT`
- `/SUPPRESSMSGBOXES`
- `/NORESTART`
- `/SP-`
- `/NORUN`
- `/UPDATE`

Depois da instalacao, voces podem endurecer a configuracao via GPO Registry Preferences usando:

- `HKLM\SOFTWARE\ShareX\PersonalPath`

Isso permite tirar o caminho pessoal do ShareX de `Documents` e apontar para uma pasta controlada do endpoint.

## Ordem pratica que eu recomendo

1. Preparar a share no controlador de dominio
2. Gerar o `ScreenshotAuditAgent.exe`
3. Fechar `agent_config.json` com MinIO e IPs reais
4. Colocar tudo na share
5. Criar a OU piloto
6. Linkar a GPO so nos 2 Windows 11
7. Rodar `gpupdate /force`
8. Reiniciar as maquinas piloto
9. Validar `ShareX`, servico do agent e upload no bucket certo

## Quando vale MSI

Eu deixaria MSI para a segunda volta, quando:

- o agent estiver estavel
- o layout de arquivos nao estiver mais mudando
- a instalacao silenciosa ja estiver validada
- voces quiserem uninstall e upgrade formais

Se quiser, depois do piloto eu monto tambem o desenho do MSI do agent com `WiX`.

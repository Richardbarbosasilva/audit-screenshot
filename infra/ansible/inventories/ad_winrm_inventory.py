#!/usr/bin/env python3
"""Dynamic Ansible inventory that queries AD via WinRM PowerShell.

Bypasses LDAP signing requirements by using WinRM (which Ansible already uses)
to run Get-ADComputer on the domain controller.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def load_config() -> dict:
    config_path = Path(
        os.environ.get(
            "LEAKGUARD_AD_INVENTORY_CONFIG",
            Path(__file__).with_name("ad_winrm_inventory.json"),
        )
    )
    if not config_path.exists():
        raise SystemExit(f"Config not found: {config_path}")
    return json.loads(config_path.read_text(encoding="utf-8"))


def query_ad_computers(config: dict) -> list[dict]:
    try:
        import winrm  # type: ignore
    except ImportError:
        raise SystemExit("pywinrm is not installed")

    dc = config["domain_controller"]
    password = os.environ.get(
        config.get("password_env", "LEAKGUARD_AD_BIND_PASSWORD"), ""
    )
    if not password:
        raise SystemExit(
            f"Password env {config.get('password_env', 'LEAKGUARD_AD_BIND_PASSWORD')} not set"
        )

    session = winrm.Session(
        f"http://{dc['host']}:{dc.get('port', 5985)}/wsman",
        auth=(dc["user"], password),
        transport=dc.get("transport", "ntlm"),
        server_cert_validation="ignore",
    )

    results = []
    for group in config.get("groups", []):
        search_base = group["search_base"]
        ldap_filter = group.get(
            "ldap_filter",
            "(&(objectClass=computer)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))",
        )
        ps_script = (
            f"$searcher = New-Object DirectoryServices.DirectorySearcher; "
            f"$searcher.SearchRoot = New-Object DirectoryServices.DirectoryEntry('LDAP://{search_base}'); "
            f"$searcher.Filter = '{ldap_filter}'; "
            f"$searcher.SearchScope = 'Subtree'; "
            f"@('name','dNSHostName','operatingSystem') | ForEach-Object {{ $searcher.PropertiesToLoad.Add($_) | Out-Null }}; "
            f"$results = $searcher.FindAll(); "
            f"$list = @(); "
            f"foreach ($r in $results) {{ "
            f"  $p = $r.Properties; "
            f"  $list += @{{ "
            f"    Name = [string]($p['name'][0]); "
            f"    DNSHostName = if ($p['dnshostname'].Count -gt 0) {{ [string]$p['dnshostname'][0] }} else {{ '' }}; "
            f"    OperatingSystem = if ($p['operatingsystem'].Count -gt 0) {{ [string]$p['operatingsystem'][0] }} else {{ '' }} "
            f"  }} "
            f"}}; "
            f"$list | ConvertTo-Json -Compress"
        )

        result = session.run_ps(ps_script)
        if result.status_code != 0:
            stderr = result.std_err.decode("utf-8", errors="replace")
            raise SystemExit(f"PowerShell error: {stderr}")

        stdout = result.std_out.decode("utf-8").strip()
        if not stdout:
            continue

        computers = json.loads(stdout)
        if isinstance(computers, dict):
            computers = [computers]

        for computer in computers:
            results.append({
                "group": group["name"],
                "name": computer.get("Name", ""),
                "dns_hostname": computer.get("DNSHostName", ""),
                "os": computer.get("OperatingSystem", ""),
                "vars": group.get("vars", {}),
            })

    return results


def build_inventory(config: dict) -> dict:
    computers = query_ad_computers(config)
    inventory = {"_meta": {"hostvars": {}}}

    for computer in computers:
        group_name = computer["group"]
        hostname = computer["name"]
        fqdn = computer["dns_hostname"] or hostname

        if group_name not in inventory:
            inventory[group_name] = {"hosts": [], "vars": computer["vars"]}

        inventory[group_name]["hosts"].append(hostname)
        inventory["_meta"]["hostvars"][hostname] = {
            "ansible_host": fqdn,
            "ansible_winrm_kerberos_hostname_override": fqdn,
            "ad_operating_system": computer["os"],
        }

    return inventory


def main():
    config = load_config()
    inventory = build_inventory(config)

    if "--host" in sys.argv:
        try:
            host = sys.argv[sys.argv.index("--host") + 1]
        except Exception:
            host = ""
        print(json.dumps(inventory["_meta"]["hostvars"].get(host, {}), indent=2))
        return

    print(json.dumps(inventory, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path


def _load_ldap3():
    try:
        from ldap3 import ALL, SUBTREE, Connection, Server  # type: ignore
    except Exception as exc:  # pragma: no cover - runtime guidance only
        raise SystemExit(
            "ldap3 nao esta instalado no executor do inventario dinamico. "
            "Instale com `pip install ldap3` no ambiente do Semaphore/runner."
        ) from exc
    return ALL, SUBTREE, Connection, Server


def load_config() -> dict:
    config_path = Path(
        os.environ.get(
            "LEAKGUARD_AD_INVENTORY_CONFIG",
            Path(__file__).with_name("ad_ou_inventory.json"),
        )
    )
    if not config_path.exists():
        raise SystemExit(
            f"Arquivo de configuracao do inventario dinamico nao encontrado: {config_path}"
        )
    return json.loads(config_path.read_text(encoding="utf-8"))


def _ensure_list(value):
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _get_first(entry: dict, key: str, default=""):
    value = entry.get(key, default)
    if isinstance(value, list):
        return value[0] if value else default
    return value if value is not None else default


def build_inventory(config: dict) -> dict:
    ALL, SUBTREE, Connection, Server = _load_ldap3()

    bind_password = os.environ.get(
        config.get("bind_password_env", "LEAKGUARD_AD_BIND_PASSWORD"), ""
    )
    if not bind_password:
        raise SystemExit(
            "Senha de bind do AD ausente. Defina a env "
            f"{config.get('bind_password_env', 'LEAKGUARD_AD_BIND_PASSWORD')}."
        )

    server = Server(
        config["server"],
        port=int(config.get("port", 389)),
        use_ssl=bool(config.get("use_ssl", False)),
        get_info=ALL,
    )
    conn = Connection(
        server,
        user=config["bind_user"],
        password=bind_password,
        auto_bind=True,
        receive_timeout=int(config.get("receive_timeout_seconds", 20)),
    )

    inventory = {"_meta": {"hostvars": {}}}
    computer_name_attr = config.get("computer_name_attr", "name")
    host_attr = config.get("host_attr", "dNSHostName")
    disabled_bit = "1.2.840.113556.1.4.803"

    default_filter = (
        f"(&(objectClass=computer)(!(userAccountControl:{disabled_bit}:=2)))"
    )

    for group in config.get("groups", []):
        group_name = group["name"]
        search_base = group["search_base"]
        ldap_filter = group.get("ldap_filter", default_filter)
        attributes = list(
            {
                computer_name_attr,
                host_attr,
                "distinguishedName",
                "operatingSystem",
                *group.get("attributes", []),
            }
        )

        conn.search(
            search_base=search_base,
            search_filter=ldap_filter,
            search_scope=SUBTREE,
            attributes=attributes,
        )

        inventory[group_name] = {"hosts": [], "vars": group.get("vars", {})}

        for entry in conn.entries:
            data = entry.entry_attributes_as_dict
            hostname = _get_first(data, computer_name_attr, "")
            if not hostname:
                continue

            fqdn = _get_first(data, host_attr, hostname)
            ansible_host = fqdn or hostname
            inventory[group_name]["hosts"].append(hostname)

            hostvars = {
                "ansible_host": ansible_host,
                "ad_dn": _get_first(data, "distinguishedName", ""),
                "ad_operating_system": _get_first(data, "operatingSystem", ""),
            }

            kerberos_override = (
                group.get("kerberos_hostname_override_attr")
                or config.get("kerberos_hostname_override_attr")
            )
            if kerberos_override:
                hostvars["ansible_winrm_kerberos_hostname_override"] = _get_first(
                    data, kerberos_override, ansible_host
                )
            elif fqdn:
                hostvars["ansible_winrm_kerberos_hostname_override"] = fqdn

            for attr_name in _ensure_list(group.get("pass_through_attributes")):
                hostvars[attr_name] = _get_first(data, attr_name, "")

            inventory["_meta"]["hostvars"][hostname] = {
                **inventory["_meta"]["hostvars"].get(hostname, {}),
                **hostvars,
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

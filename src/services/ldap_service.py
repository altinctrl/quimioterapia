import os
import json
from pathlib import Path

from ldap3 import Server, Connection, ALL, SUBTREE
from dotenv import load_dotenv

load_dotenv()


def load_group_mapping():
    env_path = os.getenv("ROLES_MAP_PATH")
    if env_path:
        file_path = Path(env_path)
    else:
        base_path = Path(__file__).resolve().parent.parent
        file_path = base_path / "roles_map.json"

    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar mapa de roles: {e}")
        return {"Administradores": "admin", "default": "enfermeiro"}


def authenticate_ldap(username, password):
    ldap_host = os.getenv("AD_SERVER", "localhost")
    base_dn = os.getenv("AD_BASEDN", "dc=hc,dc=gov,dc=br")

    admin_dn = os.getenv("AD_ADMIN_DN", "cn=admin,dc=hc,dc=gov,dc=br")
    admin_pw = os.getenv("AD_ADMIN_PASSWORD", "admin")

    user_dn = f"cn={username},ou=people,{base_dn}"

    mapping = load_group_mapping()

    try:
        server = Server(ldap_host, get_info=ALL)

        try:
            conn_user = Connection(server, user=user_dn, password=password, auto_bind=True)
            conn_user.unbind()
        except Exception:
            print(f"Senha inválida para usuário {username}")
            return None

        conn_admin = Connection(server, user=admin_dn, password=admin_pw, auto_bind=True)
        search_filter = f"(&(objectClass=groupOfNames)(member={user_dn}))"
        conn_admin.search(
            search_base=f"ou=groups,{base_dn}",
            search_filter=search_filter,
            attributes=['cn'],
            search_scope=SUBTREE
        )

        user_groups = []
        for entry in conn_admin.entries:
            val = entry.cn.value
            if isinstance(val, list):
                user_groups.extend(val)
            else:
                user_groups.append(str(val))

        print(f"DEBUG: Usuário validado: {user_dn}")
        print(f"DEBUG: Grupos encontrados (busca admin): {user_groups}")

        conn_admin.search(search_base=user_dn, search_filter="(objectClass=*)", attributes=['displayName', 'mail'])
        user_info = conn_admin.entries[0] if conn_admin.entries else None

        conn_admin.unbind()

        system_role = mapping.get("default", "enfermeiro")

        for group in user_groups:
            if group in mapping:
                system_role = mapping[group]
                if system_role == "admin":
                    break

        raw_display_name = user_info.displayName.value if user_info and 'displayName' in user_info else username
        if isinstance(raw_display_name, list):
            display_name = str(raw_display_name[0]) if raw_display_name else username
        else:
            display_name = str(raw_display_name)

        return {
            "username": username,
            "display_name": display_name,
            "email": str(user_info.mail) if user_info and 'mail' in user_info else "",
            "groups": user_groups,
            "role": system_role
        }

    except Exception as e:
        print(f"Erro técnico na autenticação LDAP: {e}")
        return None

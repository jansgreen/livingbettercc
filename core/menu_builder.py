import re
from typing import List, Dict, Optional


def safe_id(text: str) -> str:
    if not text:
        return "menu"
    return re.sub(r"[^a-zA-Z0-9_-]", "", (text or "").replace(" ", "_").lower())


def filter_submenus(user, submenus: List[Dict]) -> List[Dict]:
    """
    Returns only allowed submenus for the given user.
    Rules:
    - superuser: allow all
    - missing 'perm': allow (considered public)
    - with 'perm': allow only if user.has_perm(perm)
    Ensures each submenu has a 'safe_id'.
    """
    if not submenus:
        return []

    if getattr(user, "is_superuser", False):
        # still ensure safe_id for consistency
        return [
            {
                **submenu,
                "safe_id": submenu.get("safe_id") or safe_id(submenu.get("nombre", "")),
            }
            for submenu in submenus
        ]

    allowed: List[Dict] = []
    for submenu in submenus:
        perm = submenu.get("perm")
        if not perm or user.has_perm(perm):
            allowed.append({
                **submenu,
                "safe_id": submenu.get("safe_id") or safe_id(submenu.get("nombre", "")),
            })
    return allowed


def build_menu(user, nombre: str, submenus: List[Dict], url: str = "#") -> Optional[Dict]:
    """
    Build a menu dict with filtered submenus. If no submenus remain, return None.
    Adds 'safe_id' to the menu.
    """
    filtered = filter_submenus(user, submenus)
    if not filtered:
        return None
    return {
        "nombre": nombre,
        "safe_id": safe_id(nombre),
        "url": url,
        "submenus": filtered,
    }


def filter_menus(user, menus_list: List[Dict]) -> List[Dict]:
    """
    Given a list of menu definitions with keys: nombre, submenus, url?, return only built menus
    with permitted submenus. Each item in menus_list can be like:
      {"nombre": "...", "submenus": [...], "url": "#"}
    """
    final: List[Dict] = []
    for m in menus_list:
        nombre = m.get("nombre", "")
        url = m.get("url", "#")
        submenus = m.get("submenus", [])
        built = build_menu(user, nombre, submenus, url)
        if built:
            final.append(built)
    return final

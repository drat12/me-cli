from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import requests

from app.client.engsel import get_family
from app.menus.package import show_package_details
from app.service.auth import AuthInstance
from app.menus.util import clear_screen, pause, _c

console = Console()

def show_hot_menu():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    in_hot_menu = True
    while in_hot_menu:
        clear_screen()
        console.print(Panel("🔥 Paket Hot 🔥", style=_c("text_title"), border_style=_c("border_info"), padding=(0, 2), expand=True))

        url = "https://me.mashu.lol/pg-hot.json"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            hot_packages = response.json()
        except Exception:
            console.print("Gagal mengambil data hot package.", style=_c("text_err"))
            pause()
            return None

        if not hot_packages:
            console.print("Tidak ada paket hot tersedia saat ini.", style=_c("text_sub"))
            pause()
            return None

        table = Table(box=None, expand=True)
        table.add_column("No", justify="center", style=_c("text_number"), width=6)
        table.add_column("Family", style=_c("text_body"))
        table.add_column("Variant", style=_c("text_key"))
        table.add_column("Option", style=_c("text_key"))

        for idx, p in enumerate(hot_packages, 1):
            table.add_row(str(idx), p["family_name"], p["variant_name"], p["option_name"])

        console.print(table)
        console.print("00. Kembali ke menu utama", style=_c("text_sub"))
        choice = console.input("Pilih paket (nomor): ").strip()

        if choice == "00":
            in_hot_menu = False
            return None

        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected = hot_packages[int(choice) - 1]
            family_code = selected["family_code"]
            is_enterprise = selected["is_enterprise"]

            family_data = get_family(api_key, tokens, family_code, is_enterprise)
            if not family_data:
                console.print("Gagal mengambil data family.", style=_c("text_err"))
                pause()
                continue

            option_code = None
            for variant in family_data["package_variants"]:
                if variant["name"] == selected["variant_name"]:
                    for option in variant["package_options"]:
                        if option["order"] == selected["order"]:
                            option_code = option["package_option_code"]
                            break

            if option_code:
                show_package_details(api_key, tokens, option_code, is_enterprise)
            else:
                console.print("Paket tidak ditemukan dalam variant.", style=_c("text_err"))
                pause()
        else:
            console.print("Input tidak valid. Silakan coba lagi.", style=_c("text_err"))
            pause()

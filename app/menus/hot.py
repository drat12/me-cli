import requests
from rich.table import Table
from rich.panel import Panel

from app.client.engsel import get_family
from app.menus.package import show_package_details
from app.service.auth import AuthInstance
from app.menus.util import clear_screen, pause
from app.theme import _c, console

def show_hot_menu():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    in_hot_menu = True
    while in_hot_menu:
        clear_screen()
        console.print(Panel("🔥 Paket HOT 🔥", title="[bold]Rekomendasi Paket[/]", border_style=_c("border_primary"), padding=(1, 4), expand=True))

        url = "https://me.mashu.lol/pg-hot.json"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            hot_packages = response.json()
        except Exception as e:
            console.print(f"Gagal mengambil data hot package: {e}", style=_c("text_err"))
            pause()
            return None

        if not hot_packages:
            console.print("Tidak ada paket HOT tersedia saat ini.", style=_c("text_warn"))
            pause()
            return None

        # Tampilkan daftar paket HOT
        table = Table(box="SIMPLE", expand=True)
        table.add_column("No", justify="right", style=_c("text_number"), width=6)
        table.add_column("Family", style=_c("text_sub"))
        table.add_column("Variant", style=_c("text_body"))
        table.add_column("Paket", style=_c("text_value"))

        for idx, p in enumerate(hot_packages):
            table.add_row(str(idx + 1), p["family_name"], p["variant_name"], p["option_name"])

        console.print(Panel(table, title="", border_style=_c("border_info"), padding=(1, 2), expand=True))
        console.print(f"[{_c('text_sub')}]00 untuk kembali ke menu utama[/{_c('text_sub')}]")
        choice = console.input(f"[{_c('text_sub')}]Pilih paket (nomor):[/{_c('text_sub')}] ").strip()

        if choice == "00":
            in_hot_menu = False
            return None

        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_bm = hot_packages[int(choice) - 1]
            family_code = selected_bm["family_code"]
            is_enterprise = selected_bm["is_enterprise"]
            
            family_data = get_family(api_key, tokens, family_code, is_enterprise)
            if not family_data:
                console.print("Gagal mengambil data family.", style=_c("text_err"))
                pause()
                continue
            
            package_variants = family_data.get("package_variants", [])
            option_code = None
            for variant in package_variants:
                if variant["name"] == selected_bm["variant_name"]:
                    for option in variant.get("package_options", []):
                        if option["order"] == selected_bm["order"]:
                            option_code = option["package_option_code"]
                            break
            
            if option_code:
                show_package_details(api_key, tokens, option_code, is_enterprise)
            else:
                console.print("Paket tidak ditemukan dalam data family.", style=_c("text_err"))
                pause()
        else:
            console.print("Input tidak valid. Silakan coba lagi.", style=_c("text_err"))
            pause()

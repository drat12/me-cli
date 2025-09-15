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
            try:
                hot_packages = response.json()
            except Exception:
                console.print("Data HOT tidak dalam format JSON.", style=_c("text_err"))
                pause()
                return None
        except Exception as e:
            console.print(f"Gagal mengambil data hot package: {e}", style=_c("text_err"))
            pause()
            return None

        if not isinstance(hot_packages, list) or not hot_packages:
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
            table.add_row(str(idx + 1), p.get("family_name", "-"), p.get("variant_name", "-"), p.get("option_name", "-"))

        console.print(Panel(table, title="", border_style=_c("border_info"), padding=(1, 2), expand=True))
        console.print(f"[{_c('text_sub')}]00 untuk kembali ke menu utama[/{_c('text_sub')}]")
        choice = console.input(f"[{_c('text_sub')}]Pilih paket (nomor):[/{_c('text_sub')}] ").strip()

        if choice == "00":
            in_hot_menu = False
            return None

        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_bm = hot_packages[int(choice) - 1]
            family_code = selected_bm.get("family_code")
            is_enterprise = selected_bm.get("is_enterprise", False)
            variant_name = selected_bm.get("variant_name")
            order = selected_bm.get("order")

            if not family_code or not variant_name or order is None:
                console.print("Data paket tidak lengkap.", style=_c("text_err"))
                pause()
                continue

            family_data = get_family(api_key, tokens, family_code, is_enterprise)
            if not family_data:
                console.print("Gagal mengambil data family.", style=_c("text_err"))
                pause()
                continue
            
            package_variants = family_data.get("package_variants", [])
            option_code = None
            for variant in package_variants:
                if variant.get("name") == variant_name:
                    for option in variant.get("package_options", []):
                        if option.get("order") == order:
                            option_code = option.get("package_option_code")
                            break
            
            if option_code:
                show_package_details(api_key, tokens, option_code, is_enterprise)
            else:
                console.print("Paket tidak ditemukan dalam data family.", style=_c("text_err"))
                pause()
        else:
            console.print("Input tidak valid. Silakan coba lagi.", style=_c("text_err"))
            pause()

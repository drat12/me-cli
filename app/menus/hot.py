import requests
from app.client.engsel import get_family
from app.menus.package import show_package_details
from app.service.auth import AuthInstance
from app.menus.util import clear_screen, pause, pesan_error, pesan_info
from app.theme import _c, console

from rich.panel import Panel
from rich.table import Table
from rich.box import MINIMAL_DOUBLE_HEAD
from rich.align import Align

def tampilkan_header():
    header_text = Align.center(f"[{_c('text_title')}]🔥 Paket HOT 🔥[/]")
    panel = Panel(
        header_text,
        border_style=_c("border_primary"),
        padding=(1, 4),
        expand=True
    )
    console.print(panel)

def tampilkan_hot_packages(hot_packages):
    table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
    table.add_column("No", justify="right", style=_c("text_number"), width=4)
    table.add_column("Family", style=_c("text_body"))
    table.add_column("Variant", style=_c("text_body"))
    table.add_column("Option", style=_c("text_body"))

    for idx, p in enumerate(hot_packages, 1):
        table.add_row(str(idx), p["family_name"], p["variant_name"], p["option_name"])

    panel = Panel(
        table,
        title=f"[{_c('text_title')}]Daftar Paket HOT[/]",
        border_style=_c("border_info"),
        padding=(1, 2),
        expand=True
    )
    console.print(panel)

def tampilkan_menu_opsi():
    opsi = Table.grid(padding=(0, 2))
    opsi.add_column(justify="right", style=_c("text_number"))
    opsi.add_column(style=_c("text_body"))
    opsi.add_row("00", "Kembali ke menu utama")

    panel = Panel(opsi, border_style=_c("border_info"), title="Opsi", title_align="center", expand=True)
    console.print(panel)

def show_hot_menu():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    in_hot_menu = True

    while in_hot_menu:
        clear_screen()
        tampilkan_header()

        url = "https://me.mashu.lol/pg-hot.json"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except Exception as e:
            pesan_error(f"Gagal mengambil data hot package: {e}")
            pause()
            return

        hot_packages = response.json()
        tampilkan_hot_packages(hot_packages)
        tampilkan_menu_opsi()

        choice = console.input(f"[{_c('text_sub')}]Pilih paket (nomor):[/{_c('text_sub')}] ").strip()
        if choice == "00":
            in_hot_menu = False
            return

        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_bm = hot_packages[int(choice) - 1]
            family_code = selected_bm["family_code"]
            is_enterprise = selected_bm["is_enterprise"]

            family_data = get_family(api_key, tokens, family_code, is_enterprise)
            if not family_data:
                pesan_error("Gagal mengambil data family.")
                pause()
                continue

            option_code = None
            for variant in family_data["package_variants"]:
                if variant["name"] == selected_bm["variant_name"]:
                    for option in variant["package_options"]:
                        if option["order"] == selected_bm["order"]:
                            option_code = option["package_option_code"]
                            break

            if option_code:
                console.print(f"[{_c('text_value')}]{option_code}[/{_c('text_value')}]")
                show_package_details(api_key, tokens, option_code, is_enterprise)
            else:
                pesan_error("Paket tidak ditemukan.")
                pause()
        else:
            pesan_error("Input tidak valid. Silahkan coba lagi.")
            pause()

from dotenv import load_dotenv
load_dotenv()

import sys
import os
import json
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED
from app.menus.util import clear_screen, pause
from app.client.engsel import *
from app.service.auth import AuthInstance
from app.menus.bookmark import show_bookmark_menu
from app.menus.account import show_account_menu
from app.menus.package import fetch_my_packages, get_packages_by_family
from app.menus.hot import show_hot_menu

# ========= Theme presets + persist =========
_THEME_FILE = "theme.json"

THEMES = {
    "dark_neon": {
        "border_primary": "#7C3AED",
        "border_info": "#06B6D4",
        "border_success": "#10B981",
        "border_warning": "#F59E0B",
        "border_error": "#EF4444",
        "text_title": "bold #E5E7EB",
        "text_sub": "bold #22D3EE",
        "text_ok": "bold #34D399",
        "text_warn": "bold #FBBF24",
        "text_err": "bold #F87171",
        "text_body": "#D1D5DB",
        "text_key": "#A78BFA",
        "text_value": "bold #F3F4F6",
        "text_money": "bold #34D399",
        "text_date": "bold #FBBF24",
        "text_number": "#C084FC",
        "gradient_start": "#22D3EE",
        "gradient_end": "#A78BFA",
    },
    "default": {
        "border_primary": "magenta",
        "border_info": "cyan",
        "border_success": "green",
        "border_warning": "yellow",
        "border_error": "red",
        "text_title": "bold white",
        "text_sub": "bold cyan",
        "text_ok": "bold green",
        "text_warn": "bold yellow",
        "text_err": "bold red",
        "text_body": "white",
        "text_key": "magenta",
        "text_value": "bold white",
        "text_money": "bold green",
        "text_date": "bold yellow",
        "text_number": "magenta",
        "gradient_start": "#8A2BE2",
        "gradient_end": "#00FFFF",
    },
    "red_black": {
        "border_primary": "#EF4444",
        "border_info": "#F87171",
        "border_success": "#22C55E",
        "border_warning": "#F59E0B",
        "border_error": "#DC2626",
        "text_title": "bold #F3F4F6",
        "text_sub": "bold #EF4444",
        "text_ok": "bold #22C55E",
        "text_warn": "bold #F59E0B",
        "text_err": "bold #F87171",
        "text_body": "#E5E7EB",
        "text_key": "#F87171",
        "text_value": "bold #F3F4F6",
        "text_money": "bold #22C55E",
        "text_date": "bold #FBBF24",
        "text_number": "#EF4444",
        "gradient_start": "#DC2626",
        "gradient_end": "#F59E0B",
    },
    "emerald_glass": {
        "border_primary": "#10B981",
        "border_info": "#34D399",
        "border_success": "#059669",
        "border_warning": "#A3E635",
        "border_error": "#EF4444",
        "text_title": "bold #ECFDF5",
        "text_sub": "bold #34D399",
        "text_ok": "bold #22C55E",
        "text_warn": "bold #A3E635",
        "text_err": "bold #F87171",
        "text_body": "#D1FAE5",
        "text_key": "#6EE7B7",
        "text_value": "bold #F0FDFA",
        "text_money": "bold #22C55E",
        "text_date": "bold #A3E635",
        "text_number": "#10B981",
        "gradient_start": "#34D399",
        "gradient_end": "#A7F3D0",
    },
}

def _load_theme_name():
    try:
        if os.path.exists(_THEME_FILE):
            with open(_THEME_FILE, "r", encoding="utf8") as f:
                return json.load(f).get("name", "dark_neon")
    except Exception:
        pass
    return "dark_neon"

def _save_theme_name(name: str):
    try:
        with open(_THEME_FILE, "w", encoding="utf8") as f:
            json.dump({"name": name}, f)
    except Exception:
        pass

_theme_name = _load_theme_name()
THEME = THEMES.get(_theme_name, THEMES["dark_neon"]).copy()

def set_theme(name: str):
    global THEME, _theme_name
    if name in THEMES:
        THEME = THEMES[name].copy()
        _theme_name = name
        _save_theme_name(name)
        return True
    return False

def _c(key: str) -> str:
    return THEME.get(key, "white")

console = Console()

def _print_centered_panel(renderable, title="", border_style=""):
    """Print Rich panel with centered title and custom border."""
    panel = Panel(
        renderable,
        title=title,
        border_style=border_style,
        padding=(0,2),
        expand=True,
        title_align="center"
    )
    console.print(panel)

def show_banner():
    # Optional: bisa tambahkan logo/banner di sini jika ingin
    pass

def show_main_menu(number, balance, balance_expired_at):
    clear_screen()
    show_banner()
    phone_number = number
    remaining_balance = balance
    expired_at_dt = datetime.fromtimestamp(balance_expired_at).strftime("%Y-%m-%d %H:%M:%S")

    # Panel Informasi Akun
    info = Table.grid(padding=(0,2))
    info.add_column(justify="right", style=_c("text_sub"))
    info.add_column(style=_c("text_body"))
    info.add_row("Nomor", f"[{_c('text_value')}]{phone_number}[/]")
    info.add_row("Pulsa", f"[{_c('text_money')}]Rp {remaining_balance:,}[/]")
    info.add_row("Masa Aktif", f"[{_c('text_date')}]{expired_at_dt}[/]")
    _print_centered_panel(info, title=f"[{_c('text_title')}]Informasi Akun[/]", border_style=_c("border_info"))

    # ======= Main Menu =======
    menu = Table(show_header=False, box=ROUNDED, padding=(1,1), expand=True)
    menu.add_column("key", justify="right", style=_c("text_number"), no_wrap=True, width=4)
    menu.add_column("desc", style=_c("text_body"))
    menu.add_row("[bold]1[/]", "Login/Ganti akun")
    menu.add_row("[bold]2[/]", "Lihat Paket Saya")
    menu.add_row("[bold]3[/]", "Beli Paket 🔥 HOT 🔥")
    menu.add_row("[bold]4[/]", "Input Family Code")
    menu.add_row("[bold]5[/]", "Input Family Code (Enterprise)")
    menu.add_row("[bold]00[/]", "Bookmark Paket")
    menu.add_row("[bold]69[/]", f"[{_c('text_sub')}]Ganti Gaya[/]")
    menu.add_row("[bold]99[/]", f"[{_c('text_err')}]Tutup aplikasi[/]")
    _print_centered_panel(menu, title=f"[{_c('text_title')}]Menu[/]", border_style=_c("border_primary"))

def show_theme_presets():
    console.print(f"\n[{_c('text_title')}]Ganti Tema (Preset)[/{_c('text_title')}]")
    theme_names = list(THEMES.keys())
    table = Table(show_header=True, box=ROUNDED, expand=True)
    table.add_column("No", justify="center", style=_c("text_sub"))
    table.add_column("Nama Preset", style=_c("text_title"))
    table.add_column("Preview Warna", style=_c("text_body"))
    for idx, name in enumerate(theme_names, 1):
        preset = THEMES[name]
        preview = (
            f"[{preset['border_primary']}]■[/{preset['border_primary']}] "
            f"[{preset['border_info']}]■[/{preset['border_info']}] "
            f"[{preset['border_success']}]■[/{preset['border_success']}] "
            f"[{preset['border_error']}]■[/{preset['border_error']}] "
            f"[{preset['text_title']}]A[/{preset['text_title']}]"
        )
        aktif = " (aktif)" if name == _theme_name else ""
        table.add_row(
            f"{idx}",
            f"{name}{aktif}",
            preview
        )
    console.print(table)

def menu_ganti_theme():
    clear_screen()
    show_theme_presets()
    theme_names = list(THEMES.keys())
    pilihan = console.input(f"\n[{_c('text_sub')}]Masukkan nomor tema yang diinginkan:[/{_c('text_sub')}] ").strip()
    try:
        idx = int(pilihan) - 1
        if idx < 0 or idx >= len(theme_names):
            pesan_error("Pilihan tema tidak valid.")
        elif theme_names[idx] == _theme_name:
            pesan_info(f"Tema '{theme_names[idx]}' sudah aktif.")
        else:
            set_theme(theme_names[idx])
            pesan_sukses(f"Tema berhasil diganti ke '{theme_names[idx]}'.")
    except Exception:
        pesan_error("Input tidak valid.")
    pause()

def pesan_error(msg):
    console.print(f"[{_c('text_err')}]{msg}[/{_c('text_err')}]")

def pesan_sukses(msg):
    console.print(f"[{_c('text_ok')}]{msg}[/{_c('text_ok')}]")

def pesan_info(msg):
    console.print(f"[{_c('text_warn')}]{msg}[/{_c('text_warn')}]")

def main():
    while True:
        active_user = AuthInstance.get_active_user()
        if active_user is not None:
            try:
                balance = get_balance(AuthInstance.api_key, active_user["tokens"]["id_token"])
                balance_remaining = balance.get("remaining")
                balance_expired_at = balance.get("expired_at")
            except Exception as e:
                pesan_error(f"Gagal mengambil data saldo: {e}")
                pause()
                continue

            show_main_menu(active_user["number"], balance_remaining, balance_expired_at)

            choice = console.input(f"[{_c('text_sub')}]Pilih menu:[/{_c('text_sub')}] ").strip()
            if choice == "1":
                selected_user_number = show_account_menu()
                if selected_user_number:
                    AuthInstance.set_active_user(selected_user_number)
                    pesan_sukses("Akun berhasil diganti.")
                else:
                    pesan_error("Tidak ada user yang dipilih atau gagal memuat user.")
                continue
            elif choice == "2":
                try:
                    fetch_my_packages()
                    pesan_sukses("Paket berhasil ditampilkan.")
                except Exception as e:
                    pesan_error(f"Gagal menampilkan paket: {e}")
                continue
            elif choice == "3":
                try:
                    show_hot_menu()
                except Exception as e:
                    pesan_error(f"Gagal menampilkan menu HOT: {e}")
            elif choice == "4":
                family_code = console.input(f"[{_c('text_sub')}]Masukkan family code (atau '99' untuk batal):[/{_c('text_sub')}] ").strip()
                if family_code == "99":
                    pesan_info("Aksi dibatalkan.")
                    continue
                try:
                    get_packages_by_family(family_code)
                    pesan_sukses("Paket berdasarkan family code berhasil ditampilkan.")
                except Exception as e:
                    pesan_error(f"Gagal menampilkan paket: {e}")
            elif choice == "5":
                family_code = console.input(f"[{_c('text_sub')}]Masukkan family code (atau '99' untuk batal):[/{_c('text_sub')}] ").strip()
                if family_code == "99":
                    pesan_info("Aksi dibatalkan.")
                    continue
                try:
                    get_packages_by_family(family_code, is_enterprise=True)
                    pesan_sukses("Paket enterprise berhasil ditampilkan.")
                except Exception as e:
                    pesan_error(f"Gagal menampilkan paket enterprise: {e}")
            elif choice == "69":
                menu_ganti_theme()
                continue
            elif choice == "00":
                try:
                    show_bookmark_menu()
                    pesan_sukses("Menu bookmark berhasil ditampilkan.")
                except Exception as e:
                    pesan_error(f"Gagal menampilkan menu bookmark: {e}")
            elif choice == "99":
                pesan_info("Exiting the application.")
                sys.exit(0)
            elif choice == "9":
                pass
            else:
                pesan_error("Pilihan tidak valid. Silakan coba lagi.")
                pause()
        else:
            pesan_info("Silakan login terlebih dahulu.")
            selected_user_number = show_account_menu()
            if selected_user_number:
                AuthInstance.set_active_user(selected_user_number)
                pesan_sukses("Login berhasil.")
            else:
                pesan_error("Tidak ada user yang dipilih atau gagal memuat user.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pesan_info("Exiting the application.")
    except Exception as e:
        pesan_error(f"Terjadi kesalahan: {e}")
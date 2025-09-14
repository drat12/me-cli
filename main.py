import os
import sys
import json
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich import box

# ========== Theme presets + persist ==========
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

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("Tekan ENTER untuk lanjut...")

def pesan_error(msg):
    console.print(f"[bold red]{msg}[/bold red]")

def pesan_sukses(msg):
    console.print(f"[bold green]{msg}[/bold green]")

def pesan_info(msg):
    console.print(f"[bold yellow]{msg}[/bold yellow]")

def show_main_menu():
    clear_screen()
    table = Table(show_header=False, box=box.ROUNDED, expand=True)
    table.add_column("", justify="right", width=6)
    table.add_column("Menu", justify="left")
    menu_items = [
        ("[bold cyan]1[/bold cyan]", "Login/Ganti akun"),
        ("[bold cyan]2[/bold cyan]", "Lihat Paket Saya"),
        ("[bold cyan]3[/bold cyan]", "Beli Paket 🔥 HOT 🔥"),
        ("[bold cyan]4[/bold cyan]", "Beli Paket Berdasarkan Family Code"),
        ("[bold cyan]5[/bold cyan]", "Beli Paket Berdasarkan Family Code (Enterprise)"),
        ("[bold cyan]6[/bold cyan]", "Ganti Tema"),  # <--- Menu ganti tema
        ("[bold cyan]99[/bold cyan]", "Tutup aplikasi")
    ]
    for num, name in menu_items:
        table.add_row(num, name)
    console.print(Panel(table, title="[bold yellow]Menu Utama[/bold yellow]", border_style=_c("border_primary"), expand=True))

def menu_ganti_theme():
    clear_screen()
    theme_names = list(THEMES.keys())
    console.print("[bold yellow]Pilih Tema:[/bold yellow]\n")
    for idx, name in enumerate(theme_names, 1):
        selected = " (aktif)" if name == _theme_name else ""
        console.print(f"[bold cyan]{idx}[/bold cyan]. {name}{selected}")
    pilihan = console.input("\n[bold cyan]Masukkan nomor tema yang diinginkan:[/bold cyan] ").strip()
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

def main():
    while True:
        show_main_menu()
        choice = console.input("[bold cyan]Pilih menu:[/bold cyan] ").strip()
        if choice == "1":
            pesan_info("Login/Ganti akun (dummy menu)")
            pause()
        elif choice == "2":
            pesan_info("Lihat Paket Saya (dummy menu)")
            pause()
        elif choice == "3":
            pesan_info("Beli Paket HOT (dummy menu)")
            pause()
        elif choice == "4":
            pesan_info("Beli Paket by Family Code (dummy menu)")
            pause()
        elif choice == "5":
            pesan_info("Beli Paket by Family Code (Enterprise) (dummy menu)")
            pause()
        elif choice == "6":
            menu_ganti_theme()
        elif choice == "99":
            pesan_info("Exiting the application.")
            sys.exit(0)
        else:
            pesan_error("Pilihan tidak valid. Silakan coba lagi.")
            pause()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pesan_info("Exiting the application.")
    except Exception as e:
        pesan_error(f"Terjadi kesalahan: {e}")
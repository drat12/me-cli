from dotenv import load_dotenv
load_dotenv()

import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from app.menus.util import clear_screen, pause
from app.client.engsel import *
from app.service.auth import AuthInstance
from app.menus.bookmark import show_bookmark_menu
from app.menus.account import show_account_menu
from app.menus.package import fetch_my_packages, get_packages_by_family
from app.menus.hot import show_hot_menu

console = Console()

def show_main_menu(number, balance, balance_expired_at):
    clear_screen()
    phone_number = number
    remaining_balance = balance
    expired_at_dt = datetime.fromtimestamp(balance_expired_at).strftime("%Y-%m-%d %H:%M:%S")

    # Panel: Informasi Akun rata kiri
    info_akun = (
        f"[bold magenta]Nomor   :[/bold magenta] {phone_number}\n"
        f"[bold magenta]Pulsa   :[/bold magenta] Rp {remaining_balance}\n"
        f"[bold magenta]Masa aktif:[/bold magenta] {expired_at_dt}"
    )
    console.print(
        Panel(
            info_akun,
            title="Informasi Akun",
            border_style="cyan",
            expand=True,
            padding=(0,2),
            title_align="right"
        )
    )

    # Tabel menu utama dua kolom, dengan garis pemisah
    table = Table(show_header=False, box=box.ROUNDED, expand=True)
    table.add_column("", justify="right", width=6)
    table.add_column("Menu", justify="left")
    menu_items = [
        ("[bold cyan]1[/bold cyan]", "Login/Ganti akun"),
        ("[bold cyan]2[/bold cyan]", "Lihat Paket Saya"),
        ("[bold cyan]3[/bold cyan]", "Beli Paket 🔥 HOT 🔥"),
        ("[bold cyan]4[/bold cyan]", "Beli Paket Berdasarkan Family Code"),
        ("[bold cyan]5[/bold cyan]", "Beli Paket Berdasarkan Family Code (Enterprise)"),
        ("[bold cyan]00[/bold cyan]", "Bookmark Paket"),
        ("[bold cyan]99[/bold cyan]", "Tutup aplikasi")
    ]
    for num, name in menu_items:
        table.add_row(num, name)
    console.print(Panel(table, title="[bold yellow]Menu Utama[/bold yellow]", border_style="green", expand=True))

def pesan_error(msg):
    console.print(f"[bold red]{msg}[/bold red]")

def pesan_sukses(msg):
    console.print(f"[bold green]{msg}[/bold green]")

def pesan_info(msg):
    console.print(f"[bold yellow]{msg}[/bold yellow]")

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

            choice = console.input("[bold cyan]Pilih menu:[/bold cyan] ").strip()
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
                family_code = console.input("[bold cyan]Masukkan family code (atau '99' untuk batal):[/bold cyan] ").strip()
                if family_code == "99":
                    pesan_info("Aksi dibatalkan.")
                    continue
                try:
                    get_packages_by_family(family_code)
                    pesan_sukses("Paket berdasarkan family code berhasil ditampilkan.")
                except Exception as e:
                    pesan_error(f"Gagal menampilkan paket: {e}")
            elif choice == "5":
                family_code = console.input("[bold cyan]Masukkan family code (atau '99' untuk batal):[/bold cyan] ").strip()
                if family_code == "99":
                    pesan_info("Aksi dibatalkan.")
                    continue
                try:
                    get_packages_by_family(family_code, is_enterprise=True)
                    pesan_sukses("Paket enterprise berhasil ditampilkan.")
                except Exception as e:
                    pesan_error(f"Gagal menampilkan paket enterprise: {e}")
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
from dotenv import load_dotenv
load_dotenv()

import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
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

    # Panel: Informasi Akun (expand sesuai terminal)
    info_akun = (
        f"[bold magenta]Nomor:[/bold magenta] {phone_number}\n"
        f"[bold magenta]Pulsa:[/bold magenta] Rp {remaining_balance}\n"
        f"[bold magenta]Masa aktif:[/bold magenta] {expired_at_dt}"
    )
    console.print(Panel(info_akun, title="[bold yellow]Informasi Akun[/bold yellow]", border_style="cyan", expand=True))

    # Tabel: Menu Utama
    table = Table(title="Menu Utama", show_header=True, header_style="bold yellow", expand=True)
    table.add_column("No", style="bold cyan", width=6, justify="left")
    table.add_column("Menu", style="bold", justify="left")

    table.add_row("1", "Login/Ganti akun")
    table.add_row("2", "Lihat Paket Saya")
    table.add_row("3", "Beli Paket 🔥 HOT 🔥")
    table.add_row("4", "Beli Paket Berdasarkan Family Code")
    table.add_row("5", "Beli Paket Berdasarkan Family Code (Enterprise)")
    table.add_row("00", "Bookmark Paket")
    table.add_row("99", "Tutup aplikasi")

    console.print(Panel(table, border_style="green", expand=True))


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
from app.client.engsel import get_otp, submit_otp
from app.menus.util import clear_screen, pause
from app.service.auth import AuthInstance
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.box import ROUNDED
from main import _c

console = Console()

def pesan_error(msg):
    console.print(f"[{_c('text_err')}]{msg}[/{_c('text_err')}]")

def pesan_sukses(msg):
    console.print(f"[{_c('text_ok')}]{msg}[/{_c('text_ok')}]")

def pesan_info(msg):
    console.print(f"[{_c('text_warn')}]{msg}[/{_c('text_warn')}]")

def login_prompt(api_key: str):
    clear_screen()
    console.print(Panel("Login ke MyXL", title="[bold]Login[/]", border_style=_c("border_primary")))
    console.print(f"[{_c('text_body')}]Masukkan nomor XL Prabayar (Contoh 6281234567890):[/{_c('text_body')}]")
    phone_number = console.input(f"[{_c('text_key')}]Nomor:[/{_c('text_key')}] ")

    if not phone_number.startswith("628") or len(phone_number) < 10 or len(phone_number) > 14:
        pesan_error("Nomor tidak valid. Pastikan nomor diawali dengan '628' dan memiliki panjang yang benar.")
        return None, None

    try:
        subscriber_id = get_otp(phone_number)
        if not subscriber_id:
            return None, None
        pesan_info("OTP berhasil dikirim ke nomor Anda.")

        otp = console.input(f"[{_c('text_key')}]Masukkan OTP:[/{_c('text_key')}] ").strip()
        if not otp.isdigit() or len(otp) != 6:
            pesan_error("OTP tidak valid. Pastikan OTP terdiri dari 6 digit angka.")
            pause()
            return None, None

        tokens = submit_otp(api_key, phone_number, otp)
        if not tokens:
            pesan_error("Gagal login. Periksa OTP dan coba lagi.")
            pause()
            return None, None

        pesan_sukses("Berhasil login!")
        return phone_number, tokens["refresh_token"]
    except Exception as e:
        pesan_error(f"Terjadi kesalahan: {e}")
        return None, None

def show_account_menu():
    clear_screen()
    AuthInstance.load_tokens()
    users = AuthInstance.refresh_tokens
    active_user = AuthInstance.get_active_user()

    in_account_menu = True
    add_user = False
    while in_account_menu:
        clear_screen()
        if AuthInstance.get_active_user() is None or add_user:
            number, refresh_token = login_prompt(AuthInstance.api_key)
            if not refresh_token:
                pesan_error("Gagal menambah akun. Silahkan coba lagi.")
                pause()
                continue

            AuthInstance.add_refresh_token(int(number), refresh_token)
            AuthInstance.load_tokens()
            users = AuthInstance.refresh_tokens
            active_user = AuthInstance.get_active_user()

            if add_user:
                add_user = False
            continue

        table = Table(title="[bold]Akun Tersimpan[/]", box=ROUNDED, expand=True)
        table.add_column("No", justify="center", style=_c("text_number"))
        table.add_column("Nomor", style=_c("text_body"))
        if not users:
            table.add_row("-", "Tidak ada akun tersimpan.")
        else:
            for idx, user in enumerate(users):
                is_active = active_user and user["number"] == active_user["number"]
                marker = f"[{_c('text_sub')}] (Aktif)[/{_c('text_sub')}]" if is_active else ""
                table.add_row(str(idx + 1), f"{user['number']}{marker}")

        console.print(table)

        console.print(f"\n[{_c('text_key')}]Command:[/{_c('text_key')}]")
        console.print(f"[{_c('text_body')}]0: Tambah Akun[/]")
        console.print(f"[{_c('text_body')}]00: Kembali ke menu utama[/]")
        console.print(f"[{_c('text_body')}]99: Hapus Akun aktif[/]")
        console.print(f"[{_c('text_body')}]Masukkan nomor akun untuk berganti.[/]")

        input_str = console.input(f"[{_c('text_sub')}]Pilihan:[/{_c('text_sub')}] ").strip()
        if input_str == "00":
            in_account_menu = False
            return active_user["number"] if active_user else None
        elif input_str == "0":
            add_user = True
            continue
        elif input_str == "99":
            if not active_user:
                pesan_error("Tidak ada akun aktif untuk dihapus.")
                pause()
                continue
            confirm = console.input(f"[{_c('text_warn')}]Yakin ingin menghapus akun {active_user['number']}? (y/n):[/{_c('text_warn')}] ").strip()
            if confirm.lower() == 'y':
                AuthInstance.remove_refresh_token(active_user["number"])
                users = AuthInstance.refresh_tokens
                active_user = AuthInstance.get_active_user()
                pesan_sukses("Akun berhasil dihapus.")
                pause()
            else:
                pesan_info("Penghapusan akun dibatalkan.")
                pause()
            continue
        elif input_str.isdigit() and 1 <= int(input_str) <= len(users):
            selected_user = users[int(input_str) - 1]
            return selected_user['number']
        else:
            pesan_error("Input tidak valid. Silahkan coba lagi.")
            pause()
            continue

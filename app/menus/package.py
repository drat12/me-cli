import json
from app.service.auth import AuthInstance
from app.client.engsel import (
    get_family, get_package, get_addons,
    purchase_package, send_api_request
)
from app.service.bookmark import BookmarkInstance
from app.client.purchase import (
    show_multipayment, show_qris_payment, settlement_bounty
)
from app.menus.util import clear_screen, pause, display_html
from app.theme import _c, console
from rich.panel import Panel
from rich.table import Table
from rich.box import MINIMAL_DOUBLE_HEAD

# ========== Utility ==========
def pesan_error(msg): console.print(f"[{_c('text_err')}]{msg}[/{_c('text_err')}]")
def pesan_sukses(msg): console.print(f"[{_c('text_ok')}]{msg}[/{_c('text_ok')}]")
def pesan_info(msg): console.print(f"[{_c('text_warn')}]{msg}[/{_c('text_warn')}]")

# ========== Detail Paket ==========
def show_package_details(api_key, tokens, package_option_code, is_enterprise, option_order=-1):
    clear_screen()
    package = get_package(api_key, tokens, package_option_code)
    if not package:
        pesan_error("Gagal memuat detail paket.")
        pause()
        return False

    variant_name = package.get("package_detail_variant", {}).get("name", "")
    option_name = package.get("package_option", {}).get("name", "")
    family_name = package.get("package_family", {}).get("name", "")
    title = f"{family_name} {variant_name} {option_name}".strip()
    item_name = f"{variant_name} {option_name}".strip()
    price = package["package_option"]["price"]
    validity = package["package_option"]["validity"]
    token_confirmation = package["token_confirmation"]
    ts_to_sign = package["timestamp"]
    payment_for = package["package_family"]["payment_for"]
    detail = display_html(package["package_option"]["tnc"])

    info = Table.grid(padding=(0, 2))
    info.add_column(justify="right", style=_c("text_sub"))
    info.add_column(style=_c("text_body"))
    info.add_row("Nama", f"[{_c('text_value')}]{title}[/]")
    info.add_row("Harga", f"[{_c('text_money')}]Rp {price:,}[/]")
    info.add_row("Masa Aktif", f"[{_c('text_date')}]{validity}[/]")
    console.print(Panel(info, title=f"[{_c('text_title')}]Detail Paket[/]", border_style=_c("border_info"), padding=(1, 0), expand=True))

    benefits = package["package_option"].get("benefits", [])
    if benefits:
        benefit_table = Table(box=MINIMAL_DOUBLE_HEAD, expand=True)
        benefit_table.add_column("Nama", style=_c("text_body"))
        benefit_table.add_column("Jumlah", style=_c("text_value"), justify="right")
        for benefit in benefits:
            name = benefit.get("name", "")
            total = benefit.get("total", 0)
            if "Call" in name:
                value = f"{total / 60:.0f} menit"
            else:
                if total >= 1_000_000_000:
                    value = f"{total / (1024 ** 3):.2f} GB"
                elif total >= 1_000_000:
                    value = f"{total / (1024 ** 2):.2f} MB"
                elif total >= 1_000:
                    value = f"{total / 1024:.2f} KB"
                else:
                    value = str(total)
            benefit_table.add_row(name, value)
        console.print(Panel(benefit_table, title=f"[{_c('text_title')}]Benefit Paket[/]", border_style=_c("border_success"), padding=(1, 0), expand=True))

    addons = get_addons(api_key, tokens, package_option_code)
    if addons:
        addon_text = json.dumps(addons, indent=2)
        console.print(Panel(addon_text, title=f"[{_c('text_title')}]Addons[/]", border_style=_c("border_info"), padding=(1, 2), expand=True))

    console.print(Panel(detail, title=f"[{_c('text_title')}]Syarat & Ketentuan[/]", border_style=_c("border_warning"), padding=(1, 2), expand=True))

    while True:
        menu = Table(show_header=False, box=MINIMAL_DOUBLE_HEAD, expand=True)
        menu.add_column("Kode", justify="center", style=_c("text_number"), width=6)
        menu.add_column("Aksi", style=_c("text_body"))
        menu.add_row("1", "Beli dengan Pulsa")
        menu.add_row("2", "Beli dengan E-Wallet")
        menu.add_row("3", "Bayar dengan QRIS")
        if payment_for == "REDEEM_VOUCHER":
            menu.add_row("4", "Ambil sebagai bonus")
        if option_order != -1:
            menu.add_row("0", "Tambah ke Bookmark")
        menu.add_row("00", "Kembali ke daftar paket")
        console.print(Panel(menu, title="", border_style=_c("border_primary"), padding=(1, 0), expand=True))

        choice = console.input(f"[{_c('text_sub')}]Pilihan:[/{_c('text_sub')}] ").strip()
        if choice == "00":
            return False
        elif choice == "0" and option_order != -1:
            success = BookmarkInstance.add_bookmark(
                family_code=package.get("package_family", {}).get("package_family_code", ""),
                family_name=family_name,
                is_enterprise=is_enterprise,
                variant_name=variant_name,
                option_name=option_name,
                order=option_order,
            )
            pesan_sukses("Paket ditambahkan ke bookmark." if success else "Paket sudah ada di bookmark.")
            pause()
        elif choice == "1":
            purchase_package(api_key, tokens, package_option_code, is_enterprise)
            pause()
            return True
        elif choice == "2":
            show_multipayment(api_key, tokens, package_option_code, token_confirmation, price, item_name)
            pause()
            return True
        elif choice == "3":
            show_qris_payment(api_key, tokens, package_option_code, token_confirmation, price, item_name)
            pause()
            return True
        elif choice == "4" and payment_for == "REDEEM_VOUCHER":
            settlement_bounty(api_key, tokens, token_confirmation, ts_to_sign, package_option_code, price, variant_name)
            pause()
        else:
            pesan_error("Pilihan tidak dikenali.")
            pause()

# ========== Daftar Paket Berdasarkan Family ==========
def get_packages_by_family(family_code: str, is_enterprise: bool = False):
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    if not tokens:
        pesan_error("Token pengguna tidak ditemukan.")
        pause()
        return None

    data = get_family(api_key, tokens, family_code, is_enterprise)
    if not data:
        pesan_error("Gagal memuat data paket keluarga.")
        pause()
        return None

    packages = []
    family_name = data['package_family']["name"]
    package_variants = data["package_variants"]

    while True:
        clear_screen()
        table = Table(title=f"[{_c('text_title')}]Paket Tersedia - {family_name}[/]", box=MINIMAL_DOUBLE_HEAD, expand=True)
        table.add_column("No", justify="center", style=_c("text_number"), width=6)
        table.add_column("Variant", style=_c("text_sub"))
        table.add_column("Nama Paket", style=_c("text_body"))
        table.add_column("Harga", style=_c("text_money"), justify="right")

        option_number = 1
        for variant in package_variants:
            variant_name = variant["name"]
            for option in variant["package_options"]:
                option_name = option["name"]
                price = option["price"]
                packages.append({
                    "number": option_number,
                    "variant_name": variant_name,
                    "option_name": option_name,
                    "price": price,
                    "code": option["package_option_code"],
                    "option_order": option["order"]
                })
                table.add_row(str(option_number), variant_name, option_name, f"Rp {price:,}")
                option_number += 1

        console.print(Panel(table, title="", border_style=_c("border_info"), padding=(1, 0), expand=True))
        console.print(f"[{_c('text_sub')}]00 untuk kembali ke menu utama[/{_c('text_sub')}]")
        choice = console.input(f"[{_c('text_sub')}]Pilih paket (nomor):[/{_c('text_sub')}] ").strip()

        if choice == "00":
            return None

        selected_pkg = next((p for p in packages if str(p["number"]) == choice), None)
        if not selected_pkg:
            pesan_error("Paket tidak ditemukan. Silakan coba lagi.")
            pause()
            continue

        is_done = show_package_details(
            api_key,
            tokens,
            selected_pkg["code"],
            is_enterprise,
            option_order=selected_pkg["option_order"]
        )
        if is_done:
            return None
# ===================================
def fetch_my_packages():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    if not tokens:
        console.print(f"[{_c('text_err')}]Token pengguna tidak ditemukan.[/{_c('text_err')}]")
        pause()
        return None

    id_token = tokens.get("id_token")
    path = "api/v8/packages/quota-details"
    payload = {
        "is_enterprise": False,
        "lang": "en",
        "family_member_id": ""
    }

    console.print(f"[{_c('text_sub')}]Mengambil daftar paket aktif...[/{_c('text_sub')}]")
    res = send_api_request(api_key, path, payload, id_token, "POST")
    if res.get("status") != "SUCCESS":
        console.print(f"[{_c('text_err')}]Gagal mengambil paket.[/{_c('text_err')}]")
        pause()
        return None

    quotas = res["data"]["quotas"]
    my_packages = []

    clear_screen()
    # Judul di tengah dalam box penuh layar
    console.print(Panel("[bold]Paket Saya[/bold]", style=_c("border_info"), padding=(0, 2), expand=True))

    # Tampilkan setiap paket dalam box individual
    for idx, quota in enumerate(quotas, 1):
        quota_code = quota["quota_code"]
        group_code = quota["group_code"]
        name = quota["name"]
        family_code = "N/A"

        package_details = get_package(api_key, tokens, quota_code)
        if package_details:
            family_code = package_details["package_family"]["package_family_code"]

        isi = f"""
[bold]{name}[/bold]
[dim]Nomor:[/] {idx}
[dim]Family Code:[/] {family_code}
[dim]Group Code:[/] {group_code}
[dim]Kode Paket:[/] {quota_code}
"""
        console.print(Panel(isi.strip(), border_style=_c("border_primary"), padding=(1, 2), expand=True))

        my_packages.append({
            "number": idx,
            "quota_code": quota_code,
        })

    # Input pilihan
    console.print(f"[{_c('text_sub')}]Masukkan nomor paket untuk membeli ulang, atau '00' untuk kembali.[/{_c('text_sub')}]")
    choice = console.input(f"[{_c('text_sub')}]Pilihan:[/{_c('text_sub')}] ").strip()

    if choice == "00":
        return None

    selected_pkg = next((pkg for pkg in my_packages if str(pkg["number"]) == choice), None)
    if not selected_pkg:
        console.print(f"[{_c('text_err')}]Paket tidak ditemukan. Silakan coba lagi.[/{_c('text_err')}]")
        pause()
        return None

    is_done = show_package_details(api_key, tokens, selected_pkg["quota_code"], False)
    if is_done:
        return None

    pause()

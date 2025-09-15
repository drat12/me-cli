import sys
import json

from app.service.auth import AuthInstance
from app.client.engsel import get_family, get_package, get_addons, purchase_package, send_api_request
from app.service.bookmark import BookmarkInstance
from app.client.purchase import show_multipayment, show_qris_payment, settlement_bounty
from app.menus.util import clear_screen, pause, display_html

def show_package_details(api_key, tokens, package_option_code, is_enterprise, option_order = -1):
    clear_screen()
    print("--------------------------")
    print("Detail Paket")
    print("--------------------------")
    package = get_package(api_key, tokens, package_option_code)
    if not package:
        print("Failed to load package details.")
        pause()
        return False

    variant_name = package.get("package_detail_variant", "").get("name","")
    price = package["package_option"]["price"]
    detail = display_html(package["package_option"]["tnc"])
    validity = package["package_option"]["validity"]
    option_name = package.get("package_option", {}).get("name","")
    family_name = package.get("package_family", {}).get("name","")
    title = f"{family_name} {variant_name} {option_name}".strip()
    item_name = f"{variant_name} {option_name}".strip()
    token_confirmation = package["token_confirmation"]
    ts_to_sign = package["timestamp"]
    payment_for = package["package_family"]["payment_for"]

    print("--------------------------")
    print(f"Nama: {title}")
    print(f"Harga: Rp {price}")
    print(f"Masa Aktif: {validity}")
    print("--------------------------")

    benefits = package["package_option"]["benefits"]
    if benefits and isinstance(benefits, list):
        print("Benefits:")
        for benefit in benefits:
            print("--------------------------")
            print(f" Name: {benefit['name']}")
            if "Call" in benefit['name']:
                print(f"  Total: {benefit['total']/60} menit")
            else:
                if benefit['total'] > 0:
                    quota = int(benefit['total'])
                    if quota >= 1_000_000_000:
                        quota_gb = quota / (1024 ** 3)
                        print(f"  Quota: {quota_gb:.2f} GB")
                    elif quota >= 1_000_000:
                        quota_mb = quota / (1024 ** 2)
                        print(f"  Quota: {quota_mb:.2f} MB")
                    elif quota >= 1_000:
                        quota_kb = quota / 1024
                        print(f"  Quota: {quota_kb:.2f} KB")
                    else:
                        print(f"  Total: {quota}")
    print("--------------------------")
    addons = get_addons(api_key, tokens, package_option_code)
    print(f"Addons:\n{json.dumps(addons, indent=2)}")
    print("--------------------------")
    print(f"SnK MyXL:\n{detail}")
    print("--------------------------")

    in_package_detail_menu = True
    while in_package_detail_menu:
        print("Options:")
        print("1. Beli dengan Pulsa")
        print("2. Beli dengan E-Wallet")
        print("3. Bayar dengan QRIS")
        if payment_for == "REDEEM_VOUCHER":
            print("4. Ambil sebagai bonus (jika tersedia)")
        if option_order != -1:
            print("0. Tambah ke Bookmark")
        print("00. Kembali ke daftar paket")

        choice = input("Pilihan: ")
        if choice == "00":
            return False
        if choice == "0" and option_order != -1:
            success = BookmarkInstance.add_bookmark(
                family_code=package.get("package_family", {}).get("package_family_code",""),
                family_name=package.get("package_family", {}).get("name",""),
                is_enterprise=is_enterprise,
                variant_name=variant_name,
                option_name=option_name,
                order=option_order,
            )
            if success:
                print("Paket berhasil ditambahkan ke bookmark.")
            else:
                print("Paket sudah ada di bookmark.")
            pause()
            continue
        if choice == '1':
            purchase_package(api_key, tokens, package_option_code, is_enterprise)
            input("Silahkan cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == '2':
            show_multipayment(api_key, tokens, package_option_code, token_confirmation, price, item_name)
            input("Silahkan lakukan pembayaran & cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == '3':
            show_qris_payment(api_key, tokens, package_option_code, token_confirmation, price, item_name)
            input("Silahkan lakukan pembayaran & cek hasil pembelian di aplikasi MyXL. Tekan Enter untuk kembali.")
            return True
        elif choice == '4':
            settlement_bounty(
                api_key=api_key,
                tokens=tokens,
                token_confirmation=token_confirmation,
                ts_to_sign=ts_to_sign,
                payment_target=package_option_code,
                price=price,
                item_name=variant_name
            )
        else:
            print("Purchase cancelled.")
            return False
    pause()
    sys.exit(0)

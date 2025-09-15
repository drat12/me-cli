import sys
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

    while True:
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

def get_packages_by_family(family_code: str, is_enterprise: bool = False):
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    if not tokens:
        print("No active user tokens found.")
        pause()
        return None

    packages = []
    data = get_family(api_key, tokens, family_code, is_enterprise)
    if not data:
        print("Failed to load family data.")
        return None

    while True:
        clear_screen()
        print("--------------------------")
        print("Paket Tersedia")
        print("--------------------------")
        family_name = data['package_family']["name"]
        print(f"Family Name: {family_name}")
        package_variants = data["package_variants"]

        option_number = 1
        variant_number = 1
        for variant in package_variants:
            variant_name = variant["name"]
            print(f" Variant {variant_number}: {variant_name}")
            for option in variant["package_options"]:
                option_name = option["name"]
                packages.append({
                    "number": option_number,
                    "variant_name": variant_name,
                    "option_name": option_name,
                    "price": option["price"],
                    "code": option["package_option_code"],
                    "option_order": option["order"]
                })
                print(f"{option_number}. {option_name} - Rp {option['price']}")
                option_number += 1
            variant_number += 1

        print("00. Kembali ke menu utama")
        pkg_choice = input("Pilih paket (nomor): ")
        if pkg_choice == "00":
            return None
        selected_pkg = next((p for p in packages if p["number"] == int(pkg_choice)), None)
        if not selected_pkg:
            print("Paket tidak ditemukan. Silakan masukan nomor yang benar.")
            continue

        is_done = show_package_details(api_key, tokens, selected_pkg["code"], is_enterprise, option_order=selected_pkg["option_order"])
        if is_done:
            return None

def fetch_my_packages():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    if not tokens:
        print("No active user tokens found.")
        pause()
        return None

    id_token = tokens.get("id_token")
    path = "api/v8/packages/quota-details"
    payload = {
        "is_enterprise": False,
        "lang": "en",
        "family_member_id": ""
    }

    print("Fetching my packages...")
    res = send_api_request(api_key, path, payload, id_token, "POST")
    if res.get("status") != "SUCCESS":
        print("Failed to fetch packages")
        print("Response:", res)
        pause()
        return None

    quotas = res["data"]["quotas"]
    clear_screen()
    print("===============================")
    print("My Packages")
    print("===============================")
    my_packages = []
    num = 1
    for quota in quotas:
        quota_code = quota["quota_code"]
        group_code = quota["group_code"]
        name = quota["name"]
        family_code = "N/A"
        print(f"fetching package no. {num} details...")
        package_details = get_package(api_key, tokens, quota_code)
        if package_details:
            family_code = package_details["package_family"]["package_family_code"]

        print("===============================")
        print(f"Package {num}")
        print(f"Name: {name}")
        print(f"Quota Code: {quota_code}")
        print(f"Family Code: {family_code}")
        print(f"Group Code: {group_code}")
        print("===============================")

        my_packages.append({
            "number": num,
            "quota_code": quota_code,
        })
        num += 1

    print("Rebuy package? Input package number to rebuy, or '00' to back.")
    choice = input("Choice: ")
    if choice == "00":
        return None

    selected_pkg = next((pkg for pkg in my_packages if str(pkg["number"]) == choice), None)
    if not selected_pkg:
        print("Paket tidak ditemukan. Silakan masukan nomor yang benar.")
        return None

    is_done = show_package_details(api_key, tokens, selected_pkg["quota_code"], False)
    if is_done:
        return None

    pause()

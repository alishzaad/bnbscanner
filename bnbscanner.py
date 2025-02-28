import os
import hashlib
import ecdsa
import requests
import sys
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init

# Initialize colorama
init()

# --- توابع تولید آدرس‌های BNB Smart Chain ---
def generate_private_key():
    return os.urandom(32).hex()  # کلید خصوصی به صورت Hex

def generate_bnb_smart_chain_address(private_hex):
    # تبدیل کلید خصوصی به کلید عمومی
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(private_hex), curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    pub_key = b'\x04' + vk.to_string()
    
    # تولید آدرس Ethereum-style (با Keccak-256)
    keccak_hash = hashlib.sha3_256(pub_key).digest()
    address = '0x' + keccak_hash[-20:].hex()
    
    return address

# --- بررسی موجودی با ThreadPool ---
def check_bnb_balance(address):
    try:
        # استفاده از API BSCScan برای بررسی موجودی BNB
        api_key = "U1TC18JTBPFC85B5J9N81J4P5XI48275YX"  # API Key شما
        response = requests.get(
            f"https://api.bscscan.com/api?module=account&action=balance&address={address}&tag=latest&apikey={api_key}",
            timeout=10,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response.raise_for_status()  # بررسی خطاهای HTTP
        balance = int(response.json().get('result', 0))
        return balance
    except requests.exceptions.RequestException as e:
        return f"{Fore.RED}Error: {e}{Style.RESET_ALL}"  # نمایش خطا با رنگ قرمز

def check_addresses(address):
    with ThreadPoolExecutor(max_workers=4) as executor:
        future = executor.submit(check_bnb_balance, address)
        return future.result()

# --- اجرای اصلی ---
def main():
    try:
        while True:
            private_hex = generate_private_key()
            address = generate_bnb_smart_chain_address(private_hex)
            
            # بررسی موجودی برای آدرس BNB
            balance = check_addresses(address)
            
            # نمایش اطلاعات در ترمینال
            status = f"Private Key: {private_hex} | BNB Address: {address} | Balance: {balance if isinstance(balance, int) else balance}"
            print(status)
            
            # بررسی موجودی و خطاها
            if isinstance(balance, int) and balance > 0:
                print(f"\n{Fore.GREEN}!!! موجودی یافت شد !!!{Style.RESET_ALL}")
                print(f"کلید خصوصی (Hex): {private_hex}")
                print(f"آدرس BNB: {address}")
                print(f"موجودی: {balance} wei")  # موجودی به صورت wei نمایش داده می‌شود
                
                # ذخیره اطلاعات در فایل
                with open('found_bnb_smart_chain.txt', 'a') as f:
                    f.write(f"Private Key (Hex): {private_hex}\n")
                    f.write(f"BNB Address: {address}\n")
                    f.write(f"Balance: {balance} wei\n\n")
                sys.exit(0)
            elif isinstance(balance, str):  # نمایش خطاها
                print(f"{Fore.RED}!!! خطا !!!{Style.RESET_ALL}")
                print(f"آدرس BNB: {address}")
                print(f"خطا: {balance}")
                
    except KeyboardInterrupt:
        print("\n\nعملیات توسط کاربر لغو شد.")

if __name__ == "__main__":
    print("""
    ░█████╗░░█████╗░██╗░░░██╗██████╗░███████╗
    ██╔══██╗██╔══██╗██║░░░██║██╔══██╗██╔════╝
    ██║░░╚═╝██║░░██║██║░░░██║██████╦╝█████╗░░
    ██║░░██╗██║░░██║██║░░░██║██╔══██╗██╔══╝░░
    ╚█████╔╝╚█████╔╝╚██████╔╝██████╦╝███████╗
    ░╚════╝░░╚════╝░░╚═════╝░╚═════╝░╚══════╝
    """)
    main()

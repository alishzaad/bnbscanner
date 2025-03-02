import os
import hashlib
import ecdsa
import requests
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init
import threading

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

# --- بررسی موجودی BNB ---
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

# --- شمارنده و قفل برای هماهنگی در چاپ ---
counter = 0
counter_lock = threading.Lock()

def process_address():
    global counter
    private_hex = generate_private_key()
    address = generate_bnb_smart_chain_address(private_hex)
    balance = check_bnb_balance(address)
    
    with counter_lock:
        counter += 1
        current_count = counter

    # آماده‌سازی رشته خروجی با استفاده از شمارنده
    if isinstance(balance, int):
        status = f"#{current_count} | Private Key: {private_hex} | BNB Address: {address} | Balance: {balance} wei"
    else:
        status = f"#{current_count} | Private Key: {private_hex} | BNB Address: {address} | Balance: {balance}"
    print(status)

    # در صورت یافتن موجودی مثبت، اطلاعات ذخیره شده و برنامه خاتمه می‌یابد
    if isinstance(balance, int) and balance > 0:
        print(f"\n{Fore.GREEN}!!! موجودی یافت شد !!!{Style.RESET_ALL}")
        print(f"کلید خصوصی (Hex): {private_hex}")
        print(f"آدرس BNB: {address}")
        print(f"موجودی: {balance} wei")
        
        with open('found_bnb_smart_chain.txt', 'a') as f:
            f.write(f"Private Key (Hex): {private_hex}\n")
            f.write(f"BNB Address: {address}\n")
            f.write(f"Balance: {balance} wei\n\n")
        sys.exit(0)

def main():
    try:
        # استفاده از ThreadPoolExecutor برای اجرای همزمان تسک‌ها
        with ThreadPoolExecutor(max_workers=10) as executor:
            while True:
                # در هر ثانیه ۵ آدرس تولید و بررسی می‌شود
                for _ in range(5):
                    executor.submit(process_address)
                time.sleep(1)
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

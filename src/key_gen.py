from cryptography.fernet import Fernet
from datetime import datetime
import os

def generate_key(name):
    key = Fernet.generate_key()
    with open(f'./keys/{name}_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.key', 'wb') as key_file:
        key_file.write(key)

def get_key(name):
    key_file_name = f"./keys/{name}.key"
    if not os.path.exists(key_file_name):
        return
    with open(key_file_name, 'rb') as key_file:
        return key_file.read()

if __name__ == "__main__":
    generate_key("renault")
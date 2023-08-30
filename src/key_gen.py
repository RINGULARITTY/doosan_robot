from cryptography.fernet import Fernet
from datetime import datetime
import os
from path_changer import resource_path

class KeyGen:
    KEYS_FOLDER = resource_path("keys")

    @staticmethod
    def generate_key(name):
        key = Fernet.generate_key()
        with open(os.path.join(KeyGen.KEYS_FOLDER, f'{name}_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.key'), 'wb') as key_file:
            key_file.write(key)

    @staticmethod
    def get_key(name):
        key_file_name = os.path.join(KeyGen.KEYS_FOLDER, f"{name}.key")
        if not os.path.exists(key_file_name):
            raise "Invalid key"
        with open(key_file_name, 'rb') as key_file:
            return key_file.read()
    
    @staticmethod
    def get_default_key():
        key_files = [f for f in os.listdir(KeyGen.KEYS_FOLDER) if f.split(".")[-1] == "key"]
        if len(key_files) == 0:
            return
        with open(os.path.join(KeyGen.KEYS_FOLDER, f"{key_files[0]}"), 'rb') as key_file:
            return key_file.read()

if __name__ == "__main__":
    KeyGen.generate_key("main")
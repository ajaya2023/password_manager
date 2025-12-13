import base64
from cryptography.fernet import Fernet

class KeyManager:
    def __init__(self, key_file='master.key'):
        self.key_file = key_file
        self.key = self.load_key()

    def generate_key(self):
        key = Fernet.generate_key()
        with open(self.key_file, 'wb') as f:
            f.write(key)
        self.key = key
        return key

    def load_key(self):
        try:
            with open(self.key_file, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            return self.generate_key()

    def change_key(self, old_key, new_key, data_list):
        """
        Re-encrypt all passwords using the new key.
        data_list: list of encrypted password entries (bytes)
        """
        old_fernet = Fernet(old_key)
        new_fernet = Fernet(new_key)
        updated_data = []

        for enc in data_list:
            decrypted = old_fernet.decrypt(enc)
            re_encrypted = new_fernet.encrypt(decrypted)
            updated_data.append(re_encrypted)

        with open(self.key_file, 'wb') as f:
            f.write(new_key)
        self.key = new_key

        return updated_data

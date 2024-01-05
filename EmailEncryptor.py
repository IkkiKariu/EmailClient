from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP


class EmailEncryptor:
    @staticmethod
    def generate_key_pair(dir_path: str):
        key = RSA.generate(2048)
        private_key = key.export_key()
        file_out = open(f"{dir_path}\\private.pem", "wb")
        file_out.write(private_key)
        file_out.close()

        public_key = key.publickey().export_key()
        file_out = open(f"{dir_path}\\public.pem", "wb")
        file_out.write(public_key)
        file_out.close()

    @staticmethod
    def encrypt_data(data: str, path_to_public_key: str):
        data = data.encode("utf-8")
        file_out = open(f"SendingEmailData\\EncryptedMessage\\encrypted_data.bin", "wb")

        recipient_key = RSA.import_key(open(path_to_public_key).read())
        session_key = get_random_bytes(16)

        # Encrypt the session key with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        enc_session_key = cipher_rsa.encrypt(session_key)

        # Encrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)
        [file_out.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]
        file_out.close()

    @staticmethod
    def decrypt_message(path_to_private_key: str) -> str:
        file_in = open("tmpEncryptedMessage\\encrypted_data.bin", "rb")

        private_key = RSA.import_key(open(path_to_private_key).read())

        enc_session_key, nonce, tag, ciphertext = \
            [file_in.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1)]
        file_in.close()

        # Decrypt the session key with the private RSA key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        # Decrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
        return data.decode("utf-8")

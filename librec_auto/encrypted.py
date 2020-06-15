from cryptography.fernet import Fernet

def generate_key():
    key = Fernet.generate_key()
    file = open("/Users/liuzijun1/Desktop/Librec-auto/librec-auto-library/librec_auto/cmd/post/key.key", "wb")
    file.write(key)
    file.close()

def encrypted_file():
    file = open("/Users/liuzijun1/Desktop/Librec-auto/librec-auto-library/librec_auto/cmd/post/key.key", "rb")
    key = file.read()
    file.close()

    with open("/Users/liuzijun1/Desktop/Librec-auto/librec-auto-library/librec_auto/cmd/post/Key_API.txt", "rb") as api:
        data = api.read()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    with open("/Users/liuzijun1/Desktop/Librec-auto/librec-auto-library/librec_auto/cmd/post/Key_API.txt.encrypted", "wb") as encry:
        encry.write(encrypted)

def encrypted_file_dropbox():
    file = open("/Users/liuzijun1/Desktop/Librec-auto/librec-auto-library/librec_auto/cmd/post/key.key", "rb")
    key = file.read()
    file.close()

    with open("/Users/liuzijun1/Desktop/Librec-auto/librec-auto-library/librec_auto/cmd/post/Key_API_Dropbox.txt", "rb") as api:
        data = api.read()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    with open("/Users/liuzijun1/Desktop/Librec-auto/librec-auto-library/librec_auto/cmd/post/Key_API_Dropbox.txt.encrypted", "wb") as encry:
        encry.write(encrypted)

generate_key()
encrypted_file()
encrypted_file_dropbox()

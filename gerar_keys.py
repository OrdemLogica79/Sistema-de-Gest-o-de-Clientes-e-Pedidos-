from cryptography.fernet import Fernet
import secrets


def gerar_secret_key() -> str:
    return secrets.token_urlsafe(32)


def gerar_chave_fernet() -> str:
    return Fernet.generate_key().decode()


if __name__ == "__main__":
    print(f"SECRET_KEY={gerar_secret_key()}")
    print(f"CHAVE_F={gerar_chave_fernet()}")

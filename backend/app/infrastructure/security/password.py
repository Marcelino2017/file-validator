from passlib.context import CryptContext

from app.domain.interfaces import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    def __init__(self) -> None:
        self._pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

    def hash(self, plain_password: str) -> str:
        return self._pwd_context.hash(plain_password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self._pwd_context.verify(plain_password, hashed_password)

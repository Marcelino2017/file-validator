from __future__ import annotations

from dataclasses import dataclass
import re

from app.application.exceptions import ConflictError, UnauthorizedError, ValidationError
from app.domain.entities import Enterprise, User
from app.domain.interfaces import (
    EnterpriseRepository,
    PasswordHasher,
    TokenProvider,
    UserRepository,
)


CEDULA_REGEX = re.compile(r"^[0-9]{6,12}$")
NIT_REGEX = re.compile(r"^[0-9]{9,15}(-[0-9])?$")


@dataclass(slots=True)
class RegisterUserInput:
    first_name: str
    last_name: str
    cedula: str
    enterprise_name: str
    nit: str
    password: str


@dataclass(slots=True)
class LoginInput:
    cedula: str
    password: str


@dataclass(slots=True)
class AuthResult:
    access_token: str
    token_type: str
    user_id: int
    cedula: str


class RegisterUser:
    def __init__(
        self,
        user_repo: UserRepository,
        enterprise_repo: EnterpriseRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repo = user_repo
        self._enterprise_repo = enterprise_repo
        self._password_hasher = password_hasher

    def execute(self, payload: RegisterUserInput) -> User:
        if not CEDULA_REGEX.fullmatch(payload.cedula):
            raise ValidationError("Formato de cédula inválido")
        if not NIT_REGEX.fullmatch(payload.nit):
            raise ValidationError("Formato de NIT inválido")

        existing_user = self._user_repo.get_by_cedula(payload.cedula)
        if existing_user:
            raise ConflictError("La cédula ya está registrada")

        enterprise = self._enterprise_repo.get_by_nit(payload.nit)
        if not enterprise:
            enterprise = self._enterprise_repo.create(
                Enterprise(name=payload.enterprise_name, nit=payload.nit)
            )

        hashed_password = self._password_hasher.hash(payload.password)
        user = User(
            first_name=payload.first_name,
            last_name=payload.last_name,
            cedula=payload.cedula,
            hashed_password=hashed_password,
            enterprise_id=enterprise.id or 0,
        )
        return self._user_repo.create(user)


class LoginUser:
    def __init__(
        self,
        user_repo: UserRepository,
        password_hasher: PasswordHasher,
        token_provider: TokenProvider,
    ) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher
        self._token_provider = token_provider

    def execute(self, payload: LoginInput) -> AuthResult:
        user = self._user_repo.get_by_cedula(payload.cedula)
        if not user:
            raise UnauthorizedError("Credenciales inválidas")

        is_valid_password = self._password_hasher.verify(
            payload.password, user.hashed_password
        )
        if not is_valid_password:
            raise UnauthorizedError("Credenciales inválidas")

        access_token = self._token_provider.create_access_token(subject=str(user.id))
        return AuthResult(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id or 0,
            cedula=user.cedula,
        )

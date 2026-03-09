from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.application.auth_service import LoginUser, RegisterUser
from app.application.exceptions import UnauthorizedError
from app.application.pdf_service import ValidateAndUploadPDF
from app.domain.entities import User
from app.domain.interfaces import (
    EnterpriseRepository,
    FileStorage,
    FileValidatorFactory,
    PasswordHasher,
    PDFRepository,
    TokenProvider,
    UserRepository,
)
from app.infrastructure.database.repositories import (
    SQLAlchemyEnterpriseRepository,
    SQLAlchemyPDFRepository,
    SQLAlchemyUserRepository,
)
from app.infrastructure.database.session import get_db_session
from app.infrastructure.security.jwt_provider import JoseJWTTokenProvider
from app.infrastructure.security.password import BcryptPasswordHasher
from app.infrastructure.storage.local_storage import LocalDiskStorage
from app.infrastructure.storage.validators import SimpleFileValidatorFactory


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_user_repo(session: Session = Depends(get_db_session)) -> UserRepository:
    return SQLAlchemyUserRepository(session)


def get_enterprise_repo(
    session: Session = Depends(get_db_session),
) -> EnterpriseRepository:
    return SQLAlchemyEnterpriseRepository(session)


def get_pdf_repo(session: Session = Depends(get_db_session)) -> PDFRepository:
    return SQLAlchemyPDFRepository(session)


def get_password_hasher() -> PasswordHasher:
    return BcryptPasswordHasher()


def get_token_provider() -> TokenProvider:
    return JoseJWTTokenProvider()


def get_storage() -> FileStorage:
    return LocalDiskStorage()


def get_validator_factory() -> FileValidatorFactory:
    return SimpleFileValidatorFactory()


def get_register_user_use_case(
    user_repo: UserRepository = Depends(get_user_repo),
    enterprise_repo: EnterpriseRepository = Depends(get_enterprise_repo),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> RegisterUser:
    return RegisterUser(user_repo, enterprise_repo, password_hasher)


def get_login_user_use_case(
    user_repo: UserRepository = Depends(get_user_repo),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_provider: TokenProvider = Depends(get_token_provider),
) -> LoginUser:
    return LoginUser(user_repo, password_hasher, token_provider)


def get_upload_pdf_use_case(
    user_repo: UserRepository = Depends(get_user_repo),
    pdf_repo: PDFRepository = Depends(get_pdf_repo),
    storage: FileStorage = Depends(get_storage),
    validator_factory: FileValidatorFactory = Depends(get_validator_factory),
) -> ValidateAndUploadPDF:
    return ValidateAndUploadPDF(user_repo, pdf_repo, storage, validator_factory)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    token_provider: TokenProvider = Depends(get_token_provider),
    user_repo: UserRepository = Depends(get_user_repo),
) -> User:
    try:
        subject = token_provider.get_subject(token)
        user_id = int(subject)
    except (ValueError, UnauthorizedError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        ) from exc

    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autorizado",
        )
    return user

from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.entities import Enterprise, PDFDocument, User
from app.domain.interfaces import EnterpriseRepository, PDFRepository, UserRepository
from app.infrastructure.database.models import EnterpriseModel, PDFDocumentModel, UserModel


def _to_enterprise_entity(model: EnterpriseModel) -> Enterprise:
    return Enterprise(
        id=model.id,
        name=model.name,
        nit=model.nit,
        created_at=model.created_at,
    )


def _to_user_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        first_name=model.first_name,
        last_name=model.last_name,
        cedula=model.cedula,
        hashed_password=model.hashed_password,
        enterprise_id=model.enterprise_id,
        created_at=model.created_at,
    )


def _to_pdf_entity(model: PDFDocumentModel) -> PDFDocument:
    return PDFDocument(
        id=model.id,
        filename=model.filename,
        mime_type=model.mime_type,
        storage_path=model.storage_path,
        sha256=model.sha256,
        user_id=model.user_id,
        enterprise_id=model.enterprise_id,
        created_at=model.created_at,
    )


class SQLAlchemyEnterpriseRepository(EnterpriseRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_nit(self, nit: str) -> Enterprise | None:
        model = self._session.query(EnterpriseModel).filter_by(nit=nit).first()
        if not model:
            return None
        return _to_enterprise_entity(model)

    def create(self, enterprise: Enterprise) -> Enterprise:
        model = EnterpriseModel(name=enterprise.name, nit=enterprise.nit)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return _to_enterprise_entity(model)


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_cedula(self, cedula: str) -> User | None:
        model = self._session.query(UserModel).filter_by(cedula=cedula).first()
        if not model:
            return None
        return _to_user_entity(model)

    def get_by_id(self, user_id: int) -> User | None:
        model = self._session.query(UserModel).filter_by(id=user_id).first()
        if not model:
            return None
        return _to_user_entity(model)

    def create(self, user: User) -> User:
        model = UserModel(
            first_name=user.first_name,
            last_name=user.last_name,
            cedula=user.cedula,
            hashed_password=user.hashed_password,
            enterprise_id=user.enterprise_id,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return _to_user_entity(model)


class SQLAlchemyPDFRepository(PDFRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, document: PDFDocument) -> PDFDocument:
        model = PDFDocumentModel(
            filename=document.filename,
            mime_type=document.mime_type,
            storage_path=document.storage_path,
            sha256=document.sha256,
            user_id=document.user_id,
            enterprise_id=document.enterprise_id,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return _to_pdf_entity(model)

"""
Implementación del Patrón Repository (GoF) para la entidad Usuario (UserModel).
Aísla la persistencia de usuarios y roles del resto del sistema.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.domain.models.user import UserModel


class UserRepositoryInterface(ABC):
    """
    Interfaz abstracta del repositorio de Usuarios (Repository Pattern).
    """

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        """Recupera un usuario por su ID primario."""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserModel]:
        """Recupera un usuario por su correo corporativo."""
        pass

    @abstractmethod
    def get_all(self, role: Optional[str] = None) -> List[UserModel]:
        """Lista todos los usuarios, con filtro opcional por rol."""
        pass

    @abstractmethod
    def create(self, user: UserModel) -> UserModel:
        """Persiste un nuevo usuario en la base de datos."""
        pass

    @abstractmethod
    def update(self, user: UserModel) -> UserModel:
        """Actualiza un usuario existente."""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Elimina un usuario por su identificador."""
        pass


class SQLAlchemyUserRepository(UserRepositoryInterface):
    """
    Implementación concreta de UserRepositoryInterface utilizando SQLAlchemy ORM.
    """

    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        return self._session.query(UserModel).filter(UserModel.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self._session.query(UserModel).filter(UserModel.email == email.strip().lower()).first()

    def get_all(self, role: Optional[str] = None) -> List[UserModel]:
        query = self._session.query(UserModel)
        if role:
            query = query.filter(UserModel.role == role.upper())
        return query.order_by(UserModel.full_name.asc()).all()

    def create(self, user: UserModel) -> UserModel:
        user.email = user.email.strip().lower()
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user

    def update(self, user: UserModel) -> UserModel:
        if user.email:
            user.email = user.email.strip().lower()
        self._session.merge(user)
        self._session.commit()
        self._session.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            return False
        self._session.delete(user)
        self._session.commit()
        return True


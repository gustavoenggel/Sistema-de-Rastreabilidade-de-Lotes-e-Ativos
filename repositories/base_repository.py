from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from Database.conexao import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def buscar_por_id(self, id_) -> Optional[ModelType]:
        return self.db.get(self.model, id_)

    def listar_todos(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.db.scalars(stmt).all())

    def criar(self, objeto: ModelType) -> ModelType:
        self.db.add(objeto)
        self.db.commit()
        self.db.refresh(objeto)
        return objeto

    def deletar(self, id_) -> bool:
        registro = self.buscar_por_id(id_)
        if registro:
            self.db.delete(registro)
            self.db.commit()
            return True
        return False
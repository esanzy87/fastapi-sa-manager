from typing import Type, TypeVar, Generic
from pydantic import BaseModel as BaseSchema
from sqlalchemy.orm import DeclarativeBase as BaseModel
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.elements import ClauseElement
from .schemas import PaginatedList


ModelT = TypeVar("ModelT", bound=BaseModel)
ListItemSchemaT = TypeVar("ListItemSchemaT", bound=BaseSchema)
DetailSchemaT = TypeVar("DetailSchemaT", bound=BaseSchema)
CreationPayloadT = TypeVar("CreationPayloadT", bound=BaseSchema)
UpdatePayloadT = TypeVar("UpdatePayloadT", bound=BaseSchema)


class BaseModelService(
    Generic[ModelT, ListItemSchemaT, DetailSchemaT, CreationPayloadT, UpdatePayloadT]
):
    db: Session
    model_class: Type[ModelT]
    list_item_schema: Type[ListItemSchemaT]
    detail_schema: Type[DetailSchemaT]
    autocommit: bool = False

    def __init__(
        self,
        db: Session,
        model_class: Type[ModelT],
        list_item_schema: Type[ListItemSchemaT],
        detail_schema: Type[DetailSchemaT],
        autocommit: bool = False,
    ):
        self.db = db
        self.model_class = model_class
        self.list_item_schema = list_item_schema
        self.detail_schema = detail_schema
        self.autocommit = autocommit

    def get_instance(self, detail_id: int, raises_exc=True) -> ModelT:
        from sqlalchemy.sql.expression import select

        stmt_0 = select(self.model_class).filter_by(id=detail_id)

        if raises_exc:
            return self.db.execute(stmt_0).scalar_one()
        else:
            return self.db.execute(stmt_0).scalar_one_or_none()

    def get_list_item_from_instance(self, instance: ModelT) -> ListItemSchemaT:
        return self.list_item_schema.from_orm(instance)

    def get_paginated_list(
        self, stmt: ClauseElement, page: int = 0, per_page: int = 20
    ) -> PaginatedList[ListItemSchemaT]:
        from sqlalchemy.sql.expression import select
        from sqlalchemy.sql.functions import count

        total_count = self.db.execute(
            select(count()).select_from(stmt.subquery())
        ).scalar_one()

        if per_page > -1:
            results = self.db.scalars(
                stmt.offset(page * per_page).limit(per_page)
            ).all()
        else:
            results = self.db.scalars(stmt).all()

        return PaginatedList(
            total_count=total_count,
            results=[self.get_list_item_from_instance(result) for result in results],
            page=page,
            per_page=per_page if per_page > -1 else total_count,
        )

    def get_detail_from_instance(self, instance: ModelT) -> DetailSchemaT:
        return self.detail_schema.from_orm(instance)

    def get_detail(self, detail_id: int) -> DetailSchemaT:
        instance = self.get_instance(detail_id)
        return self.get_detail_from_instance(instance)

    def create(self, payload: CreationPayloadT) -> ModelT:
        instance = self.model_class(**payload.dict())
        self.db.add(instance)

        if self.autocommit:
            self.db.commit()
        else:
            self.db.flush()
        self.db.refresh(instance)
        return instance

    def update(self, detail_id: int, payload: UpdatePayloadT) -> ModelT:
        instance = self.get_instance(detail_id)
        for field, value in payload:
            setattr(instance, field, value)

        if self.autocommit:
            self.db.commit()
        else:
            self.db.flush()
        self.db.refresh(instance)
        return instance

    def delete(self, detail_id: int) -> None:
        from sqlalchemy.sql.expression import delete

        stmt_0 = delete(self.model_class).filter_by(id=detail_id)
        self.db.execute(stmt_0)

        if self.autocommit:
            self.db.commit()
        else:
            self.db.flush()

        return

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.document import Document


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, document: Document) -> None:
        self.db.add(document)

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, document: Document) -> None:
        self.db.refresh(document)

    def get_by_id(self, document_id: UUID) -> Document | None:
        return self.db.scalar(
            select(Document).where(Document.id == document_id)
        )

    def get_by_owner(self, owner_id: UUID) -> list[Document]:
        return list(
            self.db.scalars(
                select(Document)
                .where(Document.owner_id == owner_id)
                .order_by(Document.created_at.desc())
            )
        )

    def delete(self, document: Document) -> None:
        self.db.delete(document)
        self.db.commit()
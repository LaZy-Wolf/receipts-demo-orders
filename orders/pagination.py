from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session


def paginate(session: Session, stmt: Select, page: int, size: int, schema: type[BaseModel]) -> dict:
    """Run `stmt` for one page and describe the whole result set."""
    total = session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = session.scalars(stmt.offset((page - 1) * size).limit(size)).all()
    return {
        "items": [schema.model_validate(row) for row in rows],
        "total": total,
        "page": page,
        "size": size,
        "pages": -(-total // size),  # ceiling division
    }

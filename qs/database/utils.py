from uuid import uuid4
import typing as t

if t.TYPE_CHECKING:
    from qs.database.types import Index


def new_index() -> "Index":
    return str(uuid4())

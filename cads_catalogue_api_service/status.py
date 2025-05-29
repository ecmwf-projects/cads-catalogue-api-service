import cads_catalogue.database
import fastapi
import sqlalchemy
from sqlalchemy.orm import Session

from .dependencies import get_session
from .models.status import CatalogueUpdateStatus

router = fastapi.APIRouter()


@router.get(
    "/status",
    response_model=list[CatalogueUpdateStatus],
    include_in_schema=False,
)
def get_catalogue_status(
    session: Session = fastapi.Depends(get_session),
) -> list[cads_catalogue.database.CatalogueUpdate]:
    """Retrieve all catalogue update statuses."""
    statement = sqlalchemy.select(cads_catalogue.database.CatalogueUpdate)
    results = session.execute(statement).scalars().all()
    return list(results)

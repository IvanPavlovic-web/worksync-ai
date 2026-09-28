from fastapi import APIRouter, Query

from app.services.meili import search


router = APIRouter()


@router.get("")
def search_jobs(
    q: str = Query("", min_length=0),
    work_mode: str | None = None,
    category: str | None = None,
    limit: int = 30,
):
    filters = []
    if work_mode:
        filters.append(f'work_mode = "{work_mode}"')
    if category:
        filters.append(f'category = "{category}"')
    filter_str = " AND ".join(filters) if filters else None
    return search(q, limit=limit, filters=filter_str)
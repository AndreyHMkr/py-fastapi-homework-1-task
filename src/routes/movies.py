import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db, MovieModel
from src.schemas import MovieListResponseSchema, MovieDetailResponseSchema

router = APIRouter()
movie_router = router


@router.get("/movies/", response_model=MovieListResponseSchema)
async def get_movies(
        page: int = Query(1, ge=1),
        per_page: int = Query(ge=1, le=20, default=10),
        db: AsyncSession = Depends(get_db),
):
    count_stmt = select(func.count()).select_from(MovieModel)
    result = await db.execute(count_stmt)
    total_items = result.scalar()

    total_pages = math.ceil(total_items / per_page)
    offset = (page - 1) * per_page

    stmt = select(MovieModel).offset(offset).limit(per_page)
    result = await db.execute(stmt)
    movies = result.scalars().all()

    if not movies:
        raise HTTPException(status_code=404, detail="No movies found.")

    prev_page = f"/theater/movies/?page={max(1, page - 1)}&per_page={per_page}" if page > 1 else None
    next_page = (f"/theater/movies/?page={min(total_pages, page + 1)}"
                 f"&per_page={per_page}") if page < total_pages else None

    return {
        "movies": movies,
        "prev_page": prev_page,
        "next_page": next_page,
        "total_pages": total_pages,
        "total_items": total_items,
    }


@router.get("/movies/{movie_id}", response_model=MovieDetailResponseSchema)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MovieModel).where(MovieModel.id == movie_id))
    movie = result.scalar_one_or_none()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie with id {movie_id} not found")
    return movie

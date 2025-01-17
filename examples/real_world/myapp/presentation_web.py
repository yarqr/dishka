from typing import Annotated

from fastapi import APIRouter

from dishka.integrations.fastapi import (
    Depends,
    inject,
)
from myapp.use_cases import AddProductsInteractor

router = APIRouter()


@router.get("/")
@inject
async def add_product(
        *,
        interactor: Annotated[AddProductsInteractor, Depends()],
) -> str:
    interactor(user_id=1)
    return "Ok"

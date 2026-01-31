from pydantic import BaseModel
from typing import List

class SubCategory(BaseModel):
    id: int
    name: str

class Category(BaseModel):
    id: int
    name: str
    sub: List[SubCategory]

class CategoryAllResponse(BaseModel):
    retval: int
    retdesc: str
    category: List[Category]

from typing import List
from pydantic import BaseModel

class TitleAndId(BaseModel):

    title: str

    id: str

    imgs: List[str] = []


class SearchResult(BaseModel):

    datas: List[TitleAndId]

    pageNum: int
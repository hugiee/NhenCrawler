from typing import List
from pydantic import BaseModel

class TitleAndId(BaseModel):

    title: str

    id: str


class SearchResult(BaseModel):

    datas: List[TitleAndId]

    pageNum: int
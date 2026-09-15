from pydantic import BaseModel

class CategorySchema(BaseModel):
    id: str
    name: str
    slug: str

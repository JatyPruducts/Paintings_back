from pydantic import BaseModel

class TotalCountResponse(BaseModel):
    total: int
from pydantic import BaseModel


class CreateRepoRequest(BaseModel):
    owner: str
    name: str
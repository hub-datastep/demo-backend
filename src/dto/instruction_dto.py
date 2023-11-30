from pydantic import BaseModel


class InstructionDto(BaseModel):
    id: int
    notion_page_id: str

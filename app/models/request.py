from pydantic import BaseModel, field_validator

class QueryRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        # 1. Strip whitespace
        cleaned = value.strip()

        # 2. Check if empty
        if not cleaned:
            raise ValueError("Question cannot be empty")

        # 3. Return cleaned value
        return cleaned


class QueryResponse(BaseModel):
    question: str      # original user question
    sql: str           # generated SQL query
    columns: list[str] # column names from result
    rows: list[list]   # actual data rows
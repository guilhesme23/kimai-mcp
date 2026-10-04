from pydantic import BaseModel, Field

class Customer(BaseModel):
    id: int = Field(description="ID of the customer")
    name: str = Field(description="Name of the customer")
    
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T] = Field(description="Entries of the current page")
    page: int = Field(description="Current page number, starting at 1")
    size: int = Field(description="Maximum number of entries per page")
    total_items: int = Field(description="Total number of entries matching the search, across all pages")
    total_pages: int = Field(description="Total number of pages for the search")
    remaining_pages: int = Field(description="Number of pages after the current one")
    has_next_page: bool = Field(description="Whether there is a page after the current one")

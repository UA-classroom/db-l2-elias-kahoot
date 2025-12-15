from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

"""
This module defines the Pydantic models (schemas) for the API.

These schemas are used to validate and structure the data for users and the quizzes. 
It ennsures that the incoming and the outgoing data meet the expected format and types.

Classes:
- UserBase, UserCreate, UserOut: Schemas for user-data.
- QuizBase, QuizCreate, QuizOut: Schemas for quiz-data.
"""


class UserBase(BaseModel):
    username: str
    email: EmailStr       # Creates a valid type for emails that looks like: (something@example.com). Other types will be rejected (FastAPI automatically returns a 422 Validation Error)
    role: str


class UserCreate(UserBase):
    password: str         # plain password from client


class UserOut(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None # Optional means "this field can be missing or None"
    visibility: Optional[str] = None  # 'public' or 'private'


class QuizCreate(QuizBase):
    creator_id: int


class QuizOut(QuizBase):
    id: int
    creator_id: int
    created_at: datetime               # Used for timestamps.
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

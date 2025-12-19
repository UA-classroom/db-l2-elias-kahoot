from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

"""
This module defines the Pydantic models (schemas) for the API.

These schemas are used to check and organize the data for users and quizzes.
They make sure that data sent to and from the API has the correct format and types.


The models in this file describe:
- Users (teachers, hosts, and players).
- Quizzes and their questions.
- Answer options for questions.
- Live quiz sessions.
- Players participating in a session.
- Answers entered during a session.
"""


# ----- USERS -----
# Represents people that are using the system (teachers, hosts and players)

class UserBase(BaseModel):
    # Core user fields shared between input and output
    username: str
    email: EmailStr       # Must be a valid email (FastAPI returns 422 if invalid)
    role: str             # admin / teacher / player


class UserCreate(UserBase):
    # Used when creating a user (POST /users)
    password: str         # Plain password from client (hashed before storing)


class UserOut(UserBase):
    # Used when returning user data to the client
    id: int               # Database-generated ID
    created_at: datetime  # Timestamp from database

    model_config = ConfigDict(from_attributes=True)    # Makes sure data from the database works with this model


# ----- QUIZZES -----
# A quiz is created by a host or teacher.
# One quiz can have many questions and many live sessions.

class QuizBase(BaseModel):
    # Core quiz fields shared between input and output
    title: str
    description: Optional[str] = None
    visibility: Optional[str] = None  # public or private


class QuizCreate(QuizBase):
    # Used when creating a quiz (POST /quizzes)
    creator_id: int


class QuizOut(QuizBase):
    # Used when returning quizzes to clients
    id: int
    creator_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# ----- QUESTIONS -----
# Questions belong to a quiz.
# One quiz can have many questions.

class QuestionBase(BaseModel):
    # Core question fields
    question_text: str            # Text shown to players
    question_type: str            # multiple_choice or True/False
    time_limit_seconds: Optional[int] = None
    points: Optional[int] = None
    sort_order: Optional[int] = None  # Order in the quiz


class QuestionCreate(QuestionBase):
    # Used when creating a question
    quiz_id: int


class QuestionOut(QuestionBase):
    # Used when returning questions from the API
    id: int
    quiz_id: int

    model_config = ConfigDict(from_attributes=True)


# ----- SESSIONS -----
# A session represents a live quiz.
# Players join a session using the join code.

class SessionCreate(BaseModel):
    # Used when creating a quiz session
    quiz_id: int
    host_id: int
    join_code: str


class SessionOut(BaseModel):
    # Used when returning session data to clients
    id: int
    quiz_id: int
    host_id: int
    join_code: str
    status: str                 # waiting / in_progress / finished
    started_at: datetime
    finished_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SessionStatusUpdate(BaseModel):
    # Used when updating the session status
    status: str                 # waiting / in_progress / finished


# ----- ANSWER OPTIONS -----
# Represents the possible answers for a question.
# One question can have many answer options.

class AnswerOptionBase(BaseModel):
    # Core answer option fields
    option_text: str
    is_correct: bool = False
    sort_order: Optional[int] = None


class AnswerOptionCreate(AnswerOptionBase):
    # Used when creating an answer option
    question_id: int


class AnswerOptionOut(AnswerOptionBase):
    # Used when returning answer optitons to clients
    id: int
    question_id: int

    model_config = ConfigDict(from_attributes=True)


# ----- SESSION PLAYERS -----
# Represents a player that has joined the quiz session.
# Can be a registered user or a guest (nickname only).

class SessionPlayerCreate(BaseModel):
    # Used when a player joins a session
    session_id: int
    nickname: str
    user_id: Optional[int] = None


class SessionPlayerOut(BaseModel):
    # Used when returning session player data
    id: int
    session_id: int
    user_id: Optional[int] = None
    nickname: str
    joined_at: datetime
    score: int

    model_config = ConfigDict(from_attributes=True)


# ----- SESSION ANSWERS -----
# Represents an answer submitted by a player during a session.
# Used for tracking the scores and results.

class SessionAnswerCreate(BaseModel):
    # Used when a player enters an answer
    session_player_id: int
    question_id: int
    answer_option_id: int


class SessionAnswerOut(BaseModel):
    # Used when returning entered answers
    id: int
    session_player_id: int
    question_id: int
    answer_option_id: int
    answered_at: Optional[datetime] = None
    is_correct: Optional[bool] = None
    points_awarded: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
import os

import psycopg2
from dotenv import load_dotenv  # loads environment variables from .env file

load_dotenv(override=True)      # ensure that .env values has higher priority over system values

# Enviroment-based configuration 
# Sensetive data such as database credentials and password are stored in enviroment variables instead of being hardcoded
DATABASE_NAME = os.getenv("DATABASE_NAME")
PASSWORD = os.getenv("PASSWORD")


def get_connection():
    """
    Function that returns a single connection
    In reality, we might use a connection pool, since
    this way we'll start a new connection each time
    someone hits one of our endpoints, which isn't great for performance
    ---------
    Function that creates ONE database connection and is reused everywhere.
    This centralizes DB config.
    ********* CHANGE THIS? ***********
    ---------
    """
    return psycopg2.connect(
        dbname=DATABASE_NAME,
        user="postgres",  # change if needed
        password=PASSWORD,
        host="localhost",  # change if needed
        port="5432",  # change if needed
    )


def create_tables():
    """
    A function that creates, opens a DB connection and defines schema.
    It starts a transaction and commits on success, if it fails it rolls back on error.
    Not used during normal app runtime, only runs when setting up DB.

    Also allows multiple CREATE TABLE statment excecutes in one call through cursor.execute.
    Uses CREATE TABLE *IF* NOT EXISTS to prevent crashes if a table already exists.
    Structured in a way so the dependencies go from the top and down.
    """
    connection = get_connection()
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
            """
            -- USERS
            CREATE TABLE IF NOT EXISTS users (
                id BIGSERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role VARCHAR(20) MOT NULL, -- e.g. admin, teacher, player.
                created_at TIMESTAMPTZ NOT NULL default now()
            );

            -- QUIZZES
            CREATE TABLE IF NOT EXISTS quizzes (
                id BIGSERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                visibility VARCHAR(20),    -- e.g. public, private.
                creator_id BIGINT NOT NULL REFERENCES users(id),
                created_at TIMESTAMPTZ NOT NULL default now(),
                updated_at TIMESTAMPTZ
            );

            -- QUIZ QUESTIONS
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id BIGSERIAL PRIMARY KEY,
                quiz_id BIGINT NOT NULL REFERENCES quizzes(id),
                question_type VARCHAR(20), -- e.g. multiple_choice, true_false.
                time_limit_seconds INT,    -- e.g. 30.
                points INT,                -- e.g. 1000.
                sort_order INT,            -- which order in the quiz.
                question_text TEXT NOT NULL
            );

            -- QUESTION ANSWER OPTIONS
            CREATE TABLE IF NOT EXISTS question_answer_options (
                id BIGSERIAL PRIMARY KEY,
                question_id BIGINT NOT NULL REFERENCES quiz_questions(id),
                option_text TEXT NOT NULL,
                is_correct BOOLEAN NOT NULL default FALSE,
                sort_order INT
            );

            -- QUIZ SESSIONS
            CREATE TABLE IF NOT EXISTS quiz_sessions (
                id BIGSERIAL PRIMARY KEY,
                quiz_id BIGINT NOT NULL REFERENCES quizzes(id),
                host_id BIGINT NOT NULL REFERENCES users(id),
                join_code VARCHAR(10) UNIQUE NOT NULL,       -- PIN-code for players to type in.
                status VARCHAR(20) NOT NULL default 'waiting'
                    CHECK (status IN ('waiting', 'in_progress', 'finished')),
                started_at TIMESTAMPTZ,
                finished_at TIMESTAMPTZ
            );

            -- QUIZ SESSION PLAYERS 
            CREATE TABLE IF NOT EXISTS quiz_session_players (
                id BIGSERIAL PRIMARY KEY,
                session_id BIGINT NOT NULL REFERENCES quiz_sessions(id),
                user_id BIGINT NULL REFERENCES users(id),
                nickname VARCHAR(50) NOT NULL,
                joined_at TIMESTAMPTZ NOT NULL default now(),
                score INT NOT NULL default 0,

                UNIQUE (session_id, nickname)   -- Constraint to keep two players from having the same nickname.
            );

            -- QUIZ SESSION ANSWERS
            CREATE TABLE IF NOT EXISTS quiz_session_answers (
                id BIGSERIAL PRIMARY KEY,
                session_player_id BIGINT NOT NULL REFERENCES quiz_session_players(id),
                answer_option_id BIGINT NOT NULL REFERENCES question_answer_options(id),
                answered_at TIMESTAMPTZ,
                is_correct BOOLEAN,
                points_awarded INT,
                question_id BIGINT NOT NULL REFERENCES quiz_questions(id)
            );
            """
        )
    connection.close()



# File only runs table creation when executed directly.
if __name__ == "__main__":
    # Only reason to execute this file would be to create new tables, meaning it serves a migration file
    create_tables()
    print("Tables created successfully.")


# Run this file - python db_setup.py (Tables created successfully.)
# uvicorn app:app --reload # Start the FastAPI development server with auto-reload (Application startup complete.)
# connect to http://localhost:8000/docs via browser
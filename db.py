from psycopg2.extras import RealDictCursor # RealDictCursor makes query result return dictionaries instead of tuples
from typing import List, Optional          # Used for typehints that makes the readabillity better
from schemas import UserCreate, QuizCreate, QuestionCreate

"""
1. This file is responsible for making database queries, which your fastapi endpoints/routes can use.
The reason we split them up is to avoid clutter in the endpoints, so that the endpoints might focus on other tasks

1.1: Using DAL (Data Access Layer) which doesn't involve using:

- FastAPI imports.
- HTTP logic.
- Request or response objects.

It only uses SQL and database logic.

-----------------------------------------------------------------------------------------------------------------------

2. Try to return results with cursor.fetchall() or cursor.fetchone() when possible

2.2: Consistent use of:

- fetchall() for the list operations.
- fetchone() for create and delete operations.
-----------------------------------------------------------------------------------------------------------------------

3. Make sure you always give the user response if something went right or wrong, sometimes 
you might need to use the RETURNING keyword to garantuee that something went right / wrong
e.g when making DELETE or UPDATE queries

3.3: Using RETURNING id in create_user, delete_user, create_quiz.

-----------------------------------------------------------------------------------------------------------------------

4. No need to use a class here

4.4: No classes used.

-----------------------------------------------------------------------------------------------------------------------

5. Try to raise exceptions to make them more reusable and work a lot with returns

5.5: No raise exceptions raised at this point.

- Returning values through dict, bool, int and None at the moment, letting psycopg2 raise the errors with implicit exceptions.

# TODO: If time allows, raise exceptions will be implemented.

-----------------------------------------------------------------------------------------------------------------------

6. You will need to decide which parameters each function should receive. All functions 
start with a connection parameter.

6.6: All the functions below start with the con statement and only accepts what they need.

-----------------------------------------------------------------------------------------------------------------------

7. Below, a few inspirational functions exist - feel free to completely ignore how they are structured

7.7: Adapted the inspirational functions that were provided:

- changed naming, added schemas/typing/comments and handeled delete confirmation.

-----------------------------------------------------------------------------------------------------------------------

8. E.g, if you decide to use psycopg3, you'd be able to directly use pydantic models with the cursor, 
these examples are however using psycopg2 and RealDictCursor

8.8: RealDictCursor parameter used in all functions and parameterized all the queries through %s.
"""


# ----- USERS -----

def list_users(con) -> List[dict]:
    """
    Fetches all users from database.
    Returns a list of dictionaries where each dict represents a user.
    """
    # Activates a connection and commits it automatically if it's successful.
    with con:
        # Open a database cursor that returns rows as dictionaries
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT id, username, email, role, created_at FROM users;")
            # fetchall() returns all rows from the query
            return cursor.fetchall()



def create_user(con, user: UserCreate) -> int:
    """
    Creates a new user in the database.
    Returns the ID of the created user.
    """
    # TODO In a "real" application, the password should be hashed before storing it.
    password_hash = user.password
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, role)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                # Using %s as placehorders as a safety messure against SQL injections
                (user.username, user.email, password_hash, user.role),
            )
            row = cursor.fetchone() # Returns the inserted row
            return row["id"]        # Returns the primary key



def get_user(con, user_id: int ) -> Optional[dict]:
    """
    Fetch a single user by its ID.
    Returns a dictionary if the user exits, if user doesn't exist, it returns None.
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT id, username, email, role, created_at FROM users WHERE id = %s;",
                (user_id,)           # Comma in parameter to create a tuple
            )
            return cursor.fetchone() # Returns one row or None



def delete_user(con, user_id: int) -> bool:
    """
    Delete a user by its ID.
    Returns True if the user was deleted, otherwise it returns False if the user doesn't exist.
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "DELETE FROM users WHERE id = %s RETURNING id;",
                (user_id,)  
            )
            # If a row is returned, the delete was successful
            row = cursor.fetchone()
            return row is not None



# ----- QUIZZES -----

def list_quizzes(con) -> List[dict]:
    """
    Fetch all quizzes from the database.
    Returns a list of quizzes as a dictionary.
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, title, description, visibility, creator_id, created_at, updated_at
                FROM quizzes;
                """
            )
            return cursor.fetchall()



def create_quiz(con, quiz: QuizCreate) -> int:
    """
    Create a new quiz in the database.
    Returns the ID of the created quiz.
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                INSERT INTO quizzes (title, description, visibility, creator_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
                """,
                (quiz.title, quiz.description, quiz.visibility, quiz.creator_id) # Values taken from the validated Pydantic schema
            )
            row = cursor.fetchone()
            return row["id"]



def list_questions_by_quiz(con, quiz_id: int):
    """
    Fetch all questions that belongs to a specific quiz.
    Returns a list of dictionaries where each dict represents a question.
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, quiz_id, question_type, time_limit_seconds, points, sort_order, question_text
                FROM quiz_questions
                WHERE quiz_id = %s
                ORDER BY sort_order NULLS LAST, id;
                """,
                (quiz_id,)
            )
            return cursor.fetchall()



# ----- QUESTIONS -----

def create_question(con, q: QuestionCreate) -> int:
    """
    Create a new question in the database.
    Returns the ID of the created question.
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                INSERT INTO quiz_questions (quiz_id, question_type, time_limit_seconds, points, sort_order, question_text)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (q.quiz_id, q.question_type, q.time_limit_seconds, q.points, q.sort_order, q.question_text)
            )
            row = cursor.fetchone()
            return row["id"]



def get_question(con, question_id: int):
    """
    Fetch a single question by ID.
    Return a dictionary if the question exists, if not, return None.
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, quiz_id, question_type, time_limit_seconds, points, sort_order, question_text
                FROM quiz_questions
                WHERE id = %s;
                """,
                (question_id,)
            )
            return cursor.fetchone()



def delete_question(con, question_id: int) -> bool:
    """
    Delete a question by its ID.
    Returns True if the question was deleted, otherwise it returns False.
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "DELETE FROM quiz_questions WHERE id = %s RETURNING id;",
                (question_id,),
            )
            # If a row is returned, the delete was successful
            row = cursor.fetchone()
            return row is not None



# ----- SESSIONS -----

def create_session(con, quiz_id: int, host_id: int, join_code: str) -> int:
    """
    Creates a new game session.
    Returns the ID of the newly created session.

    - The session status is not set here, it's handled by PostgresSQL.
    - If a INSERT is not provided as a value for status, it will be set as 'waiting' per default. 
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                INSERT INTO quiz_sessions (quiz_id, host_id, join_code)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (quiz_id, host_id, join_code),
            )
            row = cursor.fetchone()
            return row["id"]


#
def get_session_by_join_code(con, join_code: str):
    """
    Fetches a quiz session using the join code.
    Used when players join the session.
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, quiz_id, host_id, join_code, status, started_at, finished_at
                FROM quiz_sessions
                WHERE join_code = %s;
                """,
                (join_code,),
            )
            return cursor.fetchone()



def get_session(con, session_id: int):
    """
    Fetches a quiz session by its ID.
    Used to get the session details.
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, quiz_id, host_id, join_code, status, started_at, finished_at
                FROM quiz_sessions
                WHERE id = %s;
                """,
                (session_id,),
            )
            return cursor.fetchone()



def update_session_status(con, session_id: int, status: str) -> bool:
    """
    Updates the status of the quiz session.
    Returns True if the session esxists and was updated.
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                UPDATE quiz_sessions
                SET status = %s,
                    finished_at = CASE WHEN %s = 'finished' THEN now() ELSE finished_at END
                WHERE id = %s
                RETURNING id;
                """,
                (status, status, session_id),
            )
            return cursor.fetchone() is not None


# ----- SESSION PLAYERS -----

def add_session_player(con, session_id: int, nickname: str, user_id: int | None):
    """
    Adds a player to the quiz session.
    The player can be a registered user or a guest player.
    Returns the new session player ID.
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                INSERT INTO quiz_session_players (session_id, nickname, user_id)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (session_id, nickname, user_id),
            )
            return cursor.fetchone()["id"]



def list_session_players(con, session_id: int):
    """
    Returns all players that have joined a specific session.
    Used to display the player list.
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, session_id, user_id, nickname, joined_at, score
                FROM quiz_session_players
                WHERE session_id = %s
                ORDER BY joined_at ASC, id ASC;
                """,
                (session_id,),
            )
            return cursor.fetchall()



def get_session_player(con, player_id: int):
    """
    Fetches a single session player by the ID.
    Used when handling player-specific actions.
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT id, session_id, user_id, nickname, joined_at, score
                FROM quiz_session_players
                WHERE id = %s;
                """,
                (player_id,),
            )
            return cursor.fetchone()



def increment_player_score(con, player_id: int, delta: int) -> bool:
    """
    Increases a player's score.
    Returns True if the player exists and was updated.
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                UPDATE quiz_session_players
                SET score = score + %s
                WHERE id = %s
                RETURNING id;
                """,
                (delta, player_id),
            )
            return cursor.fetchone() is not None


import os

import psycopg2
from db_setup import get_connection
from fastapi import FastAPI, HTTPException
from typing import List
import db
from schemas import UserCreate, UserOut, QuizCreate, QuizOut, QuestionCreate, QuestionOut, SessionCreate


app = FastAPI()

"""
ADD ENDPOINTS FOR FASTAPI HERE
Make sure to do the following:

- Use the correct HTTP method (e.g get, post, put, delete)

- Use correct STATUS CODES, e.g 200, 400, 401 etc. when returning a result to the user

- Use pydantic models whenever you receive user data and need to validate the structure and data types (VG)

This means you need some error handling that determine what should be returned to the user
Read more: https://www.geeksforgeeks.org/10-most-common-http-status-codes/
- Use correct URL paths the resource, e.g some endpoints should be located at the exact same URL, 
but will have different HTTP-verbs.
"""


# INSPIRATION FOR A LIST-ENDPOINT - Not necessary to use pydantic models, but we could to ascertain that we return the correct values
# @app.get("/items/")
# def read_items():
#     con = get_connection()
#     items = get_items(con)
#     return {"items": items}


# INSPIRATION FOR A POST-ENDPOINT, uses a pydantic model to validate
# @app.post("/validation_items/")
# def create_item_validation(item: ItemCreate):
#     con = get_connection()
#     item_id = add_item_validation(con, item)
#     return {"item_id": item_id}


# IMPLEMENT THE ACTUAL ENDPOINTS! Feel free to remove



# ----- USERS -----

@app.get("/users", response_model=List[UserOut])
def list_users():
    """
    GET /users
    Fetch all users from the database.    
    """
    # Opens a new database connection for this specific request
    con = get_connection()
    try:
        # Call the DAL(Data Access Layer) function that runs the SQL query 
        users = db.list_users(con)
        # Return raw dicts and FastAPI converts them to UserOut
        return users
    finally:
        # Always close the connection, even if something goes wrong
        con.close()



@app.post("/users", response_model=dict, status_code=201)
def create_user(user: UserCreate):
    """
    POST /users
    Create a new user using validated request data.
    """
    con = get_connection()
    try:
        # Inserts user to database and get the ID
        user_id = db.create_user(con, user)
        # Return the ID response
        return{"id": user_id}
    except Exception as e:
        # If error occurs, convert the database errors into a HTTP response
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        con.close()



@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    """
    GET /users{user_id}
    Fetch a single user by ID.
    """
    con = get_connection()
    try:
        user = db.get_user(con, user_id)
        # If a user is not found, return 404 status
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        return user
    finally:
        con.close()



@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    """
    DELETE /users/{user_id}
    Delete a user with its ID.
    """
    con = get_connection()
    try:
        deleted = db.delete_user(con, user_id)
        # If there's nothing to delete, the user did not exist - print message.
        if not deleted:
            raise HTTPException(status_code=404, detail="User not found.")
        # Successful DELETE: FastAPI returns 204 No Content
        return
    finally:
        con.close()



# ----- QUIZZES -----

@app.get("/quizzes", response_model=List[QuizOut])
def list_quizzes():
    """
    GET /quizzes
    Fetch all quizzes.
    """
    con = get_connection()
    try:
        quizzes = db.list_quizzes(con)
        return quizzes
    finally:
        con.close()



@app.post("/quizzes", response_model=dict, status_code=201)
def create_quiz(quiz: QuizCreate):
    """
    POST /quizzes
    Create a new quiz.
    """
    con = get_connection()
    try:
        quiz_id = db.create_quiz(con, quiz)
        return {"id": quiz_id}
    finally:
        con.close()



@app.get ("/quizzes/{quiz_id}/questions", response_model=List[QuestionOut])
def list_questions(quiz_id: int):
    """
    Get /quizzes/{quiz_id}/questions
    Fetch all questions that belongs to a specific quiz.
    """
    con = get_connection()
    try:
        return db.list_questions_by_quiz(con, quiz_id)
    finally:
        con.close()



# ----- QUESTIONS -----

@app.post("/questions", status_code=201, response_model=dict)
def create_question(question: QuestionCreate):
    """
    POST /questions
    Create a new question for a quiz using the validated request data.
    """
    con = get_connection()
    try:
        question_id = db.create_question(con, question)
        return {"id": question_id}
    finally:
        con.close()



@app.get("/questions/{question_id}", response_model=QuestionOut)
def get_question(question_id: int):
    """
    GET /questions/{question_id}
    Fetch a single question by its ID.
    """
    con = get_connection()
    try:
        q = db.get_question(con, question_id)
        if not q:
            raise HTTPException(status_code=404, detail="Question not found.")
        return q
    finally:
        con.close()



@app.delete("/questions/{question_id}", status_code=204)
def delete_question(question_id: int):
    """
    DELETE /questions/{question_id}
    Delete a question by its ID.
    """
    con = get_connection()
    try:
        deleted = db.delete_question(con, question_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Question not found")
        return
    finally:
        con.close()



@app.post("/sessions", status_code=201, response_model=dict)
def create_session(session: SessionCreate):
    """
    POST /sessions
    Create a new game session. Status defaults to 'waiting'.
    """
    con = get_connection()
    try:
        session_id = db.create_session(
            con,
            quiz_id=session.quiz_id,
            host_id=session.host_id,
            join_code=session.join_code,
        )
        return {"id": session_id}
    finally:
        con.close()

# uvicorn app:app --reload
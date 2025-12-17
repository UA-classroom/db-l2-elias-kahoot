import os

import psycopg2
from db_setup import get_connection
from fastapi import FastAPI, HTTPException
from typing import List
import db
from schemas import UserCreate, UserOut, QuizCreate, QuizOut


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


app = FastAPI()

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
"""
GET /users{iser_id}
Fetch a single user by ID.
"""
def get_user(user_id: int):
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


# uvicorn app:app --reload
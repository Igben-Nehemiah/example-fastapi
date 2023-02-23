from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends 
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=engine)

app = FastAPI()




class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None


class UpdatePostDto(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None

HOST = 'localhost'
DB='fastapi2'
DB_USER="postgres",
DB_PASSWORD= 'password'

max_number_of_trials = 5
number_of_trials = 0

while number_of_trials < max_number_of_trials:
    try:
        conn = psycopg2.connect(host=HOST, database=DB,
            user="postgres", password=DB_PASSWORD, cursor_factory=RealDictCursor)

        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)

    finally:
        number_of_trials += 1


@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))
    # post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} was not found")
    return {"data": post}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)): 
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts =db.query(models.Post).all()

    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES 
    #         (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {"data": new_post}


@app.delete("/posts/{id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} was not found")

    post.delete(synchronize_session=False)
    db.commit()
    # conn.commit()

@app.put("/posts/{id}")
def update_post(id: int, update_post_dto: UpdatePostDto, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title=%s, content=%s, 
    #     published=%s WHERE id=%s RETURNING *""", (payload.title, payload.content, 
    #         payload.published, (str(id))))
    
    # updated_post = cursor.fetchone()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} was not found")

    post_query.update(update_post_dto.dict(), synchronize_session=False)
    db.commit()            
    # conn.commit()
    return {"data": post_query.first()}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)): 
    posts =db.query(models.Post).all()
    return {"data": posts}

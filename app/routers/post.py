from typing import List
from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, oauth2, schemas
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db),
                            current_user = Depends(oauth2.get_current_user)):
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")) \
            .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True) \
            .group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} was not found")
    
    if post.Post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorised to perform requested action")

    return post

@router.get("/", response_model=list[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), 
                            current_user = Depends(oauth2.get_current_user),
                            limit: int = 10,
                            skip: int = 0,
                            search: str = ""): 

    posts_query = db.query(models.Post, func.count(models.Vote.post_id).label("votes")) \
            .join(models.Vote, models.Vote.post_id == models.Post.id,isouter=True).group_by(models.Post.id) \
            .filter(models.Post.title.contains(search)).offset(skip).limit(limit)
    
    return posts_query.all() 


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponseDto)
def create_posts(post: schemas.CreatePostDto, db: Session = Depends(get_db),
                            current_user = Depends(oauth2.get_current_user)):
    new_post = models.Post(**post.dict(), owner_id = current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.delete("/{id}", status_code= status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db),
                            current_user = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} was not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorised to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()

@router.put("/{id}", response_model=schemas.PostResponseDto)
def update_post(id: int, update_post_dto: schemas.UpdatePostDto, 
                            db: Session = Depends(get_db), 
                            current_user = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} was not found")
        
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorised to perform requested action")

    post_query.update(update_post_dto.dict(), synchronize_session=False)
    db.commit()            
    return post_query.first()
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.comment import Comment
from app.models.user import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.delete("/{comment_id}")
def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == current_user.id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or not authorized")
    db.delete(comment)
    db.commit()
    return {"success": True}

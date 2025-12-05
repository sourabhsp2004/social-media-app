import os
import uuid
import tempfile
import shutil
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

from app.schemas import PostCreate, PostResponse, UserRead, UserCreate, UserUpdate, CommentCreate, CommentResponse, LikeCreate, LikeResponse
from app.db import Post, create_db_and_tables, get_async_session, User, Comment, Like
from app.images import imagekit
from app.users import auth_backend, current_active_user, fastapi_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix='/auth/jwt', tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])

@app.post("/upload")
async def upload_file(
        file: UploadFile = File(...),
        caption: str = Form(""),
        user: User = Depends(current_active_user),
        session: AsyncSession = Depends(get_async_session)
):
    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        upload_result = imagekit.upload_file(
            file=open(temp_file_path, "rb"),
            file_name=file.filename,
            options=UploadFileRequestOptions(
                use_unique_file_name=True,
                tags=["backend-upload"]
            )
        )

        if upload_result.response_metadata.http_status_code == 200:
            post = Post(
                user_id=user.id,
                caption=caption,
                url=upload_result.url,
                file_type="video" if file.content_type.startswith("video/") else "image",
                file_name=upload_result.name
            )
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()

@app.get("/feed")
async def get_feed(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    # Get posts
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    # Get users
    result = await session.execute(select(User))
    users = [row[0] for row in result.all()]
    user_dict = {u.id: u.email for u in users}

    posts_data = []
    for post in posts:
        # Get like count
        like_count_result = await session.execute(select(func.count(Like.id)).where(Like.post_id == post.id))
        like_count = like_count_result.scalar()

        # Check if liked by current user
        is_liked_result = await session.execute(select(Like).where(Like.post_id == post.id, Like.user_id == user.id))
        is_liked = is_liked_result.scalars().first() is not None

        # Get comment count
        comment_count_result = await session.execute(select(func.count(Comment.id)).where(Comment.post_id == post.id))
        comment_count = comment_count_result.scalar()

        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,
                "email": user_dict.get(post.user_id, "Unknown"),
                "like_count": like_count,
                "comment_count": comment_count,
                "is_liked": is_liked
            }
        )

    return {"posts": posts_data}


@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user),):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="You don't have permission to delete this post")

        await session.delete(post)
        await session.commit()

        return {"success": True, "message": "Post deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/posts/{post_id}/comments", response_model=CommentResponse)
async def create_comment(
    post_id: str,
    comment: CommentCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        post_uuid = uuid.UUID(post_id)
        new_comment = Comment(
            user_id=user.id,
            post_id=post_uuid,
            content=comment.content
        )
        session.add(new_comment)
        await session.commit()
        await session.refresh(new_comment)
        
        return CommentResponse(
            id=new_comment.id,
            user_id=new_comment.user_id,
            post_id=new_comment.post_id,
            content=new_comment.content,
            created_at=new_comment.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/posts/{post_id}/comments")
async def get_comments(
    post_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        post_uuid = uuid.UUID(post_id)
        result = await session.execute(
            select(Comment).where(Comment.post_id == post_uuid).order_by(Comment.created_at.asc())
        )
        comments = result.scalars().all()
        
        # Fetch user emails for comments
        user_ids = [c.user_id for c in comments]
        if user_ids:
            user_result = await session.execute(select(User).where(User.id.in_(user_ids)))
            users = user_result.scalars().all()
            user_map = {u.id: u.email for u in users}
        else:
            user_map = {}

        return {
            "comments": [
                {
                    "id": str(c.id),
                    "user_id": str(c.user_id),
                    "email": user_map.get(c.user_id, "Unknown"),
                    "content": c.content,
                    "created_at": c.created_at.isoformat()
                }
                for c in comments
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/posts/{post_id}/like")
async def toggle_like(
    post_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        post_uuid = uuid.UUID(post_id)
        
        # Check if already liked
        result = await session.execute(
            select(Like).where(Like.post_id == post_uuid, Like.user_id == user.id)
        )
        existing_like = result.scalars().first()
        
        if existing_like:
            await session.delete(existing_like)
            await session.commit()
            return {"liked": False}
        else:
            new_like = Like(user_id=user.id, post_id=post_uuid)
            session.add(new_like)
            await session.commit()
            return {"liked": True}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
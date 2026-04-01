from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Column, ForeignKey,Table, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from flask_bcrypt import check_password_hash, generate_password_hash
from datetime import datetime

db = SQLAlchemy()





posts_hashtag = db.Table(
"posts_hashtags",
db.metadata,
Column("posts_id", ForeignKey("posts.id")),
Column("hashtags_id", ForeignKey("hashtags.id"))
)


class User(db.Model):

    __tablename__= "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(120),nullable=False)
    user_name:Mapped[str]=mapped_column(String(120),unique=True,nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    profile:Mapped["Profile"]= relationship(back_populates="user")
    posts:Mapped[list["Post"]]= relationship(back_populates="user")
    comments:Mapped[list["Comments"]]= relationship(back_populates="user")
    hashtags:Mapped[list["HashTags"]]= relationship(back_populates="user")
    likes:Mapped[list["Likes"]]= relationship(back_populates="user")

    def set_password(self,password):
     self.password= generate_password_hash(password).decode('utf-8')

    def check_password_hash(self,password):
     return check_password_hash(self.password,password)


    def serialize(self):
        return {
            "id": self.id,
            "name":self.name,
            "user_name":self.user_name,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class Profile(db.Model):

    __tablename__= "profile"

    id:Mapped[int]= mapped_column(primary_key=True)
    biography:Mapped[str]=mapped_column(String(225),nullable=True)
    photo:Mapped[str] = mapped_column(String(255), nullable= True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"),unique=True,nullable=False)

    user:Mapped["User"]= relationship(back_populates="profile")

    # def __repr__(self):
    #     return{
    #         f"<Profile {self.id} - User : {self.user.user_name}>"
    #     }


    def serialize(self):
        return{
            "id":self.id,
            "biography":self.biography,
            "photo": self.photo,
            "user_id":self.user_id
        }



class Post(db.Model):

    __tablename__="posts"

    id:Mapped[int] = mapped_column(primary_key=True)
    photo:Mapped[str] = mapped_column(String(255), nullable= False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"),unique=True,nullable=False)

    user:Mapped["User"]=relationship(back_populates="posts")
    likes:Mapped[list["Likes"]]=relationship(back_populates="post")
    comments:Mapped[list["Comments"]]= relationship(back_populates="post")
    hashtags: Mapped[list["HashTags"]] = relationship(secondary=posts_hashtag, back_populates="posts")




    def serialize(self):
        return {
            "id":self.id,
            "photo":self.photo,
            "date":self.date,
            "user_id":self.user_id
        }
    


class HashTags(db.Model):

    __tablename__="hashtags"

    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str]= mapped_column(String(180),nullable=False)
    post_id:Mapped[int]=mapped_column(ForeignKey("posts.id"),unique=True,nullable=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"),unique=True,nullable=True)

    posts: Mapped[list["Post"]] = relationship(secondary=posts_hashtag, back_populates="hashtags")
    user:Mapped["User"]=relationship(back_populates="hashtags")



    def serialize(self):
        return {
            "id":self.id,
            "name":self.name,
            
        }
    


    
class Comments(db.Model):

    __tablename__= "comments"

    id:Mapped[int]= mapped_column(primary_key=True)
    content:Mapped[str] = mapped_column(String(500),nullable= True)
    date:Mapped[datetime] = mapped_column(DateTime,nullable=False)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)
    post_id:Mapped[int] = mapped_column(ForeignKey("posts.id"),nullable=False)


    user:Mapped["User"]= relationship(back_populates="comments")
    post:Mapped["Post"]= relationship(back_populates="comments")
    likes:Mapped[list["Likes"]]=relationship(back_populates="comment")

    def serialize(self):
        return {
            "id":self.id,
            "content":self.content,
            "date":self.date,
            "user_id":self.user_id,
            "post_id":self.post_id
        }
    
class Likes(db.Model):

    __tablename__="likes"

    id:Mapped[int] = mapped_column(primary_key=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)
    post_id:Mapped[int] = mapped_column(ForeignKey("posts.id"),nullable=True)
    comment_id:Mapped[int]=mapped_column(ForeignKey("comments.id"),nullable=True)



    user:Mapped["User"]= relationship(back_populates="likes", foreign_keys=[user_id])
    post:Mapped["Post"]=relationship(back_populates="likes",foreign_keys=[post_id])
    comment:Mapped["Comments"]= relationship(back_populates="likes",foreign_keys=[comment_id])

    def serialize(self):
        return {
            "id":self.id,
            "user_name": self.user.user_name,
            "user_id":self.user_id,
            "post_id":self.post_id,
            "comment_id":self.comment_id
        }
    


import os
from flask_admin import Admin
from models import db, User,Profile,Post,HashTags, Comments,Likes
from flask_admin.contrib.sqla import ModelView
from flask import Flask
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "una-clave-secreta"

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')
    jwt = JWTManager(app)


    
    # Add your models here, for example this is how we add a the User model to the admin



    
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Profile, db.session))
    admin.add_view(ModelView(Post, db.session))
    admin.add_view(ModelView(HashTags, db.session))
    admin.add_view(ModelView(Comments, db.session))
    admin.add_view(ModelView(Likes, db.session))

    
    

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))
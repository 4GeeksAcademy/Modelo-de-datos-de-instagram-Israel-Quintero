"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User,Profile,Post,HashTags, Comments,Likes
from sqlalchemy import select
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False


db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():


    person= User.query.get(1)
    print(person.serialize())
    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/create/user', methods=['POST'])
def create_user():
    data= request.get_json()

    user_name= data.get('user_name')
    name=data.get('name')
    email=data.get('email')
    password=data.get('password')

    if not user_name or not name or not  email or not password:
        return jsonify({'msg':'Please fill the missing blanks up to register your account '}),400
    
    existing_user= db.session.execute(select(User).where(User.email == email, User.user_name == user_name)).scalar_one_or_none()

    if existing_user:
        return jsonify({'msg':'A user with this email or username already exists'}),401


    new_user=User(user_name=user_name,name=name,email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg':'El registro de usuario se ha completado satisfactoriamente'}),200


@app.route('/login',methods=['POST'])
def user_login():
    data= request.get_json()
    email=data.get('email')
    password=data.get('password')

    if not email or not password:
        return jsonify({'msg':'email or password required'}),400

    existing_user= db.session.execute(select(User).where(User.email == email)).scalar_one_or_none()

    if existing_user is None:
        return jsonify({'msg':'email or password are incorrect'}),401
    
    if existing_user.check_password_hash(password):
        access_token=create_access_token(identity=str(existing_user.id))
        return jsonify({
            'msg': 'Inicio de sesión exitoso',
            'token': access_token,
            'existing_user': existing_user.serialize(),
        }), 200
    else:
        return jsonify({'msg': 'El correo eletrócnico o password son incorrectos'}), 401


@app.route('/create/profile', methods=['POST'])
@jwt_required()
def create_profile():
    existing_user= get_jwt_identity()
    existing_user_id=db.session.get(User, int(existing_user))

    if not existing_user_id:
        return jsonify({'msg':'user not authorized'}),400
    
    data=request.get_json()
  

    if not data:
        return jsonify({'msg':'invalid data'}),401
    
    new_profile=Profile(
    biography= data.get('biography'),
    photo=data.get('photo'),
    user_id=existing_user_id.id
    )

    db.session.add(new_profile)
    db.session.commit()

    return jsonify({'msg':'Your profile has been succesfully updated'}),200




@app.route('/create/post', methods=['POST'])
@jwt_required()
def create_post():
     existing_user= get_jwt_identity()
     existing_user_id=db.session.get(User, int(existing_user))

     if not existing_user_id:
        return jsonify({'msg':'user not authorized'}),400
    
     data=request.get_json()
  

     if not data:
        return jsonify({'msg':'invalid data'}),401
     
     new_post=Post(
         photo=data.get('photo'),
         date=data.get('date'),
         user_id=existing_user_id.id
     )

     db.session.add(new_post)
     db.session.commit()

     return jsonify({'msg':'Your post has been succesfully created'}),200






@app.route('/create/hashtag', methods=['POST'])
@jwt_required()
def create_hashtag():
     existing_user= get_jwt_identity()
     existing_user_id=db.session.get(User, int(existing_user))

     if not existing_user_id:
        return jsonify({'msg':'user not authorized'}),400
    
     data=request.get_json()
  

     if not data:
        return jsonify({'msg':'invalid data'}),401
     
     post_id=data.get("post_id")
     post= db.session.get(Post,post_id)
     

     
     new_hashtag=HashTags(
         name=data.get('name'),
         post_id=post.id,
         
         )


     db.session.add(new_hashtag)
     db.session.commit()

     return jsonify({'msg':'The hashtag has been successfully created'}),200



@app.route('/create/comment', methods=['POST'])
@jwt_required()
def create_comment():
     existing_user= get_jwt_identity()
     existing_user_id=db.session.get(User, int(existing_user))

     if not existing_user_id:
        return jsonify({'msg':'user not authorized'}),400
    
     data=request.get_json()
     
     if not data:
        return jsonify({'msg':'invalid data'}),401
    
     post_id=data.get("post_id")
     post= db.session.get(Post,post_id)
     
     new_comment=Comments(
        content=data.get('content'),
        date=data.get('date'),
        user_id=existing_user_id.id,
        post_id=post.id
     )

     db.session.add(new_comment)
     db.session.commit()

     return jsonify({'msg':'The comment has been created successfully'}),200


@app.route('/create/like', methods=['POST'])
@jwt_required()
def create_like():
     existing_user= get_jwt_identity()
     existing_user_id=db.session.get(User, int(existing_user))

     if not existing_user_id:
        return jsonify({'msg':'user not authorized'}),400
    
     data=request.get_json()
     
     if not data:
        return jsonify({'msg':'invalid data'}),401
    
     post_id=data.get("post_id")
     comment_id=data.get("comment_id")

     post= db.session.get(Post,post_id) if  post_id else None
     comment=db.session.get(Comments,comment_id) if comment_id else None

     if not post and not comment:
         return jsonify({'msg':'post or comment no found'}),402
     
     new_like=Likes(
         user_id=existing_user_id.id,
    
         post_id=post.id if  post else None,
         comment=comment.id if  comment else None
     )

     db.session.add(new_like)
     db.session.commit()

     return jsonify({'msg':'You have liked this content'}),200


@app.route('/view/likes', methods=['GET'])
@jwt_required()
def view_likes():
     existing_user= get_jwt_identity()
     existing_user_id=db.session.get(User, int(existing_user))

     if not existing_user_id:
        return jsonify({'msg':'user not authorized'}),400
    
     likes= [like.serialize() for like in existing_user_id.likes]

     
 
     return jsonify(likes),200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

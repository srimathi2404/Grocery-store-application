from flask_security import Security,SQLAlchemySessionUserDatastore
from models import Users,role,db
from API import *
import hashlib
from worker import *
from caching import cache
class Config(object):
    DEBUG = False
    TESTING = False

from dotenv import load_dotenv
load_dotenv()
import os
def create_role():
    if not role.query.get(1):
    
        r=role(name='user',description="userrrr")
        r1=role(name="admin",description="admin")
        r2=role(name="manager",description="manager")
        db.session.add(r)
        db.session.add(r1)
        db.session.add(r2)
        db.session.commit()



class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    SECRET_KEY = "thisissecter"
    SECURITY_PASSWORD_SALT = "thisissaltt"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = os.getenv('CACHE_REDIS_HOST')
    CACHE_REDIS_PORT = os.getenv('CACHE_REDIS_PORT')
    CACHE_REDIS_PASSWORD = os.getenv('CACHE_REDIS_PASSWORD')
    # CACHE_REDIS_DB = 3
from flask import Flask
from models import db, Users, role,RolesUsers

#from sec import datastore
from config import DevelopmentConfig


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    api.init_app(app)
    db.init_app(app)
    cache.init_app(app)

    user_datastore = SQLAlchemySessionUserDatastore(db.session,Users,role) # Not SQLAlchemyUserDatastore
    app.security = Security(app, user_datastore)
    # api.init_app(app)
    #excel.init_excel(app)
    #app.security = Security(app, datastore)
    #cache.init_app(app)
    with app.app_context():
        
        db.create_all()
        create_role()
        # to get the users with admin as role
        admin_users = Users.query.filter_by(username="admin").first()
        if not admin_users:
            password="admin"
            # add_admin(username="admin",password="admin",fname="admin",lname="admin",mobile="1212121212",email="admin@gmail.com")
            encoded_password = password.encode('utf-8')
            hashed_password = hashlib.sha256(encoded_password).hexdigest()
            app.security.datastore.create_user(username="admin",first_name="fname", last_name="lname",roles=["admin"], mobile_no=99999, email="email",password=hashed_password)
            db.session.commit()
        

    return app

app = create_app()

# def celery_func():
#     # cache.init_app(app)
    
#     celery1 = celery
#     celery1.conf.update(
#         broker_url=app.config["CELERY_BROKER_URL"],
#         result_backend=app.config["CELERY_RESULT_BACKEND"]
#     )
#     celery1.Task = ContextTask
#     # Setting Flask Security Setup
#     app.app_context().push()

#     return celery1


# celery = celery_func()

# celery_app = celery_init_app(app)
    
    
from user import *
from API import *

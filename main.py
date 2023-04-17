from flask import Flask
from model import *
from flask_restful import Api
from flask_login import LoginManager

app = Flask(__name__,static_folder='./static')

# app.config['SQLALCHEMY_DATABASE_URI']="postgresql://postgres:Bala5885@localhost/app_data_2"
app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///blogDatabase.sqlite3"
db.init_app(app)
api = Api(app)
app.app_context().push()

db.create_all()
from controler import *

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

from api import *
api.add_resource(UserApi,"/api/user","/api/user/<string:user_name>")
api.add_resource(PostApi,"/api/post","/api/post/<int:id>")
api.add_resource(Actions,'/api/follow/<string:user_name>',
                    '/api/unfollow/<string:user_name>/<string:follower_user_name>' )
api.add_resource(AllPost,'/api/all_post/<string:u_name>')

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    # sess.init_app(app)

    
    app.run()

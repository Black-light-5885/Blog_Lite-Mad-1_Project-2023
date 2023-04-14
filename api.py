from flask_restful import Resource,fields,marshal_with,reqparse
from main import db
from model import *
from validation import *
user_output = {
                "id" : fields.Integer,
                "user_name" : fields.String,
                "first_name" : fields.String,
                "last_name" : fields.String,
                "gender" : fields.String
            }

user_parser = reqparse.RequestParser()
user_parser.add_argument('first_name')
user_parser.add_argument('last_name')
user_parser.add_argument('user_name')
user_parser.add_argument('gender')
user_parser.add_argument('password')


class UserApi(Resource):
    @marshal_with(user_output)
    def get(self, user_name):
        user = User.query.filter_by(user_name = user_name).first()
        if user:
            return user
        else:
            raise NotFoundError(status_code=404)
    def put(self, user_name):
        arg = user_parser.parse_args()
        first_name = arg.get('first_name',None)
        last_name = arg.get('last_name',None)
        user = User.query.filter_by(user_name = user_name).first()
        if user:
            if first_name != 'None' and len(first_name)<2:
                raise BusninessValidationError(error_message = 'first Name Too short',status_code = 400)
            elif first_name:
                user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                db.session.commit()
                return '',200
        else:
            raise NotFoundError(status_code=404)
    def delete(self, user_name):
        user = User.query.filter_by(user_name = user_name).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return "",200
        else:
            raise NotFoundError(status_code=404)

    @marshal_with(user_output)
    def post(self):
        arg = user_parser.parse_args()
        first_name = arg.get('first_name',None)
        last_name = arg.get('last_name',None)
        user_name = arg.get('user_name',None)
        gender = arg.get('gender',None)
        password = arg.get('password',None)
        user_ = User.query.filter_by(user_name=user_name).first()
        print(user_)
        if first_name =='None' or len(first_name)<=2:
            raise BusninessValidationError(status_code=400,error_message='First Name Empty or Too short')
        elif user_name == 'None' or len(user_name)<=2:
            raise BusninessValidationError(status_code=400,error_message='User Name Empty or Too short')
        elif user_:
            raise BusninessValidationError(status_code=400,error_message='User Name already used!')
        elif not gender or (gender not in ['Male','Female']):
            raise BusninessValidationError(status_code=400,error_message='Ivalid genger value. Genger must be either Male or Female')
        elif not password:
            raise BusninessValidationError(status_code=400,error_message='Password can\'t empty')
        elif len(password)<7:
            raise BusninessValidationError(status_code=400,error_message='Password length is short. Password must greater than or equal to 7')
        else:
            user = User(first_name= first_name,last_name=last_name,
            user_name= user_name,gender=gender,password=password)
            db.session.add(user)
            db.session.commit()
            user_return = User.query.filter_by(user_name= user_name).first()
            return user_return


post_output = {
                "id" : fields.Integer,
                "tittle" : fields.String,
                "content" : fields.String,
                "user_id" : fields.Integer,
            }

post_parser = reqparse.RequestParser()
post_parser.add_argument('Title')
post_parser.add_argument('Content')
post_parser.add_argument('user_id')



class PostApi(Resource):
    @marshal_with(post_output)
    def get(self,id):
        post = Blogs.query.get(id)
        if post:
            return post
        else:
            raise NotFoundError(status_code=400)
    @marshal_with(post_output)
    def put(self,id):
        post_arg = post_parser.parse_args()
        title = post_arg.get('Title', None)
        content = post_arg.get('Content',None)
        post = Blogs.query.get(id)
        if post:
            if title and len(title)<2:
                raise BusninessValidationError(error_message = 'Title too short',status_code = 400)
            elif title:
                post.tittle = title
                if content:
                    post.content = content
                db.session.commit()
                post = Blogs.query.get(id)
                return post
        else:
            raise NotFoundError(status_code=404)
    def delete(self,id):
        post = Blogs.query.get(id)
        if post:
            db.session.delete(post)
            db.session.commit()
            return '',200
        else:
            raise NotFoundError(status_code=400)
    def post(self):
        post_arg = post_parser.parse_args()
        title = post_arg.get('Title', None)
        content = post_arg.get('Content',None)
        user_id = post_arg.get('user_id',None)
        user = User.query.get(user_id)
        if title and len(title)<2:
            raise BusninessValidationError(error_message = 'Title too short',status_code = 400)
        elif not title:
            raise BusninessValidationError(error_message = 'Title can\'t be empty',status_code = 400)
        elif content and len(content)<2:
            raise BusninessValidationError(error_message = 'Content too short',status_code = 400)
        elif not content:
            raise BusninessValidationError(error_message = 'Title can\'t be empty',status_code = 400)
        
        elif not user:
            raise BusninessValidationError(error_message = 'Invalid user_id',status_code = 400)
        else:
            post = Blogs(tittle = title,content = content, user_id = user_id)
            db.session.add(post)
            db.session.commit()
            return '',201


action_parser = reqparse.RequestParser()
action_parser.add_argument('follower_user_name')
action_parser.add_argument('Content')
 
class Actions(Resource):
    def post(self, user_name):
        arg = action_parser.parse_args()
        followee = arg.get('follower_user_name',None)
        if not followee :
            raise BusninessValidationError(error_message = 'Ivalid follower User Name',status_code = 400)
            
        followee_user = User.query.filter_by(user_name = followee).first()
        curr_user = User.query.filter_by(user_name = user_name).first()
        
        if curr_user and followee_user:
            flist = [ids.user_2 for ids in Followers.query.filter_by(user_1= curr_user.id).all()]
            if followee_user.id in flist:
                raise BusninessValidationError(error_message = 'Already following the user',status_code = 400)
            else: 
                flow = Followers(user_1 = curr_user.id,user_2 = followee_user.id)
                db.session.add(flow) 
                db.session.commit()
                
                return '',201
        
        else:
            raise NotFoundError(status_code=400)


    def delete(self,user_name,follower_user_name):
        followee_user = User.query.filter_by(user_name = follower_user_name).first()
        curr_user = User.query.filter_by(user_name = user_name).first()
        print(curr_user.id,followee_user.id)
        if curr_user and followee_user:
            flow = Followers.query.get((curr_user.id,followee_user.id))
            if not flow :
                raise BusninessValidationError(error_message = 'Invalid request. Users not following',status_code = 400)
            else: 
                db.session.delete(flow) 
                db.session.commit()
                return '',204
        
        else:
            raise NotFoundError(status_code=400)

class AllPost(Resource):
    def get(self,u_name):
        user = User.query.filter_by(user_name = u_name).first()
        if user:
            posts = Blogs.query.filter_by(user_id = user.id).all()
            all_post = {}
            a = 1
            for post in posts:
                post_dic = {}
                post_dic['title'] = post.tittle
                post_dic['content'] = post.content
                all_post[str(a)] = post_dic
                a +=1
            return all_post
        else:
            raise NotFoundError(status_code=400)
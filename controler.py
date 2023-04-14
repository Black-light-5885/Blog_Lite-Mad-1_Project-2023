from flask import render_template, redirect,flash
from flask import request
from model import *
import base64
import io
import os
import shutil
import PIL.Image as Image
from rapidfuzz import fuzz
from main import app
from flask_login import login_required, login_user,logout_user,current_user
from werkzeug.utils import secure_filename



# This line creates a route for the root URL ("/") and allows for both GET and POST methods
@app.route('/',methods=['GET','POST'])

# This defines a function called 'home' that will be executed when the root URL is accessed
def home():
    # This line uses the Flask 'render_template' function to render the 'welcome.html' template
    # and pass in the 'current_user' object as the 'user' variable
    return render_template('welcome.html', user = current_user)


# This code is a route for the login page that is accessible via a GET or POST request
# The code checks if the request method is POST, and if so, it gets the user_name and password from the form
# It then queries the User table to see if the user_name exists, and if it does, it checks if the password matches
# If the user_name and password match, the user is logged in and their profile picture is saved to the server
# If the user_name and password do not match, an error message is displayed and the user is prompted to try again
@app.route('/login', methods = ["GET","POST"])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        user = User.query.filter_by(user_name= user_name).first()
        if user != None and user.password == password:
            login_user(user)
            img = user.picture
            if img:
                img = Image.open(io.BytesIO(img))
                path = f'./static/Profile/{user.id}/profile.jpg'
                os.mkdir(f'./static/Profile/{user.id}')
                img.save(path)
            else:
                img = Image.open(f'./static/img/user_profile.webp')
                path = f'./static/Profile/{user.id}/profile.jpg'
                os.mkdir(f'./static/Profile/{user.id}')
                img.save(path)
            return redirect(f"/user/home")
        else:
            flash('User Name or Password Wrong..', category='error')
            return render_template('login.html', error_1='Id does not exsit', 
            error_2 = 'Password does not exsit',user = current_user)
    return render_template('login.html', user = current_user)





@app.route('/register', methods = ["GET","POST"])
def register():
    # check if the request method is POST
    if request.method == 'POST':
        # get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        user_name = request.form.get('user_name')
        password_1 = request.form.get('password')
        password_2 = request.form.get('password_2')
        gender = request.form.get('gender')
        profile = request.files['picture']
        # check if the user_name already exists
        user = User.query.filter_by(user_name = user_name).first()
        if user:
            # if user_name already exists, flash an error message and redirect to register page
            flash('User Name already exist.', category='error')
            return render_template('Register.html', error = 'Somethig went wrong',user= current_user)           
        elif len(first_name) < 2:
            # if first_name is too short, flash an error message and redirect to register page
            flash('Hey First Name is too short.', category='error')
            return render_template('Register.html', error = 'Somethig went wrong',user= current_user)
        elif len(password_1) <7:
            # if password_1 is too short, flash an error message and redirect to register page
            flash('Hey Passwords too shot.', category='error')
            return render_template('Register.html', error = 'Somethig went wrong',user= current_user)
        elif password_1 != password_2:
            # if password_1 and password_2 do not match, flash an error message and redirect to register page
            flash('Hey Passwords doesnt match.', category='error')
            return render_template('Register.html', error = 'Somethig went wrong', user= current_user)

        else:
            # create a new user with the form data and add it to the database
            user = User(first_name=first_name,last_name=last_name,user_name=user_name,password=password_1,
             gender = gender,picture = profile.read())
            db.session.add(user)
            db.session.commit()
            # redirect to login page
            return redirect("/login")
    # if the request method is GET, render the register template
    return render_template('Register.html', user = current_user)




# This code creates a route for the logout page and ensures that the user is logged in before proceeding
@app.route('/logout')
@login_required
def logout():
    # Get the current user
    user = current_user
    # Delete the user's profile folder from the static directory
    shutil.rmtree(f'./static/Profile/{user.id}')
    # Log the user out
    logout_user()
    # Redirect the user to the login page
    return redirect('/login')


def home_management():
    # Get the current logged in user
    user = current_user
    
    # Get all the followers for the current user
    followers = Followers.query.filter_by(user_1 = user.id).all()
    
    # Initialize an empty list to store all the followers' blog posts
    blogs = []

    # Iterate through each follower and get their blog posts
    for user_ in followers:
        blog = Blogs.query.filter_by(user_id = user_.user_2).all()
        # Append the blog posts to the blogs list
        blogs=blogs+blog
    
    # Initialize an empty list to store the final posts data
    posts = []
    
    # Iterate through each blog post
    for blog in blogs:
        # Check if the post is not private
        if not blog.privacy:
            # Create a dictionary to store the post data
            post_dic ={}
            # Add the blog post data to the dictionary
            post_dic['data'] = blog
            # Get the profile picture of the post author and convert it to base64
            post_dic['profile'] = base64.b64encode(User.query.get(blog.user_id).picture).decode('utf-8')
            # Get the image of the post and convert it to base64
            img = base64.b64encode (blog.image)
            img = img.decode('utf-8')
            post_dic['img']=img
            # Get all the comments on the post
            comment_ = Comments.query.filter_by(blog = blog.id).all()
            # Get the author of the post
            post_user = User.query.get(blog.user_id)
            # Get the first name of the post author
            p_user_name = post_user.first_name
            # Add the post author's name to the dictionary
            post_dic['post_user']= p_user_name
            comments={}
            # Iterate through each comment
            for com in comment_ :
                # Check if the comment is made by the current user
                if com.user == user.id:
                    comments['you'] = com.comment
                else:
                    # Get the user who made the comment
                    c_user = User.query.get(com.user)
                    # Get the first name of the user who made the comment
                    c_user_name = c_user.first_name
                    comments[c_user_name] = com.comment
            # Add the comments to the dictionary
            post_dic['comments']=comments
            # Append the post data to the final posts list
            posts.append(post_dic)
    # Return the final list of posts
    return posts

@app.route('/user/home',methods=['GET',"POST"]) # Route for the user home page, allowing both GET and POST methods
@login_required # Decorator to check if the user is logged in before accessing the page
def user_home(): # Function to handle the user home page
    user = current_user # Get the current logged in user
    home_posts = home_management() # Get the posts for the user's home page
    return render_template('home.html', user= current_user,posts = home_posts) # Render the home page template with the current user and their home posts


def profile_data(user):
    # Assign the current user to user_current variable
    user_current = current_user
    # Encode and decode the user's profile picture
    profile = base64.b64encode(User.query.get(user.id).picture).decode('utf-8')
    # Get all the users that the current user is following
    following = Followers.query.filter_by(user_1 = user.id).all()
    # Get all the users that are following the current user
    followers = Followers.query.filter_by(user_2 = user.id).all()
    # Get all the blogs of the current user
    blogs = Blogs.query.filter_by(user_id = user.id).all()
    posts = []
    # Iterate through each blog
    for blog in blogs:
        # Check if the blog is private or if the user is the owner of the blog
        if not blog.privacy or blog.user_id == user_current.id:
            post_dic ={}
            post_dic['data'] = blog
            # Encode and decode the blog's image
            img = base64.b64encode (blog.image)
            img = img.decode('utf-8')
            post_dic['img']=img
            comment_ = Comments.query.filter_by(blog = blog.id).all()
            comments={}
            # Iterate through each comment
            for com in comment_ :
                # Check if the comment is made by the current user
                if com.user == user.id:
                    comments['you'] = com.comment
                else:
                    c_user = User.query.get(com.user)
                    c_user_name = c_user.first_name
                    comments[c_user_name] = com.comment
            post_dic['comments']=comments
            posts.append(post_dic)
    # Return the blog posts, following, followers, and profile picture
    return posts,following,followers, profile

# This code is defining a route for the user profile page, and it requires the user to be logged in.
@app.route('/user/profile') # Defining the route for the user profile page
@login_required # Requiring the user to be logged in to access the page
def user_profile():
    user = current_user # Getting the current user
    posts,following,followers,profile = profile_data(user) # Getting the posts, following, followers, and profile data for the user
    return render_template('profile.html', user_ = user, following = following, 
                followers = followers, posts =posts,user = user, profile = profile ) # Rendering the profile.html template and passing in the user data



@app.route('/user/profile/<int:user_id>')
@login_required
def post_user_profile(user_id):
    # Get the current logged in user
    user = current_user
    # Check if the current user's id matches the user id in the URL
    if user.id == user_id:
        # If it does, redirect the user to their own profile page
        return redirect('/user/profile')
    else:
        # If it doesn't, get the user from the database using the user id in the URL
        user_ = User.query.get(user_id)
        # Get the current user's followers 
        flow = Followers.query.filter_by(user_1 = user.id)
        # Create a list of the current user's followers
        ur_flow =[usr.user_2 for usr in flow]
        # Get the profile data for the user in the URL
        posts, following, followers, profile = profile_data(user_)
        # Check if the user in the URL is one of the current user's followers
        if user_id in ur_flow:
            # If they are, render the profile template with the user's data
            return render_template('profile.html', user_ = user_, following = following, 
                followers = followers, posts =posts,user = current_user,profile = profile )
        else:
            # If they are not, render the restricted profile template with the user's data
            return render_template('restricted_profile.html',user_ = user_,following = following, 
                followers = followers, user = current_user,profile=profile)




# This is a function that handles the routing for a search for a user.
# It is decorated with the @app.route and @login_required decorators, meaning that it can only be accessed
# by logged in users and is accessed via a POST request to the '/user/search' endpoint

@app.route('/user/search',methods=["POST"])
@login_required
def user_search():
    # Initialize a variable that keeps track if a search returns no results
    not_found = False
    # Get the search key from the form data in the request
    original = request.form.get('search_key')
    search_key = original
    # Get the current logged in user
    user = current_user
    # Initialize a list to store the IDs of users that the current user is following
    follow_list = []
    # Get all of the user's followers from the Followers table
    followers = Followers.query.filter_by(user_1 = user.id).all()
    # Add the IDs of the followers to the follow_list
    for a in followers:
        follow_list.append(a.user_2)
    # Search for users with first names like the search key and store them in a list
    search_list = User.query.filter(User.first_name.like('%'+search_key+'%')).all()
    # Search for users with last names like the search key and store them in a list
    search_list_2 = User.query.filter(User.last_name.like('%'+search_key+'%')).all()
    # Add the users from the last names search to the first names search list
    search_list.extend(search_list_2)
    # Search for users with usernames like the search key and store them in a list
    search_list_3 = User.query.filter(User.user_name.like('%'+search_key+'%')).all()
    # Add the users from the usernames search to the first names and last names search list
    search_list.extend(search_list_3)
    
    # If the search returns less than 2 results, check for partial matches using the fuzz library
    if len(search_list) < 2 :
        if len(search_list) < 1:
            # If there are no results, set not_found to True
            not_found = True
        # Get all users from the User table
        all_users = User.query.all()
        # Check each user's first name, last name, and username for a partial match with the search key
        for user in all_users:
            if fuzz.partial_ratio(search_key,user.first_name) >=50:
                search_list.append(user)
            elif fuzz.partial_ratio(search_key,user.last_name) >=50:
                search_list.append(user)
            elif fuzz.partial_ratio(search_key,user.user_name) >=50:
                search_list.append(user)
    # Remove any duplicate users from the search list
    search_list = list(set(search_list))
    # Initialize a final search list to store the search results in a dictionary format
    search_list_final =[]
    for a in search_list:
        user_dic = {}
        user_dic['data'] = a
        user_dic['profile'] = base64.b64encode(User.query.get(a.id).picture).decode('utf-8')
        search_list_final.append(user_dic)
    return render_template('search.html', user_list = search_list_final, search_key= original,
                             user = current_user, follow_list = follow_list, not_found = not_found)

@app.route('/user/follow/<int:user_id>', methods=['POST'])
@login_required  #decorator to check if user is logged in
def follow(user_id):
    user = current_user  #get the current user
    req = Followers(user_1 = user.id,user_2 = user_id)  #create a new followers request with current user as user_1 and user_id as user_2
    db.session.add(req)  #add the request to the database session
    db.session.commit()  #commit the changes to the database
    return {} #redirect('/user/home')  #redirect the user to their home page


# Define the route and request method
@app.route('/user/unfollow/<int:user_id>', methods=['POST'])
@login_required
def un_follow(user_id):
    # Get the current logged in user
    user = current_user
    # Retrieve the follow request from the Followers table where the current user is the follower and the user_id is the followee
    req = Followers.query.get((user.id,user_id))
    # Delete the follow request from the database
    db.session.delete(req)
    # Commit the changes to the database
    db.session.commit()
    return {} #redirect('/user/home')


@app.route('/user/following')
def show_following():
    # Get the current logged in user
    user = current_user
    # Get all the followers of the current user
    flws = Followers.query.filter_by(user_1 = user.id).all()
    # Create an empty list to store user data
    users = []
    # Loop through the followers
    for u in flws:
        # Create an empty dictionary to store user data
        user_dic = {}
        # Get the user data for the current follower
        user_a = User.query.get(u.user_2)
        # Add the user data to the dictionary
        user_dic['data'] = user_a
        # Add the base64 encoded profile picture to the dictionary
        user_dic['profile'] = base64.b64encode(user_a.picture).decode('utf-8')
        # Add the dictionary to the list of users
        users.append(user_dic)
    # Render the following template with the user list and the current user
    return render_template("following.html", user_list = users, user = current_user)

@app.route('/user/followers/')
@login_required
def show_followers():
    # Get the current logged in user
    user = current_user
    # Get all the followers for the current user where user_2 = user.id
    flws = Followers.query.filter_by(user_2 = user.id).all()
    # Create an empty list to store the followers
    follow_list = []
    # Get all the people the current user is following where user_1 = user.id
    followers = Followers.query.filter_by(user_1 = user.id).all()
    # Iterate over the followers and append their user_2 to the follow_list
    for a in followers:
        follow_list.append(a.user_2)
    # Create an empty list to store the user data
    users = []
    # Iterate over the followers and get the user data and profile picture
    for u in flws:
        user_dic = {}
        user_a = User.query.get(u.user_1)
        user_dic['data'] = user_a
        user_dic['profile'] = base64.b64encode(user_a.picture).decode('utf-8')
        users.append(user_dic)
    # Render the followers template with the user data and follow_list
    return render_template("followers.html", user_list = users, user = current_user,
    follow_list=follow_list)


@app.route('/user/create_blog', methods = ["GET","POST"])
@login_required
def create_blog():
    # Get the currently logged in user
    user = current_user
    if request.method =='POST':
        # Get the title, content, and privacy from the form data
        title = request.form.get('title')
        content = request.form.get('content')
        privacy = request.form.get('privacy')
        
        # Convert the privacy string to a boolean value
        if privacy =='false':
            privacy = False
        else:
            privacy = True
        
        # Get the picture file and secure the file name
        pic = request.files['picture']
        file_name = secure_filename(pic.filename)
        
        # Create a new blog object and add it to the database
        blog = Blogs(tittle=title, content = content,image=pic.read(),
        image_name=file_name,  user_id = user.id, privacy = privacy)
        db.session.add(blog)
        db.session.commit()
        
        # Redirect the user to the home page
        return  redirect('/user/home')
    # Render the create_post template for GET requests
    return render_template('create_post.html', user = user)



# This code defines a route for updating a post for the current logged in user.
# The route takes in the post_id as a parameter and only allows for GET and POST methods
# The login_required decorator is used to ensure that only logged in users can access this route

@app.route('/user/update_post/<int:post_id>', methods = ["GET","POST"]) # Define the route and specify the allowed methods
@login_required # Ensure that only logged in users can access this route
def update_post(post_id):
    bb = current_user
    # Get the post with the specified id
    post = Blogs.query.get(post_id)
    if not post or post.user_id != bb.id:
        return redirect('/user/profile')
    # Encode the image of the post
    img = base64.b64encode (post.image)
    # Decode the encoded image
    post_picture = img.decode('utf-8')
    if request.method =='POST':
        # Initialize flag to check if any changes were made
        flag = False
        # Get the title and content from the form
        title = request.form.get('title')
        content = request.form.get('content')
        # Get the picture from the form
        pic = request.files['picture']
        # Check if the title has been changed
        if title != post.tittle:
            flag = True
            # Update the title of the post
            post.tittle = title
        # Check if the content has been changed
        if content != post.content:
            # Update the content of the post
            post.content = content
            flag = True
        # Check if a new picture was uploaded
        if pic:
            flag = True
            # Update the image and image name of the post
            post.image = pic.read()
            post.image_name = secure_filename(pic.filename)
        # Check if any changes were made
        if flag:
            # Commit the changes to the database
            db.session.commit()
        # Redirect the user to the home page
        return redirect('/user/profile')
     
    # Render the update_post template and pass in the current user, post, and post picture
    return render_template('update_post.html', user= current_user, post_ = post, post_picture=post_picture)


@app.route('/blog/like/<blog_id>',methods = ['POST'])
@login_required
def like_blog(blog_id):
    # get the blog from the database using its id
    blog = Blogs.query.get(blog_id)
    # increment the likes count by 1
    blog.likes = blog.likes +1
    # add the updated blog to the database session
    db.session.add(blog)
    # commit the changes to the database
    db.session.commit()
    # return an empty object and a status code of 200 to indicate success
    return {},200


@app.route('/user/blog/comment/<comment>/id/<blog_id>',methods = ['post'])
# This line sets the route for a specific URL with variables for the comment and blog_id
@login_required
# This line ensures that the user is logged in before allowing them to add a comment
def add_comment(comment,blog_id):
    # This function takes in the comment and blog_id as arguments
    user = current_user
    # This line sets the user variable as the current logged in user
    cumment = Comments(user=user.id,blog = blog_id,comment =comment)
    # This line creates a new comment object with the user's id, the blog's id, and the comment text
    db.session.add(cumment)
    # This line adds the new comment to the database
    db.session.commit()
    # This line saves the new comment to the database
    return {},200


# Routing the URL '/user/blog/delete/<blog_id>' with DELETE request method
@app.route('/user/blog/delete/<blog_id>', methods=['DELETE'])
# Checking if user is logged in before executing the function
@login_required
# Defining function to delete a blog post
def blog_delete(blog_id):
    
    # Retrieving the blog post from the database using the blog_id
    blog = Blogs.query.get(blog_id)
    
    # Assigning the current user to a variable
    user = current_user
    
    # Checking if the blog post belongs to the logged in user and if it exists
    if blog.user_id == user.id and blog:
        
        # Deleting the blog post from the database
        db.session.delete(blog)
        
        # Committing the changes to the database
        db.session.commit()
        
        # Returning success status code
        return {},200
    
    # If the blog post doesn't belong to the logged in user or doesn't exist
    else:
        
        # Returning failure status code
        return {},400


@app.route('/user/delete/<int:user_id>')
@login_required
# Defining function to delete a user
def user_delete(user_id):
    shutil.rmtree(f'./static/Profile/{user_id}')
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Account deleted successfully', category='Success')
    return redirect('/register')



























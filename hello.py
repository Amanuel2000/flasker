from flask import Flask, render_template, flash, request, redirect, url_for
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm, CommentForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os


# create a Flask Instance
app = Flask(__name__)
# Add CKeditor
ckeditor = CKEditor(app)

# Add Database
# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///users.db"

# New MySQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:password@localhost/our_users"
# Secret Key
app.config['SECRET_KEY'] = "My secret key that no one is going to know"

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# create check page


# pass stuff to Navbar


@app.context_processor
def base():
    form = SearchForm()
    return {"form": form}
# create admin page


@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 17:
        return render_template("admin.html")
    else:
        flash("Sorry you must be the admin to access this Admin page...")
        return redirect(url_for("dashboard"))

# Create Search Function


@app.route('/search', methods=["POST"])
def search():
    name = None
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # Get data from submitted form
        post.searched = form.searched.data
        # Query the  Database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html", form=form, searched=post.searched, posts=posts)


# Register users
@app.route('/register', methods=['GET', 'POST'])
def register():
    name = None
    form = UserForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the Password
            hashed_pw = generate_password_hash(form.password_hash.data)
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data,
                         password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.password_hash.data = ''

        flash("Registered Successfully!, Please continue login and access your dashboard")
        return redirect(url_for('login'))
    else:
        return render_template("register.html", form=form)

# create Login page


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Succesfull!!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!")
        else:
            flash("That User Doesn't Exist! Try Again...")
    return render_template('login.html', form=form)

# Create Logout Page


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out!  Thanks For Stopping By...")
    return redirect(url_for('login'))

# Create Dashboard Page


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        # name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.about_author = request.form['about_author']

        # Check for profile pic
        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']
            # Grab Image Name
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            # Set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            # Save That Image
            saver = request.files['profile_pic']

            # Change it to a string to save to db
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash("User Updated Successfully!")
                return render_template("dashboard.html",
                                       form=form,
                                       name_to_update=name_to_update)
            except:
                flash("Error!   Looks like there was a problem")
                return render_template("dashboard.html",
                                       form=form,
                                       name_to_update=name_to_update)
        else:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update)
    else:
        return render_template("dashboard.html",
                               form=form,
                               name_to_update=name_to_update,
                               id=id)

    return render_template("dashboard.html")


# Forum posts
@app.route('/posts')
def posts():
    # Grab all the posts fromt he database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)


@app.route('/about')
def about():
    return render_template("about.html")

# Create Delete route


@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id or id == 17:

        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            # return a message
            flash("Message post was delted Successfully")

            # Grab all the posts fromt he database
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
        except:
            # Return an Error
            flash("Whoops! There was a problem deleting post, try again...")

            # Grab all the posts fromt he database
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    else:
        # return a message
        flash("You aren't authorized to delete that post")

        # Grab all the posts fromt he database
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

# Forum Comments


@app.route("/create-comment/<post_id>", methods=['POST'])
def create_comment(post_id):
    form = CommmentForm()
    if form.validate_on_submit():
        comment = Comments(comment=form.comment.data)
    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Posts.query.filter_by(id=post_id)
        if post:
            comment = Comments(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return render_template("post.html", post=post)


@app.route('/posts/<int:id>')
def comment(id):
    comments = Comments.query.order_by(Comments.date_commented)
    return render_template("post.html", post=post)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        # post.slug = form.slug.data
        post.content = form.content.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated!")
        return redirect(url_for('post', id=post.id))

    if current_user.id == post.poster_id or current_user.id == 17:
        form.title.data = post.title
        # form.author.data =post.author
        # form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You aren't authorized to edit this post ...")
        # Grab all the posts fromt he database
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data,
                     poster_id=poster)
        form.title.data = ''
        form.content.data = ''
        # form.author.data = ''

        # Add post to data base

        db.session.add(post)
        db.session.commit()

        # Return a Message
        flash("Message Post Submitted Successfully")

     # Redirect to the webpage
    return render_template("add_post.html", form=form)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if id == current_user.id or current_user.id == 17:
        user_to_delete = Users.query.get_or_404(id)
        name = None
        form = UserForm()

        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User Deleted Successfully")

            our_users = Users.query.order_by(Users.date_added)
            return render_template("add_user.html",
                                   form=form,
                                   name=name,
                                   our_users=our_users)
        except:
            flash("Whoops! there was a problem delting a user, try again ...")
            return render_template("add_user.html",
                                   form=form,
                                   name=name,
                                   our_users=our_users)
    else:
        flash("Whoops! Sorry you can't delete that user ...")
        return redirect(url_for('dashboard'))


# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']

        name_to_update.username = request.form['username']

        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
        except:
            flash("Error!  Looks like there was a problem...try again!")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)
    else:

        return render_template("update.html", form=form,
                               name_to_update=name_to_update,
                               id=id)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the Password
            hashed_pw = generate_password_hash(form.password_hash.data)
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data,
                         password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.password_hash.data = ''

        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
                           form=form,
                           name=name,
                           our_users=our_users)

# creat a route decorator


@app.route('/')
def index():
    # first_name = "Jhon"
    # stuff = "This is <strong> Bold </strong> Text"
    # favorite_pizza = ["pepperoni", "Cheese", "Mushrooms", 41]
    return render_template("index.html",)
    # first_name = first_name,
    # stuff = stuff,
    # favorite_pizza =  favorite_pizza )

# localhost:5000/user/Jhon
# @app.route('/user')
# def user():
 #   return render_template("users.html",  ) # using jinja variable

# @app.route('/users')
# def users():
    # Grab all the posts fromt he database
 #   users = Users.query.order_by(Users.date_posted)
  #  return render_template("users.html",users=users)
# create Custom Error Pages
# Invalid URL


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Internal Server Error thing
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data

        form.email.data = ''
        form.password_hash.data = ''
        # Lookup User By Email Address
        pw_to_check = Users.query.filter_by(email=email).first()
        # Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template("test_pw.html",
                           email=email,
                           password=password,
                           pw_to_check=pw_to_check,
                           passed=passed,
                           form=form)

# Create Name Page


@app.route('/user', methods=['GET', 'POST'])
def user():
    user = None
    form = UserForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully!")

    return render_template("users.html",
                           user=user,
                           form=form)


# Create  A Forum Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Key To Link Users (refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# Create a Comment Model


class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text)
    date_commented = db.Column(db.DateTime, default=datetime.utcnow)
    # Foreign Key To Link Users (refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

# Create a model


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    # password_hash = db.Column(db.String(120))
    # password_hash2 = db.Column(db.String(120))
    # favorite_color = db.Column(db.String(200))
    about_author = db.Column(db.Text(200), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(200), nullable=True)

    # Do some password stuff!
    password_hash = db.Column(db.String(128))
    # Users can have many posts
    posts = db.relationship('Posts', backref='poster')

    @property
    def password(self):
        raise AttributeError('password is not a readble attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # create A String
    def __repr__(self):
        return '<Name %r>' % self.name


if (__name__ == "__main__"):
    app.run(debug=False, host='0,0,0,0')

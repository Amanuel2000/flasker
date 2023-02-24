from flask import Flask, render_template


#create a Flask Instance
app = Flask(__name__)

# creat a route decorator
@app.route('/')

# def index():
#     return "<h1> Hello People </h1>"


# safe
# capitalize
# lower 
# upper
# title
# trim
# striptags


def index():
    first_name = "Jhon"
    stuff = "This is <strong> Bold </strong> Text"
    favorite_pizza = ["pepperoni", "Cheese", "Mushrooms", 41]
    return render_template("index.html",
                           first_name = first_name,
                          stuff = stuff,
                           favorite_pizza =  favorite_pizza )

#localhost:5000/user/Jhon
@app.route('/user/<name>')

def user(name):
    return render_template("user.html", user_name = name) # using jinja variable


#create Custom Error Pages
# Invalid URL
@app.errorhandler(404)

def page_not_found(e):
    return render_template("404.html"), 404

 
# Internal Server Error
@app.errorhandler(500)

def page_not_found(e):
    return render_template("500.html"), 500
    
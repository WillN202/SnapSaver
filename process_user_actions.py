from db_connect import db_operations
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import UserMixin, login_user, LoginManager, current_user
app = Flask(__name__)

class User(UserMixin):
    def __init__(self, email, name, postcode, userID):
        self.email = email
        self.name = name
        self.postcode = postcode
        self.id = userID

    def is_anonymous(self):
        return False

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

def register_user():
    email = request.form["email"]
    passw1 = request.form["password1"]
    passw2 = request.form["password2"]
    postcode = request.form["postcode"]
    username = request.form["username"]

    if email == "" or passw1 == "" or passw2 == "" or postcode == "" or username == "":
        print("err1")
        return render_template("Register.html", err="Enter all the information required!")

    if passw1 != passw2:
        print("err2")
        return render_template("Register.html", err="Passwords do not match")

    db = db_operations()
    if not (db.insert_user(email, passw1, username, postcode)):
        return render_template("Register.html", err="Account already registered with same email, or unknown error")
    
    return redirect(url_for("show_login"))


def process_login():
    if request.form["email"] == "" or request.form["password"] == "":
        return render_template("Login.html", err="Enter an email and password!")

    db = db_operations()
    if (db.verify_user(request.form["email"], request.form["password"])):
        print("user verified")
        
        flash("Successful login, redirecting")

        item = db.get_email_name(request.form["email"])
        tempUsr = User(item[0], item[1], item[2], item[3])
        if "remember" in request.form:
            login_user(tempUsr, remember=request.form["remember"])
        else:
            login_user(tempUsr)
        return redirect(url_for("show_index"))
    else:
        print("user unverified")

        return render_template("Login.html", err="User not found with that email and password")


def change_details():
    arguments = list(request.form.keys())
    db = db_operations()
    print(arguments)
    if arguments[1] == "name":
        db.alter_name(request.form["name"], current_user.id)
        flash("Name Updated")
    elif arguments[1] == "email":
        db.alter_email(request.form["email"], current_user.id)
        flash("Email Updated")
    elif arguments[1] == "postcode":
        db.alter_postcode(request.form["postcode"], current_user.id)
        flash("Postcode Updated")
    elif arguments[1] == "pass1":

        if request.form["pass1"] == request.form["pass2"]:
            db.alter_password(request.form["pass1"], current_user.id)
            flash("Password Updated")
        else:
            flash("Passwords Do Not Match")

    else:
        flash("Invalid data entry")

    return render_template("Profile.html")
    
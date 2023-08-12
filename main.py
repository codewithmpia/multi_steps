from pathlib import Path

from flask import Flask, render_template, request, session, flash

from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import FlaskForm
from wtforms.fields import StringField, EmailField, PasswordField
from wtforms.validators import DataRequired, Email
from flask_bootstrap import Bootstrap5

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=BASE_DIR / "assets/templates",
    static_folder=BASE_DIR / "assets/static"
)
app.config["SECRET_KEY"] = "top-secret"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR}/db.sqlite3"

db = SQLAlchemy(app)
bootstrap = Bootstrap5(app)
Session(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __str__(self):
        return self.username


class UsernameForm(FlaskForm):
    username = StringField(
        label="Nom d'utilisateur", 
        validators=[DataRequired()]
    )


class EmailForm(FlaskForm):
    email = EmailField(
        label="Adresse email", 
        validators=[DataRequired(), Email()]
    )


class PasswordForm(FlaskForm):
    password = PasswordField(
        label="Mot de passe", 
        validators=[DataRequired()]
    )


class ConfirmPasswordForm(FlaskForm):
    confirm = PasswordField(
        label="Confirmer le mot de passe", 
        validators=[DataRequired()]
    )


@app.route("/", methods=("GET", "POST"))
def index():
    username_form = UsernameForm()
    session.pop("user", None)

    if "user" not in session:
        session["user"] = {}

    if request.method == "POST" and username_form.validate_on_submit():
        username = username_form.username.data

        session["user"]["username"] = username

        return render_template("email.html", email_form=EmailForm())
    
    elif username_form.errors:
        flash(username_form.errors, "warning")

    return render_template(
        "index.html",
        username_form=username_form
    )


@app.route("/username/edit/", methods=("GET", "POST"))
def edit_username():
    username = session["user"]["username"]

    username_form = UsernameForm()

    if request.method == "POST" and username_form.validate_on_submit():
        session["user"]["username"] = username_form.username.data

        return render_template("email.html", email_form=EmailForm())
    
    elif username_form.errors:
        flash(username_form.errors, "warning")

    return render_template(
        "edit_username.html",
        username_form=username_form,
        username=username
    )
    

@app.route("/email/", methods=("GET", "POST"))
def get_email():
    email_form = EmailForm()

    if request.method == "POST" and email_form.validate_on_submit():
        session["user"]["email"] = email_form.email.data

        return render_template(
            "password.html",
            password_form=PasswordForm()
        )
    
    elif email_form.errors:
        flash(email_form.errors)

    return render_template(
        "email.html",
        email_form=email_form
    )


@app.route("/email/edit/", methods=("GET", "POST"))
def edit_email():
    email = session["user"]["email"]
    email_form = EmailForm()

    if request.method == "POST" and email_form.validate_on_submit():
        session["user"]["email"] = email_form.email.data

        return render_template(
            "password.html",
            password_form=PasswordForm()
        )
    
    elif email_form.errors:
        flash(email_form.errors, "warning")

    return render_template(
        "edit_email.html",
        email_form=email_form,
        email=email
    )


@app.route("/password/", methods=("GET", "POST"))
def get_password():
    password_form = PasswordForm()

    if request.method == "POST" and password_form.validate_on_submit():
        session["user"]["password"] = password_form.password.data

        return render_template(
            "confirm_password.html",
            confirm_password_form=ConfirmPasswordForm()
        )
    
    elif password_form.errors:
        flash(password_form.errors, "warning")

    return render_template(
        "password.html",
        password_form=password_form 
    )


@app.route("/password/edit/", methods=("GET", "POST"))
def edit_password():
    password_form = PasswordForm()

    if request.method == "POST" and password_form.validate_on_submit():
        session["user"]["password"] = password_form.password.data

        return render_template(
            "confirm_password.html",
            confirm_password_form = ConfirmPasswordForm()
        )
    
    elif password_form.errors:
        flash(password_form.errors, "warning")

    return render_template(
        "edit_password.html",
        password_form=password_form
    )


@app.route("/password/confirm/", methods=("GET", "POST"))
def get_password_confirm():
    confirm_password_form = ConfirmPasswordForm()
    message = ""

    if request.method == "POST" and confirm_password_form.validate_on_submit():
        if session["user"]["password"] == confirm_password_form.confirm.data:
            new_user = User(
                username=session["user"]["username"],
                email=session["user"]["email"],
                password=session["user"]["password"]
            )
            db.session.add(new_user)
            db.session.commit()

            session.pop("user", None)

            flash("Inscription effectuée avec succès.", "success")

            return render_template("complete.html")
        
        else:
            message = "Les mots de passe ne correspondent pas."   
    
    elif confirm_password_form.errors:
        flash(confirm_password_form.errors, "warning")

    return render_template(
        "confirm_password.html",
        confirm_password_form=confirm_password_form,
        message=message
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


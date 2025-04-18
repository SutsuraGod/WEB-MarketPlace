from flask import Flask, render_template, redirect, abort, request, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_restful import Api
from data import db_session
from data.users import Users
from forms.login_form import LoginForm, RegisterForm

app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = 'webservicekey'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/marketplace.db")
    app.run(debug=True)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def user_loader(user_id):
    session = db_session.create_session()
    return session.query(Users).get(user_id)


@app.route('/')
def main_page():
    return render_template("main_page.html", title="Маркетплейс", products=[])


@app.route("/register", methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        session = db_session.create_session()

        if session.query(Users).filter(Users.email == form.email.data).first():
            return render_template("register.html", title="Регистрация", message="Такой пользователь уже существует",
                                   form=form)

        user = Users(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)

        session.add(user)

        logout_user()

        session.commit()
        return redirect("/login")
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(Users).filter(Users.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")

        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


if __name__ == '__main__':
    main()

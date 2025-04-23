import os
from flask import Flask, render_template, redirect, abort, request, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_restful import Api
from data import db_session
from data.users import Users
from data.avatars import Avatars
from data.ads import Ads
from data.images import Images
from forms.login_form import LoginForm, RegisterForm
from forms.ad_form import AdForm
from werkzeug.utils import secure_filename

app = Flask(__name__)
api = Api(app)

# секретный ключ для защиты
app.config['SECRET_KEY'] = 'webservicekey'
# папка для загрузки фотографий
app.config["UPLOAD_FOLDER"] = "static/img"

# объект класса для регистрации и авторизации пользователя
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    # создание библиотеки
    db_session.global_init("db/marketplace.db")
    # запуск приложения
    app.run(debug=True)


@app.route("/logout")
@login_required
def logout():
    '''Выход пользователя из аккаунта и перенаправление на главную страницу'''
    logout_user()
    return redirect("/")


@login_manager.user_loader
def user_loader(user_id):
    '''Создание сессии пользователя'''
    session = db_session.create_session()
    return session.query(Users).get(user_id)


@app.route('/')
def main_page():
    '''Обработчик главной страницы'''
    session = db_session.create_session()
    ads = session.query(Ads).all()
    return render_template("main_page.html", title="Маркетплейс", ads=ads)


@app.route("/register", methods=['GET', 'POST'])
def register_page():
    '''Обработчик страницы регистрации'''
    form = RegisterForm()
    if form.validate_on_submit():
        session = db_session.create_session()

        # проверка на существование пользователя
        if session.query(Users).filter(Users.email == form.email.data).first():
            return render_template("register.html", title="Регистрация", message="Такой пользователь уже существует",
                                   form=form)

        # создание пользователя
        user = Users(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)

        session.add(user)

        logout_user()

        session.commit()
        # перенаправление пользователя на страницы авторизации
        return redirect("/login")
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    '''Обработчик страницы авторизации'''
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(Users).filter(Users.email == form.email.data).first()

        if user and user.check_password(form.password.data):  # проверка на валидность введенных данных
            # авторизация пользователя и дальнейшее перенаправление его на главную страницу
            login_user(user, remember=form.remember_me.data)
            return redirect("/")

        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/profile/<user_id>")
@login_required
def profile_page(user_id):
    '''Обработчки профиля страницы'''
    session = db_session.create_session()
    # получения id пользователя и пути до картинки аватара
    user = session.query(Users).get(user_id)
    ads = session.query(Ads).all()
    image_path = session.query(Avatars.image_path).filter(Avatars.user_id == user_id).first()
    return render_template("profile.html", title="Профиль пользователя", user=user, image_path=image_path, ads=ads)


@app.route("/create_ad", methods=["GET", "POST"])
@login_required
def create_ad():
    '''Обработчик создания объявления'''
    form = AdForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        ad = Ads(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            category=int(form.categories.data),
            city=form.city.data
        )
        session.add(ad)
        session.commit()

        # загрузка файлов на сервер
        uploaded_file = form.images.data

        if len(uploaded_file) > 5:
            return render_template("create_ad.html", title="Создание объявления", form=form,
                                   message="Можно загрузить не больше 5 изображений")

        for file in uploaded_file:
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)
                image = Images(
                    ad_id=ad.id,
                    image_path=filepath
                )
                session.add(image)
                session.commit()

        return redirect("/")
    return render_template("create_ad.html", title="Создание объявления", form=form)


if __name__ == '__main__':
    main()

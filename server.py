import os
import uuid
from sqlalchemy.orm import joinedload
from flask import Flask, render_template, redirect, abort, request, make_response, jsonify
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_restful import Api
from data import db_session
from data.users import Users
from data.ads import Ads
from data.images import Images
from data.categories import Categories
from data.avatars import Avatars
from data.reviews import Reviews
from forms.login_form import LoginForm, RegisterForm
from forms.ad_form import AdForm
from forms.review_form import ReviewForm
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
api = Api(app)

# секретный ключ для защиты
app.config['SECRET_KEY'] = 'webservicekey'
# папка для загрузки фотографий
app.config["IMAGE_UPLOAD_FOLDER"] = "static/img"
app.config["AVATAR_UPLOAD_FOLDER"] = "static/avatars"

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
    with db_session.create_session() as session:
        return session.query(Users).get(user_id)


@app.route('/')
def main_page():
    '''Обработчик главной страницы'''
    with db_session.create_session() as session:
        ads = session.query(Ads).all()
        images = []
        categories = []
        for ad in ads:
            image = session.query(Images).filter(Images.ad_id == ad.id).first()
            images.append(image.image_path)
            category = session.query(Categories).filter(ad.category == Categories.id).first()
            categories.append(category.category)

    return render_template("main_page.html", title="Маркетплейс", ads=ads, images=images, categories=categories)


@app.route("/register", methods=['GET', 'POST'])
def register_page():
    '''Обработчик страницы регистрации'''
    form = RegisterForm()
    if form.validate_on_submit():
        with db_session.create_session() as session:
            # проверка на существование пользователя
            if session.query(Users).filter(Users.email == form.email.data).first():
                return render_template("register.html", title="Регистрация",
                                       message="Такой пользователь уже существует",
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

            # добавление базового аватара
            with open('static/avatars/base_avatar.png', 'rb') as f:
                class FileObj:
                    filename = 'base_avatar.jpg'
                    stream = f

                    def read(self, *args, **kwargs):
                        return self.stream.read(*args, **kwargs)

                file_obj = FileObj()
                save_avatar(file_obj, user.id)

        # перенаправление пользователя на страницы авторизации
        return redirect("/login")
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    '''Обработчик страницы авторизации'''
    form = LoginForm()
    if form.validate_on_submit():
        with db_session.create_session() as session:
            user = session.query(Users).filter(Users.email == form.email.data).first()

        if user and user.check_password(form.password.data):  # проверка на валидность введенных данных
            # авторизация пользователя и дальнейшее перенаправление его на главную страницу
            login_user(user, remember=form.remember_me.data)
            return redirect("/")

        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/profile/<user_id>")
def profile_page(user_id):
    '''Обработчки профиля страницы'''
    with db_session.create_session() as session:
        # получения id пользователя и пути до картинки аватара
        user = session.query(Users).filter(Users.id == user_id).first()
        ads = session.query(Ads).filter(Ads.user_id == user_id).all()
        image_path = session.query(Avatars.image_path).filter(Avatars.user_id == user_id).first()
        if image_path is None:
            image_path = (0,)

    return render_template("profile.html", title="Профиль пользователя", user=user, image_path=image_path[0], ads=ads)


@app.route("/create_ad", methods=["GET", "POST"])
@login_required
def create_ad():
    '''Обработчик создания объявления'''
    form = AdForm()
    if form.validate_on_submit():
        with db_session.create_session() as session:
            ad = Ads(
                user_id=current_user.id,
                title=form.title.data,
                description=form.description.data,
                price=form.price.data,
                category=int(form.categories.data),
                city=form.city.data
            )

            # загрузка файлов на сервер
            uploaded_file = form.images.data

            if len(uploaded_file) > 5:
                return render_template("create_ad.html", title="Создание объявления", form=form,
                                       message="Можно загрузить не больше 5 изображений")

            session.add(ad)
            session.commit()

            for file in uploaded_file:
                if file:
                    # генерируем уникальное имя
                    filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1].lower()}"
                    # функция, для создания безопасного пути
                    secure_name = secure_filename(filename)
                    filepath = os.path.join(app.config["IMAGE_UPLOAD_FOLDER"], secure_name)
                    # сохраняем в памяти
                    img = Image.open(file)
                    # задаем размер 300x300
                    img.resize((300, 300), Image.LANCZOS)
                    # сохраняем
                    img.save(filepath)
                    image = Images(
                        ad_id=ad.id,
                        image_path=filepath,
                        original_image_path=file.filename
                    )
                    session.add(image)
            session.commit()

        return redirect("/")
    return render_template("create_ad.html", title="Создание объявления", form=form)


@app.route("/edit_ad/<int:ad_id>", methods=["GET", "POST"])
@login_required
def edit_ad(ad_id):
    '''Обработчик изменения объявления'''
    with db_session.create_session() as session:
        # получение текущих фотографий
        images_paths = session.query(Images).filter(Images.ad_id == ad_id).all()

    form = AdForm()

    # добавление их в форму
    form.images_paths = images_paths

    if request.method == "GET":
        with db_session.create_session() as session:
            ad = session.query(Ads).filter(Ads.id == ad_id).first()

        if not ad or current_user.id != ad.user_id:  # проверка на валидность данных
            abort(404)
        # установка в поля формы данных
        form.title.data = ad.title
        form.description.data = ad.description
        form.price.data = ad.price
        form.categories.data = str(ad.category)
        form.city.data = ad.city

    if form.validate_on_submit():
        with db_session.create_session() as session:
            ad = session.query(Ads).filter(Ads.id == ad_id).first()
            if ad:
                # изменение данных
                ad.title = form.title.data
                ad.description = form.description.data
                ad.price = form.price.data
                ad.category = int(form.categories.data)
                ad.city = form.city.data

                # сохранение изменений
                session.add(ad)
                session.commit()

                # загрузка файлов на сервер
                uploaded_file = [file for file in form.images.data if file and file.filename]
                if uploaded_file:
                    if len(uploaded_file) > 5:
                        return render_template("create_ad.html", title="Создание объявления", form=form,
                                               images_paths=images_paths,
                                               message="Можно загрузить не больше 5 изображений")

                    # удаление старых фото
                    for image in images_paths:
                        if os.path.exists(image.image_path):
                            os.remove(image.image_path)
                    session.query(Images).filter(Images.ad_id == ad_id).delete()

                    # загрузка новых фотографий
                    for file in uploaded_file:
                        if file:
                            # генерируем уникальное имя
                            filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1].lower()}"
                            # функция, для создания безопасного пути
                            secure_name = secure_filename(filename)
                            filepath = os.path.join(app.config["IMAGE_UPLOAD_FOLDER"], secure_name)
                            # сохраняем в памяти
                            img = Image.open(file)
                            # задаем размер 300x300
                            img.resize((300, 300), Image.LANCZOS)
                            # сохраняем
                            img.save(filepath)
                            image = Images(
                                ad_id=ad.id,
                                image_path=filepath,
                                original_image_path=file.filename
                            )
                            session.add(image)
                    session.commit()

        return redirect("/")
    return render_template("create_ad.html", title="Изменение объявления", form=form, images_paths=images_paths)


@app.route("/delete_ad/<int:ad_id>", methods=["GET", "POST"])
@login_required
def delete_ad(ad_id):
    '''Обработчик удаления объявления'''
    with db_session.create_session() as session:
        ad = session.query(Ads).filter(Ads.id == ad_id).first()
        images = session.query(Images).filter(Images.ad_id == ad_id).all()

        # выкидываем ошибку 404, если не нашли объявления
        if not ad:
            abort(404)
        else:
            # удаляем фотографии из памяти сервера
            for image in images:
                if os.path.exists(image.image_path):
                    os.remove(image.image_path)
            # удаляем фото и объявление из БД
            session.query(Images).filter(Images.ad_id == ad_id).delete()
            session.delete(ad)

            # сохраняем результат
            session.commit()

    return redirect(f"/profile/{current_user.id}")


@app.route("/ads/<int:ad_id>", methods=["GET"])
def view_ads(ad_id):
    '''Обработчик подробного показа объявления'''
    with db_session.create_session() as session:
        # находим нужную информацию об объявлении в БД
        ad = session.query(Ads).filter(Ads.id == ad_id).first()
        images = session.query(Images).filter(Images.ad_id == ad_id).all()
        seller = session.query(Users).filter(Users.id == ad.user_id).first()
        category = session.query(Categories).filter(Categories.id == ad.category).first()
        reviews = session.query(Reviews) \
            .options(joinedload(Reviews.author)) \
            .filter(Reviews.ad_id == ad.id) \
            .all()

        average = round(sum([review.rating for review in reviews]) / len(reviews))

        user_has_reviewed = False
        if current_user.is_authenticated:
            user_has_reviewed = session.query(Reviews).filter(
                Reviews.ad_id == ad_id,
                Reviews.user_id == current_user.id
            ).first() is not None

    # возвращаем шаблон
    return render_template("product.html", title=f"{ad.title}", images=images, product=ad, seller=seller,
                           category=category, reviews=reviews, user_has_reviewed=user_has_reviewed, average=average)


def save_avatar(file, user_id):
    '''Функция для сохранения аватарки'''
    # генерируем имя
    filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1].lower()}"
    # безопасно сохраняем имя
    secure_name = secure_filename(filename)
    # переходим в папку
    upload_path = os.path.join(app.config['AVATAR_UPLOAD_FOLDER'], secure_name)

    # изменяем размер до 120х120 и сохраняем в /static/avatars/
    img = Image.open(file.stream)
    img = img.convert("RGB")
    img.thumbnail((120, 120), Image.LANCZOS)
    img.save(upload_path, format='JPEG', quality=95)

    with db_session.create_session() as session:
        # удаляем старую аватарку, если она была
        avatar = session.query(Avatars).filter(Avatars.user_id == user_id).first()

        if avatar is not None:
            os.remove(avatar.image_path)
            session.delete(avatar)
        # сохраняем в БД
        avatar = Avatars(
            user_id=user_id,
            image_path=upload_path
        )

        session.add(avatar)
        session.commit()
    return upload_path


@app.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    '''Обработчик сохранения аватарки'''
    if 'file' not in request.files:
        return 'Нет файла', 400

    file = request.files['file']
    if file.filename == '':
        return 'Файл не выбран', 400
    # сохраняем новый аватар
    save_avatar(file, current_user.id)

    return redirect(f"/profile/{current_user.id}")


@app.route("/create_review/<int:ad_id>", methods=["GET", "POST"])
@login_required
def create_review(ad_id):
    '''Обработчик создания отзыва'''
    form = ReviewForm()

    if form.validate_on_submit():
        comment = form.comment.data
        rating = form.rating.data
        with db_session.create_session() as session:
            last_review = session.query(Reviews).filter(Reviews.ad_id == ad_id,
                                                        Reviews.user_id == current_user.id).first()

            if last_review is not None:
                return render_template("create_review.html", title="Создание объявления", form=form,
                                       message="Вы уже оставляли отзыв на этот товар")
            review = Reviews(
                user_id=current_user.id,
                ad_id=ad_id,
                rating=rating,
                comment=comment
            )
            session.add(review)
            session.commit()
            return redirect(f"/ads/{ad_id}")

    return render_template("create_review.html", title="Создание отзыва", form=form)


@app.route("/edit_review/<int:review_id>", methods=["GET", "POST"])
@login_required
def edit_review(review_id):
    form = ReviewForm()

    if request.method == "GET":
        with db_session.create_session() as session:
            review = session.query(Reviews).filter(Reviews.id == review_id).first()

            if review is None:
                abort(404)

            form.comment.data = review.comment
            form.rating.data = int(review.rating)

    if form.validate_on_submit():
        with db_session.create_session() as session:
            review = session.query(Reviews).filter(Reviews.id == review_id).first()
            if review:
                review.comment = form.comment.data
                review.rating = form.rating.data
                session.add(review)
                session.commit()
            return redirect(f"/ads/{review.ad_id}")

    return render_template("create_review.html", title="Изменение отзыва", form=form)


@app.route("/delete_review/<int:review_id>", methods=["GET", "POST"])
def delete_review(review_id):
    '''Обработчик удаления объявления'''
    with db_session.create_session() as session:
        review = session.query(Reviews).filter(Reviews.id == review_id).first()

        if review is None:
            abort(404)
        else:
            ad_id = review.ad_id
            session.delete(review)
            session.commit()

        return redirect(f"/ads/{ad_id}")


if __name__ == '__main__':
    main()

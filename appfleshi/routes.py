from flask import render_template, url_for, redirect, flash, abort, request
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
import os

from appfleshi import app, database, bcrypt
from appfleshi.forms import LoginForm, RegisterForm, PhotoForm
from appfleshi.models import User, Photo, Like


@app.route('/', methods=['GET', 'POST'])
def homepage():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            return redirect(url_for('feed'))
    return render_template('homepage.html', form=login_form)



@app.route('/createaccount', methods=['GET', 'POST'])
def createaccount():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        password = bcrypt.generate_password_hash(register_form.password.data)
        user = User(username=register_form.username.data,
                    password=password,
                    email=register_form.email.data)
        database.session.add(user)
        database.session.commit()
        login_user(user, remember=True)
        return redirect(url_for('profile', user_id=user.id))
    return render_template('createaccount.html', form=register_form)

@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if user_id == current_user.id:
        photo_form = PhotoForm()

        if photo_form.validate_on_submit():
            file = photo_form.photo.data

            filename = secure_filename(file.filename)

            import time
            unique_name = f"{time.time_ns()}_{filename}"

            path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], unique_name)
            file.save(path)

            photo = Photo(
                file_name=unique_name,
                user_id=current_user.id,
                caption=photo_form.caption.data
            )

            database.session.add(photo)
            database.session.commit()

            return redirect(url_for('profile', user_id=current_user.id))

        photos = Photo.query.filter_by(user_id=current_user.id).order_by(Photo.upload_date.desc()).all()

        return render_template(
            "profile.html",
            user=current_user,
            form=photo_form,
            photos=photos
        )

    else:
        user = User.query.get_or_404(user_id)
        photos = Photo.query.filter_by(user_id=user.id).order_by(Photo.upload_date.desc()).all()

        return render_template(
            "profile.html",
            user=user,
            form=None,
            photos=photos
        )

@app.route('/delete/<int:photo_id>', methods=['POST'])
@login_required
def delete(photo_id):
    photo = Photo.query.get(photo_id)

    if photo is None:
        return redirect(url_for("profile", user_id=current_user.id))

    if photo.user_id != current_user.id:
        abort(403)

    file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], photo.file_name)
    if os.path.exists(file_path):
        os.remove(file_path)

    database.session.delete(photo)
    database.session.commit()

    return redirect(url_for("profile", user_id=current_user.id))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))

@app.route('/feed')
@login_required
def feed():
    photos = Photo.query.order_by(Photo.upload_date.desc()).all()
    return render_template("feed.html", photos=photos)

@app.route('/like/<int:photo_id>', methods=['POST'])
@login_required
def like(photo_id):
    photo = Photo.query.filter_by(id=photo_id).first()

    if not photo:
        return redirect(url_for('feed'))

    liked= Like.query.filter_by(user_id=current_user.id, photo_id=photo_id).first()

    if liked:
        database.session.delete(liked)
        database.session.commit()

    else:
        new_like = Like(user_id=current_user.id, photo_id=photo_id)
        database.session.add(new_like)
        database.session.commit()

    return redirect(request.referrer or url_for('feed'))
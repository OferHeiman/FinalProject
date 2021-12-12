import os
from app import app, db, models
from flask import redirect, render_template, url_for, flash
import qrcode
import urllib.request
from PIL import Image
from pyzbar.pyzbar import decode
from passlib.hash import pbkdf2_sha256
from flask_login import login_user, current_user, logout_user
from flask_uploads import configure_uploads, IMAGES, UploadSet
import validators

# Saving photo configuration
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)


# @app.context_processor  # pass variables information to templates
# def inject_constants():
#     scannedqrs = models.ScanQR.query.count()
#     return {'scannedqrs': scannedqrs}


@app.route('/')
def index():
    our_posts = models.ScanQR.query.order_by(models.ScanQR.date_added)
    return render_template('index.html')


# generates qr code
def create_qr(user_data, qr_color, qr_background_color, user_image=''):
    user_data = user_data
    qr_color = qr_color
    qr_background_color = qr_background_color
    user_image = user_image
    filename = str(current_user.get_id()) + 'generatedqr' + str(models.GenerateQR.query.count() + 1) + '.png'
    if user_image:
        image = Image.open(user_image)
        basewidth = 75
        wpercent = (basewidth / float(image.size[0]))
        hsize = int((float(image.size[1]) * float(wpercent)))
        image = image.resize((basewidth, hsize), Image.ANTIALIAS)
        qr = qrcode.QRCode(version=3, error_correction=qrcode.constants.ERROR_CORRECT_H, border=1)
        qr.add_data(user_data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color=qr_color, back_color=qr_background_color).convert('RGB')
        pos = ((qr_image.size[0] - image.size[0]) // 2,
               (qr_image.size[1] - image.size[1]) // 2)
        qr_image.paste(image, pos)
        qr_image.save('app/static/generatedqr/' + filename)
    else:
        qr = qrcode.QRCode(version=3, error_correction=qrcode.constants.ERROR_CORRECT_H, border=1)
        qr.add_data(user_data)
        qr.make()
        qr_image = qr.make_image(fill_color=qr_color, back_color=qr_background_color).convert('RGB')
        qr_image.save('app/static/generatedqr/' + filename)
    return filename


@app.route('/generate', methods=("GET", "POST"))
def generate():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    name = None
    form = models.GenerateQRForm()
    if form.validate_on_submit():  # Check if the form has been filled
        qr_text = form.qr_text.data
        qr_image = form.qr_image.data
        qr_color = form.qr_color.data
        qr_background_color = form.qr_background_color.data
        filename = create_qr(user_data=qr_text, qr_color=qr_color, qr_background_color=qr_background_color,
                             user_image=qr_image)
        if qr_image:
            image = photos.save(qr_image)
            qrgenerate = models.GenerateQR(qr_text=qr_text, qr_image=filename, qr_color=qr_color,
                                           qr_background_color=qr_background_color, user_id=current_user.get_id())
            os.remove('app/static/scannedqr/' + image)
        else:
            qrgenerate = models.GenerateQR(qr_text=qr_text, qr_image=filename, qr_color=qr_color,
                                           qr_background_color=qr_background_color, user_id=current_user.get_id())
        db.session.add(qrgenerate)
        db.session.commit()
        form.qr_text.data = ''
        form.qr_image.data = ''
        form.qr_color.data = 'Black'
        form.qr_background_color.data = 'White'
        return render_template("generate.html", form=form, name=name, qr_text=qr_text, qr_image=filename)
    return render_template("generate.html", form=form, name=name)


@app.route('/scan', methods=("GET", "POST"))
def scan():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    name = None
    form = models.ScanQRForm()
    if form.validate_on_submit():  # Check if the form has been filled
        qr_url = form.qr_url.data
        qr_image = form.qr_image.data
        filename = str(current_user.get_id()) + "user_qr_scan_" + str(models.ScanQR.query.count() + 1) + '.png'
        if qr_url == '' and not qr_image:
            flash("Please input URL or Image")
            return render_template("scan.html", form=form, name=name)
        elif validators.url(form.qr_url.data):
            urllib.request.urlretrieve(qr_url, 'app/static/scannedqr/' + filename)
            value = decode(Image.open('app/static/scannedqr/' + filename))
            try:
                value_decoded = value[0][0].decode("utf-8")
                qrscan = models.ScanQR(qr_url=qr_url, qr_image=filename, qr_value=value_decoded,
                                       user_id=current_user.get_id())
                db.session.add(qrscan)
                db.session.commit()
                form.qr_url.data = ''
                form.qr_image.data = ''
                flash(value_decoded)
                return render_template("scan.html", form=form, name=name, qr_url=qr_url, used_url=True)
            except:
                os.remove('app/static/scannedqr/' + filename)
                return render_template("scan.html", form=form, name=name, qr_image=filename, used_url=False,
                                       not_qr=True)
        else:
            image = photos.save(qr_image, name=filename)
            try:
                value = decode(Image.open('app/static/scannedqr/' + image))
                value_decoded = value[0][0].decode("utf-8")
                qrscan = models.ScanQR(qr_image=image, qr_value=value_decoded, user_id=current_user.get_id())
                db.session.add(qrscan)
                db.session.commit()
                form.qr_url.data = ''
                form.qr_image.data = ''
                flash(value_decoded)
                return render_template("scan.html", form=form, name=name, qr_image=image, used_url=False)
            except:
                os.remove('app/static/scannedqr/' + image)
                return render_template("scan.html", form=form, name=name, qr_image=image, used_url=False, not_qr=True)
    return render_template("scan.html", form=form, name=name)


@app.route('/signup', methods=("GET", "POST"))
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = models.UsersForm()
    if form.validate_on_submit():  # Check if the form has been filled
        username = form.username.data
        email = form.email.data
        password = form.password.data
        hashed_password = pbkdf2_sha256.hash(password)
        user = models.Users(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        form.username.data = ''
        form.email.data = ''
        form.password.data = ''
        form.confirmpassword.data = ''
        flash("You Have Successfully Signed Up!")
        return redirect(url_for('index'))
    return render_template("signup.html", form=form)


@app.route('/login', methods=("GET", "POST"))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = models.LoginForm()
    if form.validate_on_submit():
        user_object = models.Users.query.filter_by(username=form.username.data).first()
        login_user(user_object)
        flash("You Have Successfully Logged in!")
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout', methods=["GET"])
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile', methods=["GET"])
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    user_scans = models.ScanQR.query.filter_by(user_id=current_user.get_id())
    user_generations = models.GenerateQR.query.filter_by(user_id=current_user.get_id())
    num_scanned = models.ScanQR.query.count()
    num_generated = models.GenerateQR.query.count()
    return render_template('profile.html', user_scans=user_scans, user_generations=user_generations,
                           num_scanned=num_scanned, num_generated=num_generated)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

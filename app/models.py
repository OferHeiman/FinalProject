from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators, FileField, SelectField
from wtforms.validators import InputRequired, Email, ValidationError
from passlib.hash import pbkdf2_sha256
from flask_login import UserMixin
from datetime import datetime


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(1024), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name


class UsersForm(FlaskForm):
    username = StringField("Username", [validators.Length(min=4, max=25, message='Username must be between 8-64 characters'),
                                        validators.InputRequired("Username Required")])
    email = StringField("Email",
                        validators=[InputRequired("Email Required"), Email(message='Please input a valid email')])
    password = PasswordField("Password", [validators.InputRequired("Password Required"),
                                          validators.EqualTo('confirmpassword', message="Passwords must match"),
                                          validators.Length(min=8, max=64, message='Password must be between 8-64 characters')])
    confirmpassword = PasswordField('Confirm Password')
    submit = SubmitField("Signup")

    @staticmethod
    def validate_username(self, username):
        user_object = Users.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists")

    @staticmethod
    def validate_email(self, email):
        user_object = Users.query.filter_by(email=email.data).first()
        if user_object:
            raise ValidationError("Email already exists")

    def __repr__(self):
        return '<Name %r>' % self.name


def invalid_credentials(form, field):
    username_entered = form.username.data
    password_entered = field.data
    user_object = Users.query.filter_by(username=username_entered).first()
    if user_object is None:
        raise ValidationError("Username or password is incorrect")
    elif not pbkdf2_sha256.verify(password_entered, user_object.password):
        raise ValidationError("Username or password is incorrect")


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[InputRequired(message="Username required")])
    password = PasswordField('Password',
                           validators=[InputRequired(message="Password required"),
                                       invalid_credentials])
    submit = SubmitField("Login")


class ScanQR(db.Model):
    __tablename__ = 'scanqr'
    id = db.Column(db.Integer, primary_key=True)
    qr_url = db.Column(db.String(1000), default='')
    qr_image = db.Column(db.String(1000), default='')
    qr_value = db.Column(db.String(2000), default='')
    date_added = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Name %r>' % self.name


class ScanQRForm(FlaskForm):
    qr_url = StringField("QR URL:")
    qr_image = FileField("QR Image:")
    submit = SubmitField("Scan QR")

    def __repr__(self):
        return '<Name %r>' % self.name


class GenerateQR(db.Model):
    __tablename__ = 'generateqr'
    id = db.Column(db.Integer, primary_key=True)
    qr_text = db.Column(db.String(1000), nullable=False)
    qr_image = db.Column(db.String(1000), default='')
    qr_color = db.Column(db.String(1000))
    qr_background_color = db.Column(db.String(1000))
    # qr_shape = db.Column(db.String(1000), default='')
    # qr_color_mask = db.Column(db.String(1000), default='')
    date_added = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Name %r>' % self.name


class GenerateQRForm(FlaskForm):
    qr_text = StringField("QR Text:", validators=[InputRequired(message="Text required")])
    qr_image = FileField("QR image:")
    qr_color = SelectField("QR Color:", choices=['Aliceblue', 'Antiquewhite', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque', 'Black', 'Blanchedalmond', 'Blue', 'Blueviolet', 'Brown', 'Burlywood', 'Cadetblue', 'Chartreuse', 'Chocolate', 'Coral', 'Cornflowerblue', 'Cornsilk', 'Crimson', 'Cyan', 'Darkblue', 'Darkcyan', 'Darkgoldenrod', 'Darkgray', 'Darkgreen', 'Darkgrey', 'Darkkhaki', 'Darkmagenta', 'Darkolivegreen', 'Darkorange', 'Darkorchid', 'Darkred', 'Darksalmon', 'Darkseagreen', 'Darkslateblue', 'Darkslategray', 'Darkslategrey', 'Darkturquoise', 'Darkviolet', 'Deeppink', 'Deepskyblue', 'Dimgray', 'Dimgrey', 'Dodgerblue', 'Firebrick', 'Floralwhite', 'Forestgreen', 'Fuchsia', 'Gainsboro', 'Ghostwhite', 'Gold', 'Goldenrod', 'Gray', 'Green', 'Greenyellow', 'Grey', 'Honeydew', 'Hotpink', 'Indianred', 'Indigo', 'Ivory', 'Khaki', 'Lavender', 'Lavenderblush', 'Lawngreen', 'Lemonchiffon', 'Lightblue', 'Lightcoral', 'Lightcyan', 'Lightgoldenrodyellow', 'Lightgray', 'Lightgreen', 'Lightgrey', 'Lightpink', 'Lightsalmon', 'Lightseagreen', 'Lightskyblue', 'Lightslategray', 'Lightslategrey', 'Lightsteelblue', 'Lightyellow', 'Lime', 'Limegreen', 'Linen', 'Magenta', 'Maroon', 'Mediumaquamarine', 'Mediumblue', 'Mediumorchid', 'Mediumpurple', 'Mediumseagreen', 'Mediumslateblue', 'Mediumspringgreen', 'Mediumturquoise', 'Mediumvioletred', 'Midnightblue', 'Mintcream', 'Mistyrose', 'Moccasin', 'Navajowhite', 'Navy', 'Oldlace', 'Olive', 'Olivedrab', 'Orange', 'Orangered', 'Orchid', 'Palegoldenrod', 'Palegreen', 'Paleturquoise', 'Palevioletred', 'Papayawhip', 'Peachpuff', 'Peru', 'Pink', 'Plum', 'Powderblue', 'Purple', 'Rebeccapurple', 'Red', 'Rosybrown', 'Royalblue', 'Saddlebrown', 'Salmon', 'Sandybrown', 'Seagreen', 'Seashell', 'Sienna', 'Silver', 'Skyblue', 'Slateblue', 'Slategray', 'Slategrey', 'Snow', 'Springgreen', 'Steelblue', 'Tan', 'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'Wheat', 'White', 'Whitesmoke', 'Yellow', 'Yellowgreen'], default='Black')
    qr_background_color = SelectField("QR Background Color:", choices=['Aliceblue', 'Antiquewhite', 'Aqua', 'Aquamarine', 'Azure', 'Beige', 'Bisque', 'Black', 'Blanchedalmond', 'Blue', 'Blueviolet', 'Brown', 'Burlywood', 'Cadetblue', 'Chartreuse', 'Chocolate', 'Coral', 'Cornflowerblue', 'Cornsilk', 'Crimson', 'Cyan', 'Darkblue', 'Darkcyan', 'Darkgoldenrod', 'Darkgray', 'Darkgreen', 'Darkgrey', 'Darkkhaki', 'Darkmagenta', 'Darkolivegreen', 'Darkorange', 'Darkorchid', 'Darkred', 'Darksalmon', 'Darkseagreen', 'Darkslateblue', 'Darkslategray', 'Darkslategrey', 'Darkturquoise', 'Darkviolet', 'Deeppink', 'Deepskyblue', 'Dimgray', 'Dimgrey', 'Dodgerblue', 'Firebrick', 'Floralwhite', 'Forestgreen', 'Fuchsia', 'Gainsboro', 'Ghostwhite', 'Gold', 'Goldenrod', 'Gray', 'Green', 'Greenyellow', 'Grey', 'Honeydew', 'Hotpink', 'Indianred', 'Indigo', 'Ivory', 'Khaki', 'Lavender', 'Lavenderblush', 'Lawngreen', 'Lemonchiffon', 'Lightblue', 'Lightcoral', 'Lightcyan', 'Lightgoldenrodyellow', 'Lightgray', 'Lightgreen', 'Lightgrey', 'Lightpink', 'Lightsalmon', 'Lightseagreen', 'Lightskyblue', 'Lightslategray', 'Lightslategrey', 'Lightsteelblue', 'Lightyellow', 'Lime', 'Limegreen', 'Linen', 'Magenta', 'Maroon', 'Mediumaquamarine', 'Mediumblue', 'Mediumorchid', 'Mediumpurple', 'Mediumseagreen', 'Mediumslateblue', 'Mediumspringgreen', 'Mediumturquoise', 'Mediumvioletred', 'Midnightblue', 'Mintcream', 'Mistyrose', 'Moccasin', 'Navajowhite', 'Navy', 'Oldlace', 'Olive', 'Olivedrab', 'Orange', 'Orangered', 'Orchid', 'Palegoldenrod', 'Palegreen', 'Paleturquoise', 'Palevioletred', 'Papayawhip', 'Peachpuff', 'Peru', 'Pink', 'Plum', 'Powderblue', 'Purple', 'Rebeccapurple', 'Red', 'Rosybrown', 'Royalblue', 'Saddlebrown', 'Salmon', 'Sandybrown', 'Seagreen', 'Seashell', 'Sienna', 'Silver', 'Skyblue', 'Slateblue', 'Slategray', 'Slategrey', 'Snow', 'Springgreen', 'Steelblue', 'Tan', 'Teal', 'Thistle', 'Tomato', 'Turquoise', 'Violet', 'Wheat', 'White', 'Whitesmoke', 'Yellow', 'Yellowgreen'], default='White')
    # qr_shape = SelectField("QR Shape:", choices=['Square', 'Rounded', 'Circle', 'Gapped Square', 'Horizontal Bars', 'Vertical Bars'])
    # qr_color_mask = SelectField("QR Color Mask:", choices=['Radial Gradiant', 'Horizontal Gradiant'])
    submit = SubmitField("Generate QR")

    def __repr__(self):
        return '<Name %r>' % self.name


# delete from users where X

from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length
from . import authenticate

class LoginForm(Form):
    username = StringField('Username', [DataRequired(), Length(max=255)])
    password = PasswordField('Password', [DataRequired()])
    remember = BooleanField('Remember Me')

    def validate(self):
        check_validate = super(LoginForm, self).validate()

        if not check_validate:
            return False
        
        if not authenticate(self.username.data, self.password.data):
            self.username.errors.append('Invalid username or password')
            return False
        return True
    

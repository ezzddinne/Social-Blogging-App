from flask import (render_template, Blueprint)
from . import oid

auth_blueprint = Blueprint('auth',
                            __name__,
                            template_folder='../templates/auth',
                            url_prefix='/auth')



from flask import Blueprint

interview = Blueprint('interview', __name__)

from app.interview import routes

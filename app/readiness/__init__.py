from flask import Blueprint

readiness = Blueprint('readiness', __name__)

from app.readiness import routes

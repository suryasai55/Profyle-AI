from flask import Blueprint

skill_gap = Blueprint('skill_gap', __name__)

from app.skill_gap import routes

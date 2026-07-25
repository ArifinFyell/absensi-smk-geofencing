from flask import Blueprint
from app.controllers import api_controller

api_bp = Blueprint('api', __name__, url_prefix='/api')

api_bp.route('/stats')(api_controller.get_realtime_stats)
api_bp.route('/search')(api_controller.global_search)
api_bp.route('/schedule/current')(api_controller.get_current_schedule)

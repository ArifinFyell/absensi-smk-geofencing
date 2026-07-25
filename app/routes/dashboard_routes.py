from flask import Blueprint
from app.controllers import dashboard_controller
from app.middleware.auth_middleware import login_required

dashboard_bp = Blueprint('dashboard', __name__)

dashboard_bp.route('/', endpoint='index')(login_required(dashboard_controller.index_view))
dashboard_bp.route('/dashboard', endpoint='dashboard_page')(login_required(dashboard_controller.index_view))
dashboard_bp.route('/monitoring', endpoint='monitoring_view')(login_required(dashboard_controller.monitoring_view))
dashboard_bp.route('/absensi/detail/<int:absensi_id>', endpoint='detail_absensi_view')(login_required(dashboard_controller.detail_absensi_view))

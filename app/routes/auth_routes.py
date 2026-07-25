from flask import Blueprint
from app.controllers import auth_controller

auth_bp = Blueprint('auth', __name__)

auth_bp.route('/login', methods=['GET', 'POST'], endpoint='login')(auth_controller.login_view)
auth_bp.route('/login_view', methods=['GET', 'POST'], endpoint='login_view')(auth_controller.login_view)
auth_bp.route('/logout', endpoint='logout')(auth_controller.logout_action)
auth_bp.route('/logout_action', endpoint='logout_action')(auth_controller.logout_action)
auth_bp.route('/change-password', methods=['POST'], endpoint='change_password')(auth_controller.change_password_action)

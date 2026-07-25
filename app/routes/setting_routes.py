from flask import Blueprint
from app.controllers import setting_controller
from app.middleware.auth_middleware import admin_required

setting_bp = Blueprint('pengaturan', __name__, url_prefix='/pengaturan')

setting_bp.route('', endpoint='index')(admin_required(setting_controller.index_view))
setting_bp.route('/list', endpoint='index_view')(admin_required(setting_controller.index_view))
setting_bp.route('/geofence', methods=['POST'], endpoint='update_geofence_action')(admin_required(setting_controller.update_geofence_action))
setting_bp.route('/jam', methods=['POST'], endpoint='update_jam_action')(admin_required(setting_controller.update_jam_action))
setting_bp.route('/sekolah', methods=['POST'], endpoint='update_sekolah_action')(admin_required(setting_controller.update_sekolah_action))
setting_bp.route('/backup', endpoint='backup_db_action')(admin_required(setting_controller.backup_db_action))

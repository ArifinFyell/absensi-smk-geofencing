from flask import Blueprint
from app.controllers import jadwal_controller
from app.middleware.auth_middleware import login_required

jadwal_bp = Blueprint('jadwal', __name__, url_prefix='/jadwal')

jadwal_bp.route('', endpoint='index')(login_required(jadwal_controller.index_view))
jadwal_bp.route('/list', endpoint='index_view')(login_required(jadwal_controller.index_view))
jadwal_bp.route('/tambah', methods=['POST'], endpoint='add_action')(login_required(jadwal_controller.add_action))
jadwal_bp.route('/edit/<int:jadwal_id>', methods=['POST'], endpoint='edit_action')(login_required(jadwal_controller.edit_action))
jadwal_bp.route('/hapus/<int:jadwal_id>', methods=['POST'], endpoint='delete_action')(login_required(jadwal_controller.delete_action))

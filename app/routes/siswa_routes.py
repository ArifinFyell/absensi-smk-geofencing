from flask import Blueprint
from app.controllers import siswa_controller
from app.middleware.auth_middleware import login_required

siswa_bp = Blueprint('siswa', __name__, url_prefix='/siswa')

siswa_bp.route('', endpoint='index')(login_required(siswa_controller.index_view))
siswa_bp.route('/list', endpoint='index_view')(login_required(siswa_controller.index_view))
siswa_bp.route('/tambah', methods=['POST'], endpoint='add_action')(login_required(siswa_controller.add_action))
siswa_bp.route('/edit/<int:siswa_id>', methods=['POST'], endpoint='edit_action')(login_required(siswa_controller.edit_action))
siswa_bp.route('/hapus/<int:siswa_id>', methods=['POST'], endpoint='delete_action')(login_required(siswa_controller.delete_action))
siswa_bp.route('/detail/<int:siswa_id>', endpoint='detail_view')(login_required(siswa_controller.detail_view))
siswa_bp.route('/export/excel', endpoint='export_excel')(login_required(siswa_controller.export_excel))

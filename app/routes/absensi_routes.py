from flask import Blueprint
from app.controllers import absensi_controller
from app.middleware.auth_middleware import login_required

absensi_bp = Blueprint('absensi', __name__, url_prefix='/absensi-siswa')

# Public student attendance portal - NO LOGIN REQUIRED for students
absensi_bp.route('', methods=['GET'], endpoint='index')(absensi_controller.student_portal_view)
absensi_bp.route('/portal', methods=['GET'], endpoint='student_portal_view')(absensi_controller.student_portal_view)
absensi_bp.route('/submit', methods=['POST'], endpoint='submit_absensi_action')(absensi_controller.submit_absensi_action)
absensi_bp.route('/api/get-jadwal-by-kelas', methods=['GET'], endpoint='get_jadwal_by_kelas')(absensi_controller.get_jadwal_by_kelas_api)
absensi_bp.route('/riwayat', endpoint='riwayat_view')(login_required(absensi_controller.riwayat_view))

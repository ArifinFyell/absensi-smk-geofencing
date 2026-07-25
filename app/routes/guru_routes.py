from flask import Blueprint
from app.controllers import guru_controller
from app.middleware.auth_middleware import guru_required

guru_bp = Blueprint('guru', __name__, url_prefix='/guru')

guru_bp.route('/dashboard', endpoint='dashboard')(guru_required(guru_controller.dashboard_view))
guru_bp.route('/jadwal', endpoint='jadwal')(guru_required(guru_controller.jadwal_view))
guru_bp.route('/absensi', endpoint='absensi')(guru_required(guru_controller.absensi_view))
guru_bp.route('/absensi/simpan', methods=['POST'], endpoint='simpan_absensi')(guru_required(guru_controller.simpan_absensi_action))
guru_bp.route('/rekap', endpoint='rekap')(guru_required(guru_controller.rekap_view))
guru_bp.route('/profil', endpoint='profil')(guru_required(guru_controller.profil_view))

# Verifikasi Email
guru_bp.route('/verify-email', endpoint='verify_email')(guru_required(guru_controller.verify_email_view))
guru_bp.route('/request-verification', methods=['POST'], endpoint='request_verification')(guru_required(guru_controller.request_verification_action))
guru_bp.route('/verify/<token>', endpoint='process_verification')(guru_required(guru_controller.process_verification_action))
guru_bp.route('/set-verified-password', methods=['POST'], endpoint='set_verified_password')(guru_required(guru_controller.set_verified_password_action))

# Manajemen Hari Libur
guru_bp.route('/jadwal/libur/tambah', methods=['POST'], endpoint='tambah_libur')(guru_required(guru_controller.tambah_libur_action))
guru_bp.route('/jadwal/libur/hapus/<int:libur_id>', methods=['POST'], endpoint='hapus_libur')(guru_required(guru_controller.hapus_libur_action))

# Monitoring Wali Kelas
guru_bp.route('/wali-kelas/absensi', endpoint='wali_kelas_absensi')(guru_required(guru_controller.absensi_wali_kelas_view))


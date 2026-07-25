from flask import Blueprint
from app.controllers import laporan_controller
from app.middleware.auth_middleware import login_required

laporan_bp = Blueprint('laporan', __name__, url_prefix='/laporan')

laporan_bp.route('', endpoint='index')(login_required(laporan_controller.index_view))
laporan_bp.route('/list', endpoint='index_view')(login_required(laporan_controller.index_view))
laporan_bp.route('/excel', endpoint='export_excel_laporan')(login_required(laporan_controller.export_excel_laporan))
laporan_bp.route('/print', endpoint='print_pdf_laporan')(login_required(laporan_controller.print_pdf_laporan))

from datetime import datetime, date
from flask import render_template, request, send_file
from app.models import db, Absensi, Kelas, Jurusan, Guru, SettingSekolah
from app.helpers.export_helper import generate_excel_absensi

def index_view():
    start_date = request.args.get('start_date', date.today().strftime('%Y-%m-01'))
    end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
    kelas_id = request.args.get('kelas_id')
    jurusan_id = request.args.get('jurusan_id')
    status_filter = request.args.get('status')

    query = Absensi.query

    if start_date:
        query = query.filter(Absensi.tanggal >= start_date)
    if end_date:
        query = query.filter(Absensi.tanggal <= end_date)
    if status_filter:
        query = query.filter(Absensi.status == status_filter)

    absensi_list = query.order_by(Absensi.tanggal.desc(), Absensi.id.desc()).all()

    if kelas_id:
        absensi_list = [a for a in absensi_list if a.siswa_rel and str(a.siswa_rel.kelas_id) == str(kelas_id)]
    if jurusan_id:
        absensi_list = [a for a in absensi_list if a.siswa_rel and str(a.siswa_rel.jurusan_id) == str(jurusan_id)]

    kelas_list = Kelas.query.all()
    jurusan_list = Jurusan.query.all()
    sekolah = SettingSekolah.query.first()

    return render_template('laporan/index.html',
                           absensi_list=absensi_list,
                           kelas_list=kelas_list,
                           jurusan_list=jurusan_list,
                           start_date=start_date,
                           end_date=end_date,
                           selected_kelas=kelas_id,
                           selected_jurusan=jurusan_id,
                           selected_status=status_filter,
                           sekolah=sekolah)

def export_excel_laporan():
    start_date = request.args.get('start_date', date.today().strftime('%Y-%m-01'))
    end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
    status_filter = request.args.get('status')

    query = Absensi.query.filter(Absensi.tanggal >= start_date, Absensi.tanggal <= end_date)
    if status_filter:
        query = query.filter(Absensi.status == status_filter)

    absensi_list = query.order_by(Absensi.tanggal.asc(), Absensi.id.asc()).all()

    title_str = f"LAPORAN REKAPITULASI ABSENSI ({start_date} s/d {end_date})"
    excel_stream = generate_excel_absensi(absensi_list, title=title_str)

    filename = f"Laporan_Absensi_SMKN1_{start_date}_sd_{end_date}.xlsx"

    return send_file(
        excel_stream,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def print_pdf_laporan():
    start_date = request.args.get('start_date', date.today().strftime('%Y-%m-01'))
    end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
    status_filter = request.args.get('status')

    query = Absensi.query.filter(Absensi.tanggal >= start_date, Absensi.tanggal <= end_date)
    if status_filter:
        query = query.filter(Absensi.status == status_filter)

    absensi_list = query.order_by(Absensi.tanggal.asc(), Absensi.id.asc()).all()
    sekolah = SettingSekolah.query.first()
    guru_head = Guru.query.first()

    return render_template('laporan/print_view.html',
                           absensi_list=absensi_list,
                           start_date=start_date,
                           end_date=end_date,
                           sekolah=sekolah,
                           guru_head=guru_head,
                           cetak_tanggal=date.today().strftime('%d %B %Y'))

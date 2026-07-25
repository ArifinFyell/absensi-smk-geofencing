import io
import openpyxl
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from app.models import db, Siswa, Kelas, Jurusan, Absensi, ActivityLog
from app.helpers.export_helper import generate_excel_absensi

def index_view():
    kelas_id = request.args.get('kelas_id')
    jurusan_id = request.args.get('jurusan_id')
    search_query = request.args.get('q', '').strip()

    query = Siswa.query

    if kelas_id:
        query = query.filter_by(kelas_id=kelas_id)
    if jurusan_id:
        query = query.filter_by(jurusan_id=jurusan_id)
    if search_query:
        query = query.filter((Siswa.nama.ilike(f'%{search_query}%')) | (Siswa.nis.ilike(f'%{search_query}%')))

    siswa_list = query.order_by(Siswa.nis.asc()).all()
    kelas_list = Kelas.query.all()
    jurusan_list = Jurusan.query.all()

    return render_template('siswa/index.html',
                           siswa_list=siswa_list,
                           kelas_list=kelas_list,
                           jurusan_list=jurusan_list,
                           search_query=search_query,
                           selected_kelas=kelas_id,
                           selected_jurusan=jurusan_id)

def add_action():
    if request.method == 'POST':
        nis = request.form.get('nis', '').strip()
        nama = request.form.get('nama', '').strip()
        kelas_id = request.form.get('kelas_id')
        jurusan_id = request.form.get('jurusan_id')
        jenis_kelamin = request.form.get('jenis_kelamin', 'Laki-Laki')
        alamat = request.form.get('alamat', '').strip()
        no_hp = request.form.get('no_hp', '').strip()

        if not nis or not nama or not kelas_id or not jurusan_id:
            flash('Harap lengkapi seluruh kolom wajib (NIS, Nama, Kelas, Jurusan).', 'danger')
            return redirect(url_for('siswa.index'))

        existing = Siswa.query.filter_by(nis=nis).first()
        if existing:
            flash(f'Siswa dengan NIS {nis} sudah terdaftar.', 'warning')
            return redirect(url_for('siswa.index'))

        new_siswa = Siswa(
            nis=nis,
            nama=nama,
            kelas_id=kelas_id,
            jurusan_id=jurusan_id,
            jenis_kelamin=jenis_kelamin,
            alamat=alamat,
            no_hp=no_hp,
            status='Aktif'
        )
        db.session.add(new_siswa)
        db.session.add(ActivityLog(user=request.args.get('user', 'Admin'), aktivitas=f"Menambahkan data siswa baru: {nama} ({nis})"))
        db.session.commit()

        flash(f'Siswa {nama} berhasil ditambahkan!', 'success')
        return redirect(url_for('siswa.index'))

def edit_action(siswa_id):
    siswa = Siswa.query.get_or_404(siswa_id)
    if request.method == 'POST':
        siswa.nis = request.form.get('nis', siswa.nis).strip()
        siswa.nama = request.form.get('nama', siswa.nama).strip()
        siswa.kelas_id = request.form.get('kelas_id', siswa.kelas_id)
        siswa.jurusan_id = request.form.get('jurusan_id', siswa.jurusan_id)
        siswa.jenis_kelamin = request.form.get('jenis_kelamin', siswa.jenis_kelamin)
        siswa.alamat = request.form.get('alamat', siswa.alamat).strip()
        siswa.no_hp = request.form.get('no_hp', siswa.no_hp).strip()
        siswa.status = request.form.get('status', siswa.status)

        db.session.add(ActivityLog(user='Admin', aktivitas=f"Memperbarui data siswa: {siswa.nama} ({siswa.nis})"))
        db.session.commit()

        flash(f'Data siswa {siswa.nama} berhasil diperbarui.', 'success')
        return redirect(url_for('siswa.index'))

def delete_action(siswa_id):
    siswa = Siswa.query.get_or_404(siswa_id)
    nama = siswa.nama
    nis = siswa.nis
    db.session.delete(siswa)
    db.session.add(ActivityLog(user='Admin', aktivitas=f"Menghapus data siswa: {nama} ({nis})"))
    db.session.commit()

    flash(f'Siswa {nama} ({nis}) berhasil dihapus.', 'info')
    return redirect(url_for('siswa.index'))

def detail_view(siswa_id):
    siswa = Siswa.query.get_or_404(siswa_id)
    absensi_history = Absensi.query.filter_by(siswa_id=siswa.id).order_by(Absensi.tanggal.desc(), Absensi.id.desc()).all()

    total_absen = len(absensi_history)
    hadir_count = sum(1 for a in absensi_history if a.status == 'Hadir')
    terlambat_count = sum(1 for a in absensi_history if a.status in ['Terlambat', 'Terlambat Berat'])
    izin_count = sum(1 for a in absensi_history if a.status == 'Izin')
    sakit_count = sum(1 for a in absensi_history if a.status == 'Sakit')

    persentase = round((hadir_count + terlambat_count) / total_absen * 100, 1) if total_absen > 0 else 100.0

    return render_template('siswa/detail.html',
                           siswa=siswa,
                           absensi_history=absensi_history,
                           total_absen=total_absen,
                           hadir_count=hadir_count,
                           terlambat_count=terlambat_count,
                           izin_count=izin_count,
                           sakit_count=sakit_count,
                           persentase=persentase)

def export_excel():
    siswa_list = Siswa.query.order_by(Siswa.nis.asc()).all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Master Data Siswa"

    ws.append(["No", "NIS", "Nama Lengkap", "Kelas", "Jurusan", "Jenis Kelamin", "No HP", "Status"])
    for idx, s in enumerate(siswa_list, start=1):
        ws.append([
            idx,
            s.nis,
            s.nama,
            s.kelas_rel.nama_kelas if s.kelas_rel else '-',
            s.jurusan_rel.kode if s.jurusan_rel else '-',
            s.jenis_kelamin,
            s.no_hp or '-',
            s.status
        ])

    stream = openpyxl.writer.excel.save_virtual_workbook(wb)
    return send_file(
        io.BytesIO(stream),
        as_attachment=True,
        download_name="Master_Data_Siswa_SMKN1_Bangkinang.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

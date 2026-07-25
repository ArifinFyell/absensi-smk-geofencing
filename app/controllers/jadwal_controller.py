from flask import render_template, request, redirect, url_for, flash
from app.models import db, Jadwal, Guru, Kelas, ActivityLog

HARI_ORDER = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat']

def index_view():
    selected_hari = request.args.get('hari', 'Senin')
    
    jadwal_by_hari = {}
    for h in HARI_ORDER:
        jadwal_by_hari[h] = Jadwal.query.filter_by(hari=h).order_by(Jadwal.jam_mulai.asc()).all()

    guru_list = Guru.query.filter_by(status='Aktif').all()
    kelas_list = Kelas.query.all()

    return render_template('jadwal/index.html',
                           jadwal_by_hari=jadwal_by_hari,
                           hari_order=HARI_ORDER,
                           selected_hari=selected_hari,
                           guru_list=guru_list,
                           kelas_list=kelas_list)

def add_action():
    if request.method == 'POST':
        hari = request.form.get('hari')
        jam_mulai = request.form.get('jam_mulai')
        jam_selesai = request.form.get('jam_selesai')
        mata_pelajaran = request.form.get('mata_pelajaran', '').strip()
        guru_id = request.form.get('guru_id') or None
        kelas_id = request.form.get('kelas_id')

        if not hari or not jam_mulai or not jam_selesai or not mata_pelajaran or not kelas_id:
            flash('Harap lengkapi seluruh kolom formulir jadwal.', 'danger')
            return redirect(url_for('jadwal.index'))

        new_j = Jadwal(
            hari=hari,
            jam_mulai=jam_mulai,
            jam_selesai=jam_selesai,
            mata_pelajaran=mata_pelajaran,
            guru_id=int(guru_id) if guru_id else None,
            kelas_id=int(kelas_id)
        )
        db.session.add(new_j)
        db.session.add(ActivityLog(user='Admin', aktivitas=f"Menambahkan jadwal pelajaran {mata_pelajaran} ({hari} {jam_mulai}-{jam_selesai})"))
        db.session.commit()

        flash(f'Jadwal pelajaran {mata_pelajaran} berhasil ditambahkan!', 'success')
        return redirect(url_for('jadwal.index', hari=hari))

def edit_action(jadwal_id):
    j = Jadwal.query.get_or_404(jadwal_id)
    if request.method == 'POST':
        j.hari = request.form.get('hari', j.hari)
        j.jam_mulai = request.form.get('jam_mulai', j.jam_mulai)
        j.jam_selesai = request.form.get('jam_selesai', j.jam_selesai)
        j.mata_pelajaran = request.form.get('mata_pelajaran', j.mata_pelajaran).strip()
        gid = request.form.get('guru_id')
        j.guru_id = int(gid) if gid else None
        j.kelas_id = request.form.get('kelas_id', j.kelas_id)

        db.session.add(ActivityLog(user='Admin', aktivitas=f"Memperbarui jadwal: {j.mata_pelajaran}"))
        db.session.commit()

        flash('Jadwal pelajaran berhasil diperbarui.', 'success')
        return redirect(url_for('jadwal.index', hari=j.hari))

def delete_action(jadwal_id):
    j = Jadwal.query.get_or_404(jadwal_id)
    mapel = j.mata_pelajaran
    hari = j.hari
    db.session.delete(j)
    db.session.add(ActivityLog(user='Admin', aktivitas=f"Menghapus jadwal pelajaran {mapel} ({hari})"))
    db.session.commit()

    flash(f'Jadwal {mapel} berhasil dihapus.', 'info')
    return redirect(url_for('jadwal.index', hari=hari))

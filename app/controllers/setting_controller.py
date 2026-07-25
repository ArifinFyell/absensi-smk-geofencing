import os
import shutil
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, current_app, send_file
from app.models import db, SettingGeofence, SettingJam, SettingSekolah, ActivityLog

def index_view():
    geofence = SettingGeofence.query.first()
    if not geofence:
        geofence = SettingGeofence(latitude=0.334612, longitude=101.026415, radius=100)
        db.session.add(geofence)
        db.session.commit()

    jam_setting = SettingJam.query.first()
    if not jam_setting:
        jam_setting = SettingJam(jam_hadir_mulai='06:45', jam_hadir_selesai='07:15', jam_terlambat_selesai='07:30', jam_tutup='17:00')
        db.session.add(jam_setting)
        db.session.commit()

    sekolah_setting = SettingSekolah.query.first()
    if not sekolah_setting:
        sekolah_setting = SettingSekolah(
            nama_sekolah='SMKN 1 BANGKINANG',
            alamat_sekolah='Jl. Tuanku Tambusai No. 1, Bangkinang, Kampar, Riau',
            logo='logo_smkn1.png',
            tahun_ajaran='2025/2026',
            semester='Ganjil'
        )
        db.session.add(sekolah_setting)
        db.session.commit()

    return render_template('pengaturan/index.html',
                           geofence=geofence,
                           jam_setting=jam_setting,
                           sekolah_setting=sekolah_setting)

def update_geofence_action():
    geofence = SettingGeofence.query.first()
    if not geofence:
        geofence = SettingGeofence()
        db.session.add(geofence)

    lat = request.form.get('latitude', type=float)
    lon = request.form.get('longitude', type=float)
    radius = request.form.get('radius', type=int)

    if lat is not None and lon is not None and radius is not None:
        geofence.latitude = lat
        geofence.longitude = lon
        geofence.radius = radius

        db.session.add(ActivityLog(user='Admin', aktivitas=f"Mengubah koordinat geofence ke ({lat}, {lon}) dengan radius {radius}m."))
        db.session.commit()

        flash('Pengaturan koordinat dan radius Geofence sekolah berhasil diperbarui.', 'success')
    else:
        flash('Data geofence tidak valid.', 'danger')

    return redirect(url_for('pengaturan.index'))

def update_jam_action():
    jam_setting = SettingJam.query.first()
    if not jam_setting:
        jam_setting = SettingJam()
        db.session.add(jam_setting)

    jam_setting.jam_hadir_mulai = request.form.get('jam_hadir_mulai', jam_setting.jam_hadir_mulai)
    jam_setting.jam_hadir_selesai = request.form.get('jam_hadir_selesai', jam_setting.jam_hadir_selesai)
    jam_setting.jam_terlambat_selesai = request.form.get('jam_terlambat_selesai', jam_setting.jam_terlambat_selesai)
    jam_setting.jam_tutup = request.form.get('jam_tutup', jam_setting.jam_tutup)

    db.session.add(ActivityLog(user='Admin', aktivitas="Memperbarui jam absensi sekolah."))
    db.session.commit()

    flash('Pengaturan jam absensi sekolah berhasil disimpan.', 'success')
    return redirect(url_for('pengaturan.index'))

def update_sekolah_action():
    sekolah = SettingSekolah.query.first()
    if not sekolah:
        sekolah = SettingSekolah()
        db.session.add(sekolah)

    sekolah.nama_sekolah = request.form.get('nama_sekolah', sekolah.nama_sekolah)
    sekolah.alamat_sekolah = request.form.get('alamat_sekolah', sekolah.alamat_sekolah)
    sekolah.tahun_ajaran = request.form.get('tahun_ajaran', sekolah.tahun_ajaran)
    sekolah.semester = request.form.get('semester', sekolah.semester)

    db.session.add(ActivityLog(user='Admin', aktivitas="Memperbarui identitas dan profil sekolah."))
    db.session.commit()

    flash('Pengaturan profil sekolah berhasil disimpan.', 'success')
    return redirect(url_for('pengaturan.index'))

def backup_db_action():
    try:
        db_file = os.path.join(current_app.config['BASE_DIR'], 'database', 'app.db')
        if os.path.exists(db_file):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"backup_absensi_smkn1_{timestamp}.db"
            backup_path = os.path.join(current_app.config['BASE_DIR'], 'database', backup_filename)
            shutil.copy2(db_file, backup_path)
            
            db.session.add(ActivityLog(user='Admin', aktivitas=f"Melakukan backup database: {backup_filename}"))
            db.session.commit()

            return send_file(backup_path, as_attachment=True, download_name=backup_filename)
        else:
            flash('File database tidak ditemukan.', 'danger')
            return redirect(url_for('pengaturan.index'))
    except Exception as e:
        flash(f'Gagal melakukan backup database: {str(e)}', 'danger')
        return redirect(url_for('pengaturan.index'))

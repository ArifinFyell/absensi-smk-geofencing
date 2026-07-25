import os
import uuid
from datetime import datetime, date
from flask import render_template, request, jsonify, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.models import db, Siswa, Kelas, Jurusan, Jadwal, Absensi, SettingGeofence, SettingJam, SettingSekolah, ActivityLog, Notification
from app.helpers.geofence import is_within_radius
from app.helpers.time_helper import get_current_hari, get_current_time_str, calculate_attendance_status

def student_portal_view():
    geofence = SettingGeofence.query.first()
    jam_setting = SettingJam.query.first()
    sekolah = SettingSekolah.query.first()
    
    hari_ini = get_current_hari()
    jam_sekarang = get_current_time_str()

    # Read current active schedule
    # Find matching schedule for current day and current time
    active_jadwal = Jadwal.query.filter(
        Jadwal.hari == hari_ini,
        Jadwal.jam_mulai <= jam_sekarang,
        Jadwal.jam_selesai >= jam_sekarang
    ).first()

    # Fallback to first schedule of current day if outside exact hour slot, or general default
    if not active_jadwal:
        active_jadwal = Jadwal.query.filter_by(hari=hari_ini).first()
    if not active_jadwal:
        active_jadwal = Jadwal.query.first()

    kelas_list = Kelas.query.all()
    jurusan_list = Jurusan.query.all()

    return render_template('absensi/index.html',
                           geofence=geofence,
                           jam_setting=jam_setting,
                           sekolah=sekolah,
                           hari_ini=hari_ini,
                           jam_sekarang=jam_sekarang,
                           active_jadwal=active_jadwal,
                           kelas_list=kelas_list,
                           jurusan_list=jurusan_list)

def submit_absensi_action():
    try:
        nama = request.form.get('nama', '').strip()
        nis = request.form.get('nis', '').strip()
        kelas_id = request.form.get('kelas_id')
        jurusan_id = request.form.get('jurusan_id')
        lat_user = request.form.get('latitude', type=float)
        lon_user = request.form.get('longitude', type=float)
        foto_file = request.files.get('foto')

        if not nama or not kelas_id or not jurusan_id:
            return jsonify({'success': False, 'message': 'Harap isi Nama, Kelas, dan Jurusan dengan lengkap.'}), 400

        if not foto_file:
            return jsonify({'success': False, 'message': 'Foto bukti absensi wajib diunggah/diambil.'}), 400

        # 1. Geofence Validation
        geofence = SettingGeofence.query.first()
        if not geofence:
            geofence_lat, geofence_lon, radius_max = 0.334612, 101.026415, 100
        else:
            geofence_lat, geofence_lon, radius_max = geofence.latitude, geofence.longitude, geofence.radius

        if lat_user is None or lon_user is None:
            return jsonify({'success': False, 'message': 'Akses GPS lokasi diperlukan untuk melakukan absensi.'}), 400

        is_valid_loc, distance_m = is_within_radius(lat_user, lon_user, geofence_lat, geofence_lon, radius_max)
        if not is_valid_loc:
            return jsonify({
                'success': False,
                'message': f'Anda berada di luar area sekolah ({round(distance_m, 1)}m dari sekolah, maksimal {radius_max}m). Absensi gagal.'
            }), 400

        # 2. Master Data Siswa Matching
        # Match by name or NIS
        query_siswa = Siswa.query.filter_by(kelas_id=kelas_id, jurusan_id=jurusan_id, status='Aktif')
        if nis:
            siswa = query_siswa.filter_by(nis=nis).first()
        else:
            siswa = query_siswa.filter(Siswa.nama.ilike(f'%{nama}%')).first()

        if not siswa:
            return jsonify({'success': False, 'message': 'Data siswa tidak ditemukan atau tidak cocok dengan data sekolah.'}), 404

        # Check duplicate attendance for today on same schedule
        today = date.today()
        hari_ini = get_current_hari()
        jam_sekarang = get_current_time_str()

        active_jadwal = Jadwal.query.filter(
            Jadwal.hari == hari_ini,
            Jadwal.jam_mulai <= jam_sekarang,
            Jadwal.jam_selesai >= jam_sekarang
        ).first()

        if not active_jadwal:
            active_jadwal = Jadwal.query.filter_by(hari=hari_ini).first()

        existing_abs = Absensi.query.filter_by(
            siswa_id=siswa.id,
            tanggal=today
        ).first()

        if existing_abs:
            return jsonify({
                'success': False,
                'message': f'Siswa {siswa.nama} sudah melakukan absensi hari ini pada pukul {existing_abs.jam_masuk}.'
            }), 400

        # 3. Save Uploaded Photo
        now = datetime.now()
        year_str = now.strftime('%Y')
        month_str = now.strftime('%m')
        day_str = now.strftime('%d')

        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'absensi', year_str, month_str, day_str)
        os.makedirs(upload_dir, exist_ok=True)

        ext = foto_file.filename.rsplit('.', 1)[-1].lower() if '.' in foto_file.filename else 'jpg'
        filename_unique = f"{siswa.nis}_{uuid.uuid4().hex[:8]}.{ext}"
        filepath = os.path.join(upload_dir, filename_unique)
        foto_file.save(filepath)

        rel_photo_path = f"absensi/{year_str}/{month_str}/{day_str}/{filename_unique}"

        # 4. Status calculation
        status_kehadiran = calculate_attendance_status(jam_sekarang)

        # 5. User-agent & Device info
        user_agent_str = request.headers.get('User-Agent', '')
        device_type = 'Mobile' if ('Android' in user_agent_str or 'iPhone' in user_agent_str) else 'Desktop'

        # 6. Save Record
        absensi_rec = Absensi(
            siswa_id=siswa.id,
            jadwal_id=active_jadwal.id if active_jadwal else None,
            tanggal=today,
            jam_masuk=datetime.now().strftime('%H:%M:%S'),
            latitude=lat_user,
            longitude=lon_user,
            jarak=distance_m,
            foto=rel_photo_path,
            status=status_kehadiran,
            device=device_type,
            ip_address=request.remote_addr,
            browser=user_agent_str[:80]
        )
        db.session.add(absensi_rec)

        # Log & Notification
        db.session.add(ActivityLog(user=siswa.nama, aktivitas=f"Berhasil absen ({status_kehadiran}) pada mapel {active_jadwal.mata_pelajaran if active_jadwal else 'Umum'}."))
        db.session.add(Notification(
            judul="Absensi Siswa Masuk",
            pesan=f"{siswa.nama} ({siswa.kelas_rel.nama_kelas if siswa.kelas_rel else ''}) berhasil melakukan absensi [{status_kehadiran}].",
            tipe="success" if status_kehadiran == 'Hadir' else "warning"
        ))
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Absensi berhasil tersimpan!',
            'data': {
                'nama': siswa.nama,
                'nis': siswa.nis,
                'jam_masuk': absensi_rec.jam_masuk,
                'status': status_kehadiran,
                'jarak': round(distance_m, 1)
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Terjadi kesalahan server: {str(e)}'}), 500

def riwayat_view():
    absensi_list = Absensi.query.order_by(Absensi.tanggal.desc(), Absensi.id.desc()).limit(100).all()
    return render_template('absensi/riwayat.html', absensi_list=absensi_list)

def get_jadwal_by_kelas_api():
    kelas_id = request.args.get('kelas_id', type=int)
    if not kelas_id:
        return jsonify({'success': False, 'message': 'kelas_id diperlukan'}), 400

    kelas = Kelas.query.get(kelas_id)
    kelas_nama = kelas.nama_kelas if kelas else '-'

    hari_ini = get_current_hari()
    jam_sekarang = get_current_time_str()

    # 1. Cari jadwal tepat pada jam & hari ini untuk kelas terpilih
    jadwal = Jadwal.query.filter(
        Jadwal.kelas_id == kelas_id,
        Jadwal.hari == hari_ini,
        Jadwal.jam_mulai <= jam_sekarang,
        Jadwal.jam_selesai >= jam_sekarang
    ).first()

    # 2. Fallback: jadwal mana saja untuk kelas ini pada hari ini
    if not jadwal:
        jadwal = Jadwal.query.filter_by(kelas_id=kelas_id, hari=hari_ini).first()

    if jadwal:
        return jsonify({
            'success': True,
            'has_jadwal': True,
            'mata_pelajaran': jadwal.mata_pelajaran,
            'guru_nama': jadwal.guru_rel.nama if jadwal.guru_rel else 'Pengajar SMKN 1',
            'kelas_nama': kelas_nama,
            'jam_mulai': jadwal.jam_mulai,
            'jam_selesai': jadwal.jam_selesai
        })
    else:
        return jsonify({
            'success': True,
            'has_jadwal': False,
            'mata_pelajaran': 'Presensi Sesi Umum Sekolah',
            'guru_nama': 'Pengajar SMKN 1 Bangkinang',
            'kelas_nama': kelas_nama
        })


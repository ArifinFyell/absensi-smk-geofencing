from datetime import date
from flask import jsonify, request
from app.models import db, Siswa, Guru, Kelas, Jadwal, Absensi, ActivityLog, Notification, SettingGeofence
from app.helpers.time_helper import get_current_hari, get_current_time_str

def get_realtime_stats():
    today = date.today()
    hari_ini = get_current_hari()

    total_siswa = Siswa.query.filter_by(status='Aktif').count()
    absensi_today = Absensi.query.filter_by(tanggal=today).all()

    hadir_count = sum(1 for a in absensi_today if a.status == 'Hadir')
    terlambat_count = sum(1 for a in absensi_today if a.status in ['Terlambat', 'Terlambat Berat'])
    izin_count = sum(1 for a in absensi_today if a.status == 'Izin')
    sakit_count = sum(1 for a in absensi_today if a.status == 'Sakit')
    total_absen_count = len(absensi_today)
    belum_hadir_count = max(0, total_siswa - total_absen_count)

    persentase_kehadiran = round((hadir_count + terlambat_count) / total_siswa * 100, 1) if total_siswa > 0 else 0

    recent_absensi = [a.to_dict() for a in Absensi.query.filter_by(tanggal=today).order_by(Absensi.id.desc()).limit(6).all()]
    recent_logs = [l.to_dict() for l in ActivityLog.query.order_by(ActivityLog.id.desc()).limit(6).all()]

    return jsonify({
        'total_siswa': total_siswa,
        'hadir_count': hadir_count,
        'terlambat_count': terlambat_count,
        'izin_count': izin_count,
        'sakit_count': sakit_count,
        'belum_hadir_count': belum_hadir_count,
        'total_absen_count': total_absen_count,
        'persentase_kehadiran': persentase_kehadiran,
        'recent_absensi': recent_absensi,
        'recent_logs': recent_logs
    })

def global_search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'students': [], 'schedules': []})

    students = Siswa.query.filter(
        (Siswa.nama.ilike(f'%{q}%')) | (Siswa.nis.ilike(f'%{q}%'))
    ).limit(8).all()

    schedules = Jadwal.query.filter(
        (Jadwal.mata_pelajaran.ilike(f'%{q}%')) | (Jadwal.hari.ilike(f'%{q}%'))
    ).limit(5).all()

    return jsonify({
        'students': [s.to_dict() for s in students],
        'schedules': [sch.to_dict() for sch in schedules]
    })

def get_current_schedule():
    hari_ini = get_current_hari()
    jam_sekarang = get_current_time_str()

    active_jadwal = Jadwal.query.filter(
        Jadwal.hari == hari_ini,
        Jadwal.jam_mulai <= jam_sekarang,
        Jadwal.jam_selesai >= jam_sekarang
    ).first()

    if not active_jadwal:
        active_jadwal = Jadwal.query.filter_by(hari=hari_ini).first()
    if not active_jadwal:
        active_jadwal = Jadwal.query.first()

    return jsonify({
        'hari': hari_ini,
        'jam': jam_sekarang,
        'jadwal': active_jadwal.to_dict() if active_jadwal else None
    })

from datetime import date, datetime
from flask import render_template, request, jsonify
from app.models import db, Siswa, Guru, Kelas, Jadwal, Absensi, ActivityLog, SettingGeofence, SettingJam, SettingSekolah
from app.helpers.time_helper import get_current_hari, get_current_time_str

def index_view():
    today = date.today()
    hari_ini = get_current_hari()

    total_siswa = Siswa.query.filter_by(status='Aktif').count()
    
    # Absensi hari ini
    absensi_today = Absensi.query.filter_by(tanggal=today).all()
    
    hadir_count = sum(1 for a in absensi_today if a.status == 'Hadir')
    terlambat_count = sum(1 for a in absensi_today if a.status in ['Terlambat', 'Terlambat Berat'])
    izin_count = sum(1 for a in absensi_today if a.status == 'Izin')
    sakit_count = sum(1 for a in absensi_today if a.status == 'Sakit')
    total_absen_count = len(absensi_today)
    belum_hadir_count = max(0, total_siswa - total_absen_count)

    persentase_kehadiran = round((hadir_count + terlambat_count) / total_siswa * 100, 1) if total_siswa > 0 else 0

    # Total Jadwal Hari Ini
    total_mapel_hari_ini = Jadwal.query.filter_by(hari=hari_ini).count()
    total_guru_aktif = Guru.query.filter_by(status='Aktif').count()

    # Activity Timeline
    recent_activities = ActivityLog.query.order_by(ActivityLog.id.desc()).limit(8).all()
    
    # Recent Attendance Activity
    recent_absensi = Absensi.query.filter_by(tanggal=today).order_by(Absensi.id.desc()).limit(6).all()

    # Kelas summary
    kelas_list = Kelas.query.all()
    kelas_summary = []
    for k in kelas_list:
        jml_siswa = Siswa.query.filter_by(kelas_id=k.id, status='Aktif').count()
        abs_k = [a for a in absensi_today if a.siswa_rel and a.siswa_rel.kelas_id == k.id]
        h_k = sum(1 for a in abs_k if a.status == 'Hadir')
        t_k = sum(1 for a in abs_k if a.status in ['Terlambat', 'Terlambat Berat'])
        b_k = max(0, jml_siswa - len(abs_k))
        kelas_summary.append({
            'kelas': k,
            'total': jml_siswa,
            'hadir': h_k,
            'terlambat': t_k,
            'belum_hadir': b_k
        })

    sekolah_setting = SettingSekolah.query.first()

    return render_template('dashboard/index.html',
                           total_siswa=total_siswa,
                           hadir_count=hadir_count,
                           terlambat_count=terlambat_count,
                           izin_count=izin_count,
                           sakit_count=sakit_count,
                           belum_hadir_count=belum_hadir_count,
                           persentase_kehadiran=persentase_kehadiran,
                           total_mapel_hari_ini=total_mapel_hari_ini,
                           total_guru_aktif=total_guru_aktif,
                           total_absen_count=total_absen_count,
                           recent_activities=recent_activities,
                           recent_absensi=recent_absensi,
                           kelas_summary=kelas_summary,
                           sekolah_setting=sekolah_setting)

def monitoring_view():
    today = date.today()
    kelas_list = Kelas.query.all()
    absensi_today = Absensi.query.filter_by(tanggal=today).all()

    kelas_detail = []
    for k in kelas_list:
        siswa_in_kelas = Siswa.query.filter_by(kelas_id=k.id, status='Aktif').all()
        siswa_items = []
        for s in siswa_in_kelas:
            abs_rec = next((a for a in absensi_today if a.siswa_id == s.id), None)
            siswa_items.append({
                'siswa': s,
                'absensi': abs_rec
            })
        
        hadir_c = sum(1 for item in siswa_items if item['absensi'] and item['absensi'].status == 'Hadir')
        terlambat_c = sum(1 for item in siswa_items if item['absensi'] and item['absensi'].status in ['Terlambat', 'Terlambat Berat'])
        belum_c = sum(1 for item in siswa_items if not item['absensi'])

        kelas_detail.append({
            'kelas': k,
            'siswa_items': siswa_items,
            'hadir': hadir_c,
            'terlambat': terlambat_c,
            'belum_hadir': belum_c,
            'total': len(siswa_in_kelas)
        })

    return render_template('dashboard/monitoring.html', kelas_detail=kelas_detail)

def detail_absensi_view(absensi_id):
    abs_rec = Absensi.query.get_or_404(absensi_id)
    geofence = SettingGeofence.query.first()
    return render_template('dashboard/detail_absensi.html', absensi=abs_rec, geofence=geofence)

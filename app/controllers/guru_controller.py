from datetime import date, datetime, timedelta
import uuid
from flask import render_template, session, redirect, url_for, request, flash
from app.models import db, User, Guru, Jadwal, Siswa, Absensi, Kelas, SettingSekolah, ActivityLog, HariLibur

# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────
def _get_guru():
    """Return the Guru record linked to the logged-in user, or None."""
    guru_id = session.get('guru_id')
    if guru_id:
        return Guru.query.get(guru_id)
    user_id = session.get('user_id')
    if user_id:
        return Guru.query.filter_by(user_id=user_id).first()
    return None

HARI_ORDER = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']
HARI_MAP   = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}

# ─────────────────────────────────────────────────────────
# Dashboard Guru
# ─────────────────────────────────────────────────────────
def dashboard_view():
    guru = _get_guru()
    if not guru:
        flash('Profil guru tidak ditemukan untuk akun ini.', 'warning')

    today        = date.today()
    hari_ini     = HARI_MAP.get(today.weekday(), 'Senin')
    jam_sekarang = datetime.now().strftime('%H:%M')

    # Jadwal guru hari ini
    jadwal_hari_ini = (Jadwal.query
                       .filter_by(hari=hari_ini, guru_id=guru.id if guru else -1)
                       .order_by(Jadwal.jam_mulai)
                       .all()) if guru else []

    # Semua kelas yang diajar
    kelas_diajar_ids = list({j.kelas_id for j in jadwal_hari_ini if j.kelas_id})

    # Rekap absensi hari ini (per kelas yang guru ini ajar)
    absensi_today = Absensi.query.filter_by(tanggal=today).all()

    kelas_summary = []
    total_siswa_guru = 0
    for kelas_id in kelas_diajar_ids:
        kelas = Kelas.query.get(kelas_id)
        if not kelas:
            continue
        jml = Siswa.query.filter_by(kelas_id=kelas_id, status='Aktif').count()
        abs_k = [a for a in absensi_today if a.siswa_rel and a.siswa_rel.kelas_id == kelas_id]
        hadir = sum(1 for a in abs_k if a.status == 'Hadir')
        terlambat = sum(1 for a in abs_k if a.status in ['Terlambat', 'Terlambat Berat'])
        belum = max(0, jml - len(abs_k))
        kelas_summary.append({'kelas': kelas, 'total': jml, 'hadir': hadir, 'terlambat': terlambat, 'belum_hadir': belum})
        total_siswa_guru += jml

    # Mata pelajaran yang diampu
    mapel_set = list({j.mata_pelajaran for j in (Jadwal.query.filter_by(guru_id=guru.id).all() if guru else [])})

    # Jadwal aktif sekarang
    aktif_now = None
    if guru:
        aktif_now = Jadwal.query.filter(
            Jadwal.hari == hari_ini,
            Jadwal.guru_id == guru.id,
            Jadwal.jam_mulai <= jam_sekarang,
            Jadwal.jam_selesai >= jam_sekarang
        ).first()

    sekolah = SettingSekolah.query.first()

    return render_template('guru/dashboard.html',
                           guru=guru,
                           hari_ini=hari_ini,
                           jadwal_hari_ini=jadwal_hari_ini,
                           aktif_now=aktif_now,
                           kelas_summary=kelas_summary,
                           total_siswa_guru=total_siswa_guru,
                           mapel_set=mapel_set,
                           sekolah=sekolah)

# ─────────────────────────────────────────────────────────
# Jadwal Guru
# ─────────────────────────────────────────────────────────
def jadwal_view():
    guru = _get_guru()
    if not guru:
        flash('Profil guru tidak ditemukan.', 'warning')

    jadwal_semua = {}
    if guru:
        for hari in HARI_ORDER:
            jadwal_semua[hari] = (Jadwal.query
                                  .filter_by(hari=hari, guru_id=guru.id)
                                  .order_by(Jadwal.jam_mulai)
                                  .all())
    else:
        for hari in HARI_ORDER:
            jadwal_semua[hari] = []

    # Ambil daftar hari libur milik guru ini (dan yang berlaku umum)
    hari_libur_records = HariLibur.query.filter(
        (HariLibur.guru_id == (guru.id if guru else None)) |
        (HariLibur.guru_id == None)
    ).all()
    hari_libur_set = {hl.tanggal for hl in hari_libur_records}
    hari_libur_list = sorted(hari_libur_records, key=lambda x: x.tanggal)

    sekolah = SettingSekolah.query.first()
    return render_template('guru/jadwal.html', guru=guru, jadwal_semua=jadwal_semua,
                           hari_libur_set=hari_libur_set, hari_libur_list=hari_libur_list,
                           sekolah=sekolah, today=date.today())

# ─────────────────────────────────────────────────────────
# Absensi Siswa (input manual oleh guru)
# ─────────────────────────────────────────────────────────
def absensi_view():
    guru = _get_guru()
    today = date.today()
    hari_ini = HARI_MAP.get(today.weekday(), 'Senin')

    jadwal_hari_ini = []
    if guru:
        jadwal_hari_ini = (Jadwal.query
                           .filter_by(hari=hari_ini, guru_id=guru.id)
                           .order_by(Jadwal.jam_mulai)
                           .all())

    kelas_diajar_ids = list({j.kelas_id for j in jadwal_hari_ini if j.kelas_id})
    kelas_list = [Kelas.query.get(k) for k in kelas_diajar_ids if Kelas.query.get(k)]

    kelas_id_sel = request.args.get('kelas_id', type=int)
    if not kelas_id_sel and kelas_list:
        kelas_id_sel = kelas_list[0].id

    siswa_list = []
    absensi_map = {}
    if kelas_id_sel:
        siswa_list = Siswa.query.filter_by(kelas_id=kelas_id_sel, status='Aktif').order_by(Siswa.nama).all()
        abs_today = Absensi.query.filter(
            Absensi.siswa_id.in_([s.id for s in siswa_list]),
            Absensi.tanggal == today
        ).all()
        absensi_map = {a.siswa_id: a for a in abs_today}

    sekolah = SettingSekolah.query.first()
    return render_template('guru/absensi.html',
                           guru=guru,
                           hari_ini=hari_ini,
                           today=today,
                           jadwal_hari_ini=jadwal_hari_ini,
                           kelas_list=kelas_list,
                           kelas_id_sel=kelas_id_sel,
                           siswa_list=siswa_list,
                           absensi_map=absensi_map,
                           sekolah=sekolah)

def simpan_absensi_action():
    """Guru manually records attendance for a student."""
    guru = _get_guru()
    if not guru:
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('guru.absensi'))

    siswa_id = request.form.get('siswa_id', type=int)
    status   = request.form.get('status', '').strip()
    keterangan = request.form.get('keterangan', '').strip()
    today    = date.today()
    valid_statuses = ['Hadir', 'Sakit', 'Izin', 'Alfa', 'Terlambat']

    if not siswa_id or status not in valid_statuses:
        flash('Data tidak valid.', 'danger')
        return redirect(url_for('guru.absensi'))

    siswa = Siswa.query.get_or_404(siswa_id)

    existing = Absensi.query.filter_by(siswa_id=siswa_id, tanggal=today).first()
    if existing:
        existing.status     = status
        existing.keterangan = keterangan
        existing.updated_by = f"guru:{guru.nama}"
    else:
        new_abs = Absensi(
            siswa_id   = siswa_id,
            tanggal    = today,
            jam_masuk  = datetime.now().strftime('%H:%M:%S'),
            status     = status,
            keterangan = keterangan,
            latitude   = None,
            longitude  = None,
            jarak      = 0,
            foto       = None,
            device     = 'Manual (Guru)',
            ip_address = request.remote_addr,
        )
        db.session.add(new_abs)

    db.session.add(ActivityLog(
        user=guru.nama,
        aktivitas=f"Input absensi manual: {siswa.nama} – {status}."
    ))
    db.session.commit()
    flash(f'Absensi {siswa.nama} berhasil disimpan [{status}].', 'success')
    kelas_id = request.form.get('kelas_id')
    return redirect(url_for('guru.absensi', kelas_id=kelas_id))

# ─────────────────────────────────────────────────────────
# Rekap Absensi
# ─────────────────────────────────────────────────────────
def rekap_view():
    guru = _get_guru()
    today  = date.today()
    # Default: current month
    bulan  = request.args.get('bulan', today.month, type=int)
    tahun  = request.args.get('tahun', today.year, type=int)
    kelas_id_sel = request.args.get('kelas_id', type=int)

    # Kelas yang diajar guru ini
    kelas_diajar_ids_all = list({j.kelas_id for j in (Jadwal.query.filter_by(guru_id=guru.id).all() if guru else []) if j.kelas_id})
    kelas_list = [Kelas.query.get(k) for k in kelas_diajar_ids_all if Kelas.query.get(k)]

    if not kelas_id_sel and kelas_list:
        kelas_id_sel = kelas_list[0].id

    siswa_list = []
    rekap_data = []
    hari_list  = []

    if kelas_id_sel:
        # Build day list for selected month
        import calendar
        _, days_in_month = calendar.monthrange(tahun, bulan)
        for d in range(1, days_in_month + 1):
            dt = date(tahun, bulan, d)
            if dt.weekday() < 5:  # Mon–Fri only
                hari_list.append(dt)

        siswa_list = Siswa.query.filter_by(kelas_id=kelas_id_sel, status='Aktif').order_by(Siswa.nama).all()
        abs_bulan  = Absensi.query.filter(
            Absensi.tanggal >= date(tahun, bulan, 1),
            Absensi.tanggal <= date(tahun, bulan, days_in_month),
            Absensi.siswa_id.in_([s.id for s in siswa_list])
        ).all()

        abs_by_siswa_day = {}
        for a in abs_bulan:
            abs_by_siswa_day[(a.siswa_id, a.tanggal)] = a

        for siswa in siswa_list:
            baris = {'siswa': siswa, 'hari': {}, 'hadir': 0, 'terlambat': 0, 'sakit': 0, 'izin': 0, 'alfa': 0}
            for hari_dt in hari_list:
                rec = abs_by_siswa_day.get((siswa.id, hari_dt))
                baris['hari'][hari_dt] = rec
                if rec:
                    if rec.status == 'Hadir':       baris['hadir'] += 1
                    elif rec.status in ['Terlambat', 'Terlambat Berat']: baris['terlambat'] += 1
                    elif rec.status == 'Sakit':      baris['sakit'] += 1
                    elif rec.status == 'Izin':       baris['izin'] += 1
                    else:                             baris['alfa'] += 1
            rekap_data.append(baris)

    sekolah = SettingSekolah.query.first()
    bulan_list = [
        (1,'Januari'),(2,'Februari'),(3,'Maret'),(4,'April'),
        (5,'Mei'),(6,'Juni'),(7,'Juli'),(8,'Agustus'),
        (9,'September'),(10,'Oktober'),(11,'November'),(12,'Desember')
    ]
    return render_template('guru/rekap.html',
                           guru=guru,
                           kelas_list=kelas_list,
                           kelas_id_sel=kelas_id_sel,
                           hari_list=hari_list,
                           siswa_list=siswa_list,
                           rekap_data=rekap_data,
                           bulan=bulan, tahun=tahun,
                           bulan_list=bulan_list,
                           sekolah=sekolah)

# ─────────────────────────────────────────────────────────
# Profil Guru
# ─────────────────────────────────────────────────────────
def profil_view():
    guru = _get_guru()
    user = User.query.get(session.get('user_id'))
    sekolah = SettingSekolah.query.first()
    return render_template('guru/profil.html', guru=guru, user=user, sekolah=sekolah)

# ─────────────────────────────────────────────────────────
# Verifikasi Email Guru
# ─────────────────────────────────────────────────────────
def verify_email_view():
    guru = _get_guru()
    if not guru:
        return redirect(url_for('auth.login'))
    if guru.is_email_verified:
        return redirect(url_for('guru.dashboard'))
    return render_template('guru/verify_email.html', guru=guru)

def request_verification_action():
    guru = _get_guru()
    if not guru:
        return redirect(url_for('auth.login'))
        
    email_input = request.form.get('email', '').strip()
    if not email_input:
        flash('Silakan masukkan email yang valid.', 'warning')
        return redirect(url_for('guru.verify_email'))
        
    guru.email = email_input
    
    # Generate token
    token = uuid.uuid4().hex
    guru.verification_token = token
    db.session.commit()
    
    # MOCK EMAIL SENDER (Logs to console)
    verification_link = url_for('guru.process_verification', token=token, _external=True)
    print("=" * 60)
    print("MOCK EMAIL VERIFICATION SENT")
    print(f"To: {guru.email}")
    print(f"Subject: Verifikasi Email & Setel Sandi Baru")
    print(f"Link: {verification_link}")
    print("=" * 60)
    
    flash('Link verifikasi telah dikirim ke email Anda! (Silakan cek terminal/konsol server untuk menyimulasikan klik link)', 'info')
    return redirect(url_for('guru.verify_email'))

def process_verification_action(token):
    guru = Guru.query.filter_by(verification_token=token).first()
    if not guru:
        flash('Token verifikasi tidak valid atau sudah kadaluarsa.', 'danger')
        return redirect(url_for('auth.login'))
        
    # Tampilkan halaman untuk set custom password
    return render_template('guru/set_verified_password.html', token=token, guru=guru)

def set_verified_password_action():
    token = request.form.get('token')
    password_baru = request.form.get('password_baru', '').strip()
    konfirmasi = request.form.get('konfirmasi', '').strip()
    
    guru = Guru.query.filter_by(verification_token=token).first()
    if not guru:
        flash('Token verifikasi tidak valid atau sudah kadaluarsa.', 'danger')
        return redirect(url_for('auth.login'))
        
    if len(password_baru) < 8:
        flash('Sandi baru minimal 8 karakter.', 'danger')
        return render_template('guru/set_verified_password.html', token=token, guru=guru)
        
    if password_baru != konfirmasi:
        flash('Konfirmasi sandi tidak cocok.', 'danger')
        return render_template('guru/set_verified_password.html', token=token, guru=guru)
        
    # 1. Update Guru status
    guru.is_email_verified = True
    guru.verification_token = None
    
    # 2. Update User Account
    user = User.query.get(guru.user_id)
    user.username = guru.email
    user.set_password(password_baru)
    
    db.session.add(ActivityLog(user=guru.nama, aktivitas=f"Memverifikasi email dan mengubah username login menjadi {guru.email}"))
    db.session.commit()
    
    flash(f'Verifikasi berhasil! Sekarang Anda dapat login menggunakan email {guru.email} dan sandi baru Anda.', 'success')
    # Logout agar mereka login ulang dengan kredensial baru
    session.clear()
    return redirect(url_for('auth.login'))

# ─────────────────────────────────────────────────────────
# Manajemen Hari Libur Guru
# ─────────────────────────────────────────────────────────
def tambah_libur_action():
    guru = _get_guru()
    if not guru:
        flash('Profil guru tidak ditemukan.', 'warning')
        return redirect(url_for('guru.jadwal'))

    tanggal_str = request.form.get('tanggal', '').strip()
    keterangan  = request.form.get('keterangan', '').strip() or 'Libur'

    if not tanggal_str:
        flash('Tanggal tidak boleh kosong.', 'danger')
        return redirect(url_for('guru.jadwal'))

    try:
        tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Format tanggal tidak valid.', 'danger')
        return redirect(url_for('guru.jadwal'))

    # Cek duplikat
    existing = HariLibur.query.filter_by(tanggal=tanggal, guru_id=guru.id).first()
    if existing:
        flash(f'Tanggal {tanggal.strftime("%d %B %Y")} sudah ditandai sebagai hari libur.', 'warning')
        return redirect(url_for('guru.jadwal'))

    libur = HariLibur(tanggal=tanggal, keterangan=keterangan,
                      guru_id=guru.id, dibuat_oleh=guru.nama)
    db.session.add(libur)
    db.session.add(ActivityLog(user=guru.nama, aktivitas=f'Menandai {tanggal.strftime("%d %B %Y")} sebagai hari libur: {keterangan}'))
    db.session.commit()

    flash(f'Tanggal {tanggal.strftime("%d %B %Y")} berhasil ditandai sebagai libur.', 'success')
    return redirect(url_for('guru.jadwal'))


def hapus_libur_action(libur_id):
    guru = _get_guru()
    libur = HariLibur.query.get_or_404(libur_id)

    # Hanya boleh hapus miliknya sendiri
    if libur.guru_id != (guru.id if guru else None):
        flash('Anda tidak memiliki izin untuk menghapus data ini.', 'danger')
        return redirect(url_for('guru.jadwal'))

    db.session.add(ActivityLog(user=guru.nama, aktivitas=f'Menghapus hari libur: {libur.tanggal.strftime("%d %B %Y")}'))
    db.session.delete(libur)
    db.session.commit()

    flash('Hari libur berhasil dihapus.', 'success')
    return redirect(url_for('guru.jadwal'))


# ─────────────────────────────────────────────────────────
# Monitoring Absensi Wali Kelas (HANYA WALI KELAS)
# ─────────────────────────────────────────────────────────
def absensi_wali_kelas_view():
    guru = _get_guru()
    if not guru or not guru.is_wali_kelas:
        flash('Akses ditolak! Fitur ini HANYA dapat diakses oleh Wali Kelas.', 'danger')
        return redirect(url_for('guru.dashboard'))

    kelas_wali = guru.wali_kelas_rel
    if not kelas_wali:
        flash('Anda belum ditugaskan sebagai Wali Kelas di kelas manapun.', 'warning')
        return redirect(url_for('guru.dashboard'))

    # Tanggal filter (default hari ini)
    tanggal_str = request.args.get('tanggal', date.today().strftime('%Y-%m-%d'))
    try:
        tgl_selected = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
    except ValueError:
        tgl_selected = date.today()

    # Dapatkan semua siswa di kelas wali ini
    siswa_list = Siswa.query.filter_by(kelas_id=kelas_wali.id).order_by(Siswa.nama).all()
    siswa_ids = [s.id for s in siswa_list]

    # Dapatkan semua record absensi siswa kelas ini pada tanggal tgl_selected (diinput oleh guru mana pun)
    absensi_records = []
    if siswa_ids:
        absensi_records = (Absensi.query
                           .filter(Absensi.siswa_id.in_(siswa_ids), Absensi.tanggal == tgl_selected)
                           .all())

    # Map absensi per siswa_id (jika ada lebih dari 1 per hari, ambil yang terbaru)
    absensi_map = {}
    for a in absensi_records:
        absensi_map[a.siswa_id] = a

    # Summary statistik
    total_siswa = len(siswa_list)
    hadir = sum(1 for a in absensi_records if a.status == 'Hadir')
    terlambat = sum(1 for a in absensi_records if a.status in ['Terlambat', 'Terlambat Berat'])
    izin = sum(1 for a in absensi_records if a.status == 'Izin')
    sakit = sum(1 for a in absensi_records if a.status == 'Sakit')
    alpa = sum(1 for a in absensi_records if a.status == 'Alpa')
    belum = max(0, total_siswa - len(absensi_map))

    sekolah = SettingSekolah.query.first()

    return render_template('guru/absensi_wali_kelas.html',
                           guru=guru,
                           kelas_wali=kelas_wali,
                           siswa_list=siswa_list,
                           absensi_map=absensi_map,
                           tgl_selected=tgl_selected,
                           summary={
                               'total': total_siswa,
                               'hadir': hadir,
                               'terlambat': terlambat,
                               'izin': izin,
                               'sakit': sakit,
                               'alpa': alpa,
                               'belum': belum
                           },
                           sekolah=sekolah)


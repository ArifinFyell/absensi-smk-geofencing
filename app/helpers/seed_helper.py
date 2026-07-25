from datetime import datetime, date
from app.models import db, User, Guru, Kelas, Jurusan, Siswa, Jadwal, SettingGeofence, SettingJam, SettingSekolah, Absensi, ActivityLog, Notification

def seed_initial_data():
    """Seed initial demo data if database is empty"""
    # 1. Admin User & Wali Kelas User
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(username='2455201011', role='admin', nama='Administrator SMKN 1 Bangkinang')
        admin.set_password('Arifin123')
        db.session.add(admin)

    db.session.commit()

    # 2. Setting Default
    if not SettingGeofence.query.first():
        geo = SettingGeofence(latitude=0.334612, longitude=101.026415, radius=100)
        db.session.add(geo)

    if not SettingJam.query.first():
        jam = SettingJam(jam_hadir_mulai='06:45', jam_hadir_selesai='07:15', jam_terlambat_selesai='07:30', jam_tutup='17:00')
        db.session.add(jam)

    sekolah = SettingSekolah.query.first()
    if not sekolah:
        sekolah = SettingSekolah(
            nama_sekolah='SMK Negeri 1 Bangkinang',
            alamat_sekolah='Jl. Tuanku Tambusai No. 1, Bangkinang, Kampar, Riau',
            logo='logo_smkn1.png',
            tahun_ajaran='2025/2026',
            semester='Semester Genap (Januari–Juni 2026)'
        )
        db.session.add(sekolah)
    else:
        sekolah.nama_sekolah = 'SMK Negeri 1 Bangkinang'
        sekolah.semester = 'Semester Genap (Januari–Juni 2026)'

    # 3. Jurusan
    jurusan_pplg = Jurusan.query.filter_by(kode='PPLG').first()
    if not jurusan_pplg:
        jurusan_pplg = Jurusan(nama_jurusan='Pengembangan Perangkat Lunak dan Gim', kode='PPLG')
        db.session.add(jurusan_pplg)
        db.session.commit()

    # 4. Kelas
    kelas_x_pplg = Kelas.query.filter_by(nama_kelas='X PPLG').first()
    if not kelas_x_pplg:
        kelas_x_pplg = Kelas(nama_kelas='X PPLG', wali_kelas='Ariefin Danu Putra, S.Kom.', tingkat='X')
        db.session.add(kelas_x_pplg)
        db.session.commit()
    else:
        kelas_x_pplg.wali_kelas = 'Ariefin Danu Putra, S.Kom.'

    guru_data = [
        {'nama': 'Ariefin Danu Putra, S.Kom.', 'email': 'ariefin@smkn1bangkinang.sch.id'},
        {'nama': 'Parsaoran Sitohang, S.T., M.Kom.', 'email': 'parsaoran@smkn1bangkinang.sch.id'},
        {'nama': 'Muhfiza Yarni, S.Pd.', 'email': 'muhfiza@smkn1bangkinang.sch.id'},
        {'nama': 'Respikayati, S.Sos.I.', 'email': 'respikayati@smkn1bangkinang.sch.id'},
        {'nama': 'Siska Hedyati, S.Kom.', 'email': 'siska@smkn1bangkinang.sch.id'},
        {'nama': 'Ilham Fitra, M.Kom.', 'email': 'ilham@smkn1bangkinang.sch.id'},
        {'nama': 'Seri Bayuni, S.Pd.', 'email': 'seri@smkn1bangkinang.sch.id'},
        {'nama': 'Kasmi Yetti, S.Pd.', 'email': 'kasmi@smkn1bangkinang.sch.id'},
        {'nama': 'Upik Hartati, S.Pd.', 'email': 'upik@smkn1bangkinang.sch.id'},
        {'nama': 'Fuad Saadi, M.Pd.', 'email': 'fuad@smkn1bangkinang.sch.id'},
        {'nama': 'Nini Rakhmayuni, S.Sn.', 'email': 'nini@smkn1bangkinang.sch.id'},
        {'nama': 'Novita, S.Pd.', 'email': 'novita@smkn1bangkinang.sch.id'},
        {'nama': 'Risnelita, S.S.', 'email': 'risnelita@smkn1bangkinang.sch.id'},
        {'nama': 'Rina Sutria, S.Si.', 'email': 'rina@smkn1bangkinang.sch.id'},
        {'nama': 'Siti Rochimah, S.Pd.', 'email': 'siti@smkn1bangkinang.sch.id'},
    ]

    for idx, g in enumerate(guru_data, 1):
        nip_guru = f"GR{idx:03d}"
        
        # Create user account for each guru
        guru_user = User.query.filter_by(username=nip_guru).first()
        if not guru_user:
            guru_user = User(username=nip_guru, role='guru', nama=g['nama'])
            guru_user.set_password('guru123')
            db.session.add(guru_user)
            db.session.flush() # To get user ID

        existing = Guru.query.filter_by(nama=g['nama']).first()
        if not existing:
            obj = Guru(
                nama=g['nama'],
                nip=nip_guru,
                email=g['email'],
                no_hp='0812' + str(abs(hash(g['nama'])))[-8:],
                status='Aktif',
                user_id=guru_user.id
            )
            db.session.add(obj)
        else:
            existing.user_id = guru_user.id
            existing.nip = nip_guru
            
    db.session.commit()

    # 6. Data Siswa Realistic
    siswa_names = [
        ("240001", "Ahmad Fauzi", "Laki-Laki"),
        ("240002", "Siti Aisyah", "Perempuan"),
        ("240003", "Muhammad Rizki", "Laki-Laki"),
        ("240004", "Nurhaliza Putri", "Perempuan"),
        ("240005", "Yoga Saputra", "Laki-Laki"),
        ("240006", "Rina Safitri", "Perempuan"),
        ("240007", "Fajar Ramadhan", "Laki-Laki"),
        ("240008", "Annisa Maharani", "Perempuan"),
        ("240009", "Dimas Pratama", "Laki-Laki"),
        ("240010", "Nabila Zahra", "Perempuan"),
        ("240011", "Bayu Kurniawan", "Laki-Laki"),
        ("240012", "Dewi Lestari", "Perempuan"),
        ("240013", "Eko Prasetyo", "Laki-Laki"),
        ("240014", "Fitriani", "Perempuan"),
        ("240015", "Gilang Ramadhan", "Laki-Laki"),
        ("240016", "Indah Permata", "Perempuan"),
        ("240017", "Joko Susilo", "Laki-Laki"),
        ("240018", "Kartika Sari", "Perempuan"),
        ("240019", "Lukman Hakim", "Laki-Laki"),
        ("240020", "Maya Anggraini", "Perempuan"),
        ("240021", "Naufal Alamsyah", "Laki-Laki"),
        ("240022", "Olivia Zalianty", "Perempuan"),
        ("240023", "Pandu Wijaya", "Laki-Laki"),
        ("240024", "Qori Afifah", "Perempuan"),
        ("240025", "Raihan Maulana", "Laki-Laki"),
        ("240026", "Suci Rahmadani", "Perempuan"),
        ("240027", "Taufik Hidayat", "Laki-Laki"),
        ("240028", "Ulfa Dwiyanti", "Perempuan"),
        ("240029", "Viko Aditya", "Laki-Laki"),
        ("240030", "Wulandari", "Perempuan"),
        ("240031", "Yusuf Bachtiar", "Laki-Laki"),
        ("240032", "Zahra Amelia", "Perempuan"),
        ("240033", "Ari Irwansyah", "Laki-Laki"),
        ("240034", "Tari Puspita", "Perempuan")
    ]

    siswa_objs = []
    if Siswa.query.count() == 0:
        for nis, nama, jk in siswa_names:
            s = Siswa(
                nis=nis,
                nama=nama,
                kelas_id=kelas_x_pplg.id,
                jurusan_id=jurusan_pplg.id,
                jenis_kelamin=jk,
                alamat='Bangkinang, Kampar',
                no_hp='082284' + nis,
                status='Aktif'
            )
            db.session.add(s)
            siswa_objs.append(s)
        db.session.commit()
    else:
        siswa_objs = Siswa.query.all()

    # 7. Seed Complete Schedule Kelas X PPLG (Senin - Jumat)
    # Helper to get guru ID by name
    def get_guru_id(nama):
        if not nama or nama == '-':
            return None
        g = Guru.query.filter_by(nama=nama).first()
        return g.id if g else None

    # We re-seed the exact schedule for X PPLG
    db.session.query(Jadwal).delete()

    raw_jadwal = [
        # Senin
        ('Senin', '07:20', '08:00', 'Informatika', 'Parsaoran Sitohang, S.T., M.Kom.'),
        ('Senin', '08:00', '08:40', 'Informatika', 'Parsaoran Sitohang, S.T., M.Kom.'),
        ('Senin', '08:40', '09:20', 'Informatika', 'Parsaoran Sitohang, S.T., M.Kom.'),
        ('Senin', '09:20', '09:50', 'ISTIRAHAT', '-'),
        ('Senin', '09:50', '10:30', 'Informatika', 'Parsaoran Sitohang, S.T., M.Kom.'),
        ('Senin', '10:30', '11:10', 'IPAS', 'Muhfiza Yarni, S.Pd.'),
        ('Senin', '11:10', '11:50', 'IPAS', 'Muhfiza Yarni, S.Pd.'),
        ('Senin', '11:50', '12:30', 'DZUHUR', '-'),
        ('Senin', '13:10', '13:50', 'Pendidikan Agama Islam', 'Respikayati, S.Sos.I.'),
        ('Senin', '13:50', '14:30', 'Pendidikan Agama Islam', 'Respikayati, S.Sos.I.'),
        ('Senin', '14:30', '15:10', 'Pendidikan Agama Islam', 'Respikayati, S.Sos.I.'),

        # Selasa
        ('Selasa', '07:20', '08:00', 'Dasar Program Keahlian', 'Siska Hedyati, S.Kom.'),
        ('Selasa', '08:00', '08:40', 'Dasar Program Keahlian', 'Siska Hedyati, S.Kom.'),
        ('Selasa', '08:40', '09:20', 'Dasar Program Keahlian', 'Siska Hedyati, S.Kom.'),
        ('Selasa', '09:20', '09:50', 'ISTIRAHAT', '-'),
        ('Selasa', '09:50', '10:30', 'Dasar Program Keahlian', 'Ilham Fitra, M.Kom.'),
        ('Selasa', '10:30', '11:10', 'Dasar Program Keahlian', 'Ilham Fitra, M.Kom.'),
        ('Selasa', '11:10', '11:50', 'Dasar Program Keahlian', 'Ilham Fitra, M.Kom.'),
        ('Selasa', '11:50', '12:30', 'Bimbingan Konseling', 'Seri Bayuni, S.Pd.'),
        ('Selasa', '12:30', '13:10', 'DZUHUR', '-'),
        ('Selasa', '13:10', '13:50', 'Seni Budaya', 'Kasmi Yetti, S.Pd.'),
        ('Selasa', '13:50', '14:30', 'Seni Budaya', 'Kasmi Yetti, S.Pd.'),
        ('Selasa', '14:30', '15:10', 'PPKn', 'Upik Hartati, S.Pd.'),
        ('Selasa', '15:10', '15:50', 'PPKn', 'Upik Hartati, S.Pd.'),

        # Rabu
        ('Rabu', '07:20', '08:00', 'Pendidikan Jasmani', 'Fuad Saadi, M.Pd.'),
        ('Rabu', '08:00', '08:40', 'Pendidikan Jasmani', 'Fuad Saadi, M.Pd.'),
        ('Rabu', '08:40', '09:20', 'Pendidikan Jasmani', 'Fuad Saadi, M.Pd.'),
        ('Rabu', '09:20', '09:50', 'ISTIRAHAT', '-'),
        ('Rabu', '09:50', '10:30', 'BMR', 'Nini Rakhmayuni, S.Sn.'),
        ('Rabu', '10:30', '11:10', 'BMR', 'Nini Rakhmayuni, S.Sn.'),
        ('Rabu', '11:10', '11:50', 'Sejarah Indonesia', 'Novita, S.Pd.'),
        ('Rabu', '11:50', '12:30', 'Sejarah Indonesia', 'Novita, S.Pd.'),
        ('Rabu', '12:30', '13:10', 'DZUHUR', '-'),
        ('Rabu', '13:10', '13:50', 'Bahasa Inggris', 'Risnelita, S.S.'),
        ('Rabu', '13:50', '14:30', 'Bahasa Inggris', 'Risnelita, S.S.'),
        ('Rabu', '14:30', '15:10', 'Bahasa Inggris', 'Risnelita, S.S.'),
        ('Rabu', '15:10', '15:50', 'Bahasa Inggris', 'Risnelita, S.S.'),

        # Kamis
        ('Kamis', '07:20', '08:00', 'Dasar Program Keahlian', 'Siska Hedyati, S.Kom.'),
        ('Kamis', '08:00', '08:40', 'Dasar Program Keahlian', 'Siska Hedyati, S.Kom.'),
        ('Kamis', '08:40', '09:20', 'Dasar Program Keahlian', 'Siska Hedyati, S.Kom.'),
        ('Kamis', '09:20', '09:50', 'ISTIRAHAT', '-'),
        ('Kamis', '09:50', '10:30', 'Matematika', 'Rina Sutria, S.Si.'),
        ('Kamis', '10:30', '11:10', 'Matematika', 'Rina Sutria, S.Si.'),
        ('Kamis', '11:10', '11:50', 'Matematika', 'Rina Sutria, S.Si.'),
        ('Kamis', '11:50', '12:30', 'Matematika', 'Rina Sutria, S.Si.'),
        ('Kamis', '12:30', '13:10', 'DZUHUR', '-'),
        ('Kamis', '13:10', '13:50', 'Bahasa Indonesia', 'Siti Rochimah, S.Pd.'),
        ('Kamis', '13:50', '14:30', 'Bahasa Indonesia', 'Siti Rochimah, S.Pd.'),
        ('Kamis', '14:30', '15:10', 'Bahasa Indonesia', 'Siti Rochimah, S.Pd.'),
        ('Kamis', '15:10', '15:50', 'Bahasa Indonesia', 'Siti Rochimah, S.Pd.'),

        # Jumat
        ('Jumat', '07:20', '08:00', 'Dasar Program Keahlian', 'Siska Hedyati, S.Kom.'),
        ('Jumat', '08:00', '08:40', 'Dasar Program Keahlian', 'Siska Hedyati, S.Kom.'),
        ('Jumat', '08:40', '09:20', 'IPAS', 'Muhfiza Yarni, S.Pd.'),
        ('Jumat', '09:20', '09:50', 'IPAS', 'Muhfiza Yarni, S.Pd.'),
        ('Jumat', '09:50', '10:30', 'IPAS', 'Muhfiza Yarni, S.Pd.'),
        ('Jumat', '10:30', '11:10', 'ISTIRAHAT', '-'),
        ('Jumat', '11:10', '11:50', 'Kegiatan Keagamaan', '-'),
        ('Jumat', '11:50', '12:30', 'Kepulangan', '-'),
    ]

    for hari, jm, js, mapel, g_nama in raw_jadwal:
        db.session.add(Jadwal(
            hari=hari,
            jam_mulai=jm,
            jam_selesai=js,
            mata_pelajaran=mapel,
            guru_id=get_guru_id(g_nama),
            kelas_id=kelas_x_pplg.id
        ))
    db.session.commit()

    # 8. Sample Attendance Entries
    if Absensi.query.count() == 0:
        j_first = Jadwal.query.filter_by(hari='Senin').first()
        today = date.today()
        sample_records = [
            (siswa_objs[0], "07:02:15", "Hadir", 15.2),
            (siswa_objs[1], "07:04:30", "Hadir", 22.4),
            (siswa_objs[2], "07:05:10", "Hadir", 18.0),
            (siswa_objs[3], "07:09:45", "Hadir", 30.1),
            (siswa_objs[4], "07:18:20", "Terlambat", 45.5),
            (siswa_objs[5], "07:22:00", "Terlambat", 12.8),
            (siswa_objs[6], "07:03:00", "Hadir", 8.3),
            (siswa_objs[7], "07:06:12", "Hadir", 11.2),
            (siswa_objs[8], "07:32:00", "Terlambat Berat", 55.0),
            (siswa_objs[9], "07:01:50", "Hadir", 14.7),
        ]

        for s_obj, jam_m, st, dist in sample_records:
            abs_obj = Absensi(
                siswa_id=s_obj.id,
                jadwal_id=j_first.id if j_first else None,
                tanggal=today,
                jam_masuk=jam_m,
                latitude=0.334615,
                longitude=101.026420,
                jarak=dist,
                foto='sample_face.jpg',
                status=st,
                device='Android / Chrome Mobile',
                ip_address='192.168.1.45',
                browser='Chrome 126.0'
            )
            db.session.add(abs_obj)
        db.session.commit()

    # 9. Activity Logs & Notifications
    if ActivityLog.query.count() == 0:
        logs = [
            ("System", "Inisialisasi sistem absensi Kelas X PPLG SMKN 1 Bangkinang berhasil."),
            ("Admin", "Mengonfigurasi data jadwal pelajaran Semester Genap (Januari-Juni 2026)."),
            ("Ariefin Danu Putra, S.Kom.", "Wali Kelas X PPLG login ke sistem monitoring absensi."),
            ("Ahmad Fauzi", "Berhasil melakukan absensi foto pada mata pelajaran Informatika."),
            ("Yoga Saputra", "Melakukan absensi dengan status Terlambat (07:18).")
        ]
        for usr, act in logs:
            db.session.add(ActivityLog(user=usr, aktivitas=act))
        db.session.commit()

    if Notification.query.count() == 0:
        notifs = [
            ("Sistem Absensi Aktif", "Jadwal Kelas X PPLG Semester Genap (Januari-Juni 2026) SMKN 1 Bangkinang aktif.", "success"),
            ("Informasi Sesi Absensi", "Sesi absensi X PPLG mata pelajaran Informatika telah berlangsung.", "info"),
            ("Notifikasi Keterlambatan", "2 Siswa tercatat mengalami keterlambatan hari ini.", "warning")
        ]
        for jdl, psn, tp in notifs:
            db.session.add(Notification(judul=jdl, pesan=psn, tipe=tp))
        db.session.commit()

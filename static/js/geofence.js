// Geofence & Camera Module for Student Attendance Portal

window.GeofenceApp = function(schoolLat, schoolLon, maxRadiusMeters) {
  return {
    schoolLat: parseFloat(schoolLat) || 0.334612,
    schoolLon: parseFloat(schoolLon) || 101.026415,
    maxRadius: parseInt(maxRadiusMeters) || 100,

    userLat: None = null,
    userLon: None = null,
    distance: 0,
    isGpsActive: false,
    isWithinRadius: false,
    gpsStatusText: 'Meminta Izin GPS...',
    gpsErrorMsg: '',
    
    // Form fields
    nama: '',
    nis: '',
    kelas_id: '',
    jurusan_id: '',
    photoDataUrl: null,
    photoFile: null,
    isCameraOpen: false,
    isSubmitting: false,
    isSuccess: false,
    successData: null,

    // Real-time Schedule Detection State
    activeJadwalMapel: 'Presensi Sesi Umum Sekolah',
    activeJadwalGuru: 'Pengajar SMKN 1 Bangkinang',
    activeJadwalKelas: '-',
    hasJadwal: false,
    isScheduleLoading: false,

    async fetchJadwalByKelas() {
      if (!this.kelas_id) {
        this.activeJadwalMapel = 'Presensi Sesi Umum Sekolah';
        this.activeJadwalGuru = 'Pengajar SMKN 1 Bangkinang';
        this.activeJadwalKelas = '-';
        this.hasJadwal = false;
        return;
      }

      this.isScheduleLoading = true;
      try {
        const res = await fetch('/absensi-siswa/api/get-jadwal-by-kelas?kelas_id=' + this.kelas_id);
        const data = await res.json();
        if (data.success && data.has_jadwal) {
          this.activeJadwalMapel = data.mata_pelajaran;
          this.activeJadwalGuru = data.guru_nama;
          this.activeJadwalKelas = data.kelas_nama;
          this.hasJadwal = true;
        } else {
          this.activeJadwalMapel = data.mata_pelajaran || 'Presensi Sesi Umum Sekolah';
          this.activeJadwalGuru = data.guru_nama || 'Pengajar SMKN 1 Bangkinang';
          this.activeJadwalKelas = data.kelas_nama || '-';
          this.hasJadwal = false;
        }
      } catch (e) {
        console.error('Error fetching schedule:', e);
      } finally {
        this.isScheduleLoading = false;
      }
    },

    init() {
      this.requestLocation();
    },

    requestLocation() {
      this.gpsStatusText = 'Mendeteksi Lokasi GPS...';
      if (!navigator.geolocation) {
        this.gpsStatusText = 'GPS Tidak Didukung Browser';
        this.gpsErrorMsg = 'Perangkat Anda tidak mendukung fitur Geolocation.';
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          this.userLat = position.coords.latitude;
          this.userLon = position.coords.longitude;
          this.isGpsActive = true;

          this.distance = this.calculateHaversine(
            this.userLat, this.userLon,
            this.schoolLat, this.schoolLon
          );

          this.isWithinRadius = this.distance <= this.maxRadius;

          if (this.isWithinRadius) {
            this.gpsStatusText = `✓ Berada di Area Sekolah (${Math.round(this.distance)}m dari sekolah)`;
          } else {
            this.gpsStatusText = `✗ Di luar Area Sekolah (${Math.round(this.distance)}m, max ${this.maxRadius}m)`;
          }
        },
        (error) => {
          this.isGpsActive = false;
          this.isWithinRadius = false;
          switch (error.code) {
            case error.PERMISSION_DENIED:
              this.gpsStatusText = 'Izin Lokasi Ditolak';
              this.gpsErrorMsg = 'Akses lokasi diperlukan untuk melakukan absensi. Silakan aktifkan GPS pada browser Anda.';
              break;
            case error.POSITION_UNAVAILABLE:
              this.gpsStatusText = 'Sinyal GPS Tidak Ditemukan';
              this.gpsErrorMsg = 'Informasi lokasi tidak tersedia. Pastikan GPS perangkat Anda aktif.';
              break;
            case error.TIMEOUT:
              this.gpsStatusText = 'Waktu GPS Habis';
              this.gpsErrorMsg = 'Pemeriksaan lokasi GPS memakan waktu terlalu lama. Silakan coba lagi.';
              break;
          }
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      );
    },

    calculateHaversine(lat1, lon1, lat2, lon2) {
      const R = 6371000; // meters
      const dLat = (lat2 - lat1) * Math.PI / 180;
      const dLon = (lon2 - lon1) * Math.PI / 180;
      const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                Math.sin(dLon / 2) * Math.sin(dLon / 2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      return R * c;
    },

    handleFileSelect(event) {
      const file = event.target.files[0];
      if (!file) return;

      if (file.size > 2 * 1024 * 1024) {
        window.showToast('Ukuran foto maksimal 2 MB.', 'danger', 'Gagal Upload Foto');
        event.target.value = '';
        return;
      }

      this.photoFile = file;
      const reader = new FileReader();
      reader.onload = (e) => {
        this.photoDataUrl = e.target.result;
      };
      reader.readAsDataURL(file);
    },

    async openCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
        const video = document.getElementById('camera-video');
        if (video) {
          video.srcObject = stream;
          video.play();
          this.isCameraOpen = true;
        }
      } catch (err) {
        window.showToast('Tidak dapat mengakes kamera perangkat. Silakan gunakan tombol Upload Foto.', 'warning');
      }
    },

    capturePhoto() {
      const video = document.getElementById('camera-video');
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      this.photoDataUrl = canvas.toDataURL('image/jpeg', 0.85);

      // Convert dataurl to File object
      fetch(this.photoDataUrl)
        .then(res => res.blob())
        .then(blob => {
          this.photoFile = new File([blob], 'captured_face.jpg', { type: 'image/jpeg' });
        });

      // Stop camera tracks
      if (video.srcObject) {
        video.srcObject.getTracks().forEach(track => track.stop());
      }
      this.isCameraOpen = false;
    },

    async submitAttendance() {
      if (!this.isWithinRadius) {
        window.showToast('Anda berada di luar area sekolah. Absensi tidak dapat dilakukan.', 'danger', 'Di Luar Radius');
        return;
      }

      if (!this.nama || !this.kelas_id || !this.jurusan_id) {
        window.showToast('Harap lengkapi Nama, Kelas, dan Jurusan Anda.', 'warning', 'Form Belum Lengkap');
        return;
      }

      if (!this.photoFile) {
        window.showToast('Foto bukti kehadiran wajib diunggah/diambil.', 'warning', 'Foto Wajib');
        return;
      }

      this.isSubmitting = true;

      const formData = new FormData();
      formData.append('nama', this.nama);
      formData.append('nis', this.nis);
      formData.append('kelas_id', this.kelas_id);
      formData.append('jurusan_id', this.jurusan_id);
      formData.append('latitude', this.userLat);
      formData.append('longitude', this.userLon);
      formData.append('foto', this.photoFile);

      try {
        const response = await fetch('/absensi-siswa/submit', {
          method: 'POST',
          body: formData
        });

        const result = await response.json();

        if (response.ok && result.success) {
          this.isSuccess = true;
          this.successData = result.data;
          
          // Trigger confetti animation if available
          if (window.confetti) {
            confetti({
              particleCount: 100,
              spread: 70,
              origin: { y: 0.6 }
            });
          }

          window.showToast('Absensi Anda Berhasil Tersimpan!', 'success', '✓ Sukses');
        } else {
          window.showToast(result.message || 'Gagal menyimpan absensi.', 'danger', '✗ Gagal');
        }
      } catch (err) {
        window.showToast('Terjadi kesalahan jaringan/server.', 'danger');
      } finally {
        this.isSubmitting = false;
      }
    }
  };
};

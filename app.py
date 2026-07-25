from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("  SISTEM ABSENSI SISWA BERBASIS GEOFENCING - SMKN 1 BANGKINANG")
    print("  Status: Server Active")
    print("  Access Admin: http://127.0.0.1:5000/login (admin / admin123)")
    print("  Access Siswa: http://127.0.0.1:5000/absensi-siswa")
    print("  Landing Page: http://127.0.0.1:5000/landing")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)

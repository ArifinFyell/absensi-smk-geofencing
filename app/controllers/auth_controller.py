from flask import render_template, request, redirect, url_for, flash, session
from app.models import db, User, Guru, ActivityLog

def login_view():
    if 'user_id' in session:
        role = session.get('user_role', 'guru')
        if role == 'admin':
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('guru.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_nama'] = user.nama or user.username
            session['user_role'] = user.role

            # Link guru profile to session if role=guru
            if user.role == 'guru':
                guru = Guru.query.filter_by(user_id=user.id).first()
                session['guru_id'] = guru.id if guru else None
                session['guru_nama'] = guru.nama if guru else (user.nama or user.username)

            db.session.add(ActivityLog(user=user.nama or user.username, aktivitas="Berhasil login ke sistem."))
            db.session.commit()

            flash(f'Selamat datang, {user.nama or user.username}!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user.role == 'admin':
                return redirect(url_for('dashboard.index'))
            return redirect(url_for('guru.dashboard'))
        else:
            flash('Username atau password yang Anda masukkan salah.', 'danger')

    return render_template('auth/login.html')

def logout_action():
    nama = session.get('user_nama', 'User')
    if 'user_id' in session:
        db.session.add(ActivityLog(user=nama, aktivitas="Logout dari sistem."))
        db.session.commit()

    session.clear()
    flash('Anda telah berhasil keluar dari sistem.', 'info')
    return redirect(url_for('auth.login'))

def change_password_action():
    """Allow guru to change their own password."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        password_lama = request.form.get('password_lama', '').strip()
        password_baru = request.form.get('password_baru', '').strip()
        konfirmasi = request.form.get('konfirmasi', '').strip()

        user = User.query.get(session['user_id'])
        if not user:
            flash('Sesi tidak valid. Silakan login kembali.', 'danger')
            return redirect(url_for('auth.login'))

        if not user.check_password(password_lama):
            flash('Password lama tidak sesuai.', 'danger')
            return redirect(url_for('guru.profil'))

        if len(password_baru) < 8:
            flash('Password baru minimal 8 karakter.', 'danger')
            return redirect(url_for('guru.profil'))

        if password_baru != konfirmasi:
            flash('Konfirmasi password tidak cocok.', 'danger')
            return redirect(url_for('guru.profil'))

        user.set_password(password_baru)
        db.session.add(ActivityLog(user=user.nama or user.username, aktivitas="Mengubah password akun."))
        db.session.commit()
        flash('Password berhasil diperbarui!', 'success')
        return redirect(url_for('guru.profil'))

    return redirect(url_for('guru.profil'))

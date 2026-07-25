import os
from flask import Flask, render_template, redirect, url_for, session, send_from_directory
from config import Config
from app.models import db, SettingSekolah

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder=os.path.join(Config.BASE_DIR, 'templates'),
                static_folder=os.path.join(Config.BASE_DIR, 'static'))
    
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Ensure database & uploads directories exist
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'absensi'), exist_ok=True)

    # Register Blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.siswa_routes import siswa_bp
    from app.routes.jadwal_routes import jadwal_bp
    from app.routes.absensi_routes import absensi_bp
    from app.routes.laporan_routes import laporan_bp
    from app.routes.setting_routes import setting_bp
    from app.routes.api_routes import api_bp
    from app.routes.guru_routes import guru_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(siswa_bp)
    app.register_blueprint(jadwal_bp)
    app.register_blueprint(absensi_bp)
    app.register_blueprint(laporan_bp)
    app.register_blueprint(setting_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(guru_bp)

    # Serve uploads static route
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Landing page route
    @app.route('/landing')
    def landing_page():
        sekolah = SettingSekolah.query.first()
        return render_template('landing.html', sekolah=sekolah)

    @app.route('/home')
    def home_redirect():
        if 'user_id' in session:
            role = session.get('user_role', 'guru')
            if role == 'admin':
                return redirect(url_for('dashboard.index'))
            return redirect(url_for('guru.dashboard'))
        return redirect(url_for('landing_page'))

    # Context Processors for Templates
    @app.context_processor
    def inject_global_settings():
        sekolah = SettingSekolah.query.first()
        return dict(sekolah_info=sekolah)

    # Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Auto Create DB & Seed Data inside App Context
    with app.app_context():
        db.create_all()
        from app.helpers.seed_helper import seed_initial_data
        try:
            seed_initial_data()
        except Exception as e:
            print(f"Seed note: {e}")

    return app

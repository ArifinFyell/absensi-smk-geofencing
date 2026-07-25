from datetime import datetime
from app.models.setting import SettingJam

HARI_MAP = {
    0: 'Senin',
    1: 'Selasa',
    2: 'Rabu',
    3: 'Kamis',
    4: 'Jumat',
    5: 'Sabtu',
    6: 'Minggu'
}

def get_current_hari():
    weekday = datetime.now().weekday()
    return HARI_MAP.get(weekday, 'Senin')

def get_current_time_str():
    return datetime.now().strftime('%H:%M')

def get_current_date_str():
    return datetime.now().strftime('%d %B %Y')

def calculate_attendance_status(jam_masuk_str=None):
    """
    Calculates attendance status: Hadir, Terlambat, or Terlambat Berat
    based on SettingJam bounds.
    """
    if not jam_masuk_str:
        jam_masuk_str = datetime.now().strftime('%H:%M')

    setting = SettingJam.query.first()
    jam_hadir_selesai = setting.jam_hadir_selesai if setting else '07:15'
    jam_terlambat_selesai = setting.jam_terlambat_selesai if setting else '07:30'

    if jam_masuk_str <= jam_hadir_selesai:
        return 'Hadir'
    elif jam_masuk_str <= jam_terlambat_selesai:
        return 'Terlambat'
    else:
        return 'Terlambat Berat'

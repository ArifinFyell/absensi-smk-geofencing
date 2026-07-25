// Realtime Polling Module for Command Center Dashboard

document.addEventListener('DOMContentLoaded', () => {
  const isDashboardPage = document.getElementById('command-center-dashboard');
  if (!isDashboardPage) return;

  function fetchRealtimeStats() {
    fetch('/api/stats')
      .then(res => res.json())
      .then(data => {
        // Update stat counters with animation
        updateCounter('stat-total-siswa', data.total_siswa);
        updateCounter('stat-hadir-count', data.hadir_count);
        updateCounter('stat-terlambat-count', data.terlambat_count);
        updateCounter('stat-belum-hadir-count', data.belum_hadir_count);
        updateCounter('stat-persentase-kehadiran', data.persentase_kehadiran + '%');
        updateCounter('stat-total-absen-count', data.total_absen_count);

        // Update recent activity feed stream
        const feedContainer = document.getElementById('live-activity-stream');
        if (feedContainer && data.recent_absensi) {
          let html = '';
          if (data.recent_absensi.length === 0) {
            html = `<div class="text-center py-6 text-slate-400 text-sm">Belum ada aktivitas absensi hari ini.</div>`;
          } else {
            data.recent_absensi.forEach(item => {
              const badgeClass = item.status === 'Hadir' 
                ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20' 
                : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20';

              html += `
                <div class="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-all border border-slate-100 dark:border-slate-800">
                  <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-full bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 flex items-center justify-center font-bold text-xs">
                      ${item.nama.substring(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <div class="font-semibold text-sm text-slate-800 dark:text-slate-200">${item.nama}</div>
                      <div class="text-xs text-slate-500 dark:text-slate-400">${item.kelas} • ${item.mata_pelajaran}</div>
                    </div>
                  </div>
                  <div class="text-right">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${badgeClass}">
                      ${item.jam_masuk} • ${item.status}
                    </span>
                  </div>
                </div>
              `;
            });
          }
          feedContainer.innerHTML = html;
        }

        // Update charts if global chart instances exist
        if (window.attendancePieChart && data) {
          window.attendancePieChart.data.datasets[0].data = [data.hadir_count, data.terlambat_count, data.belum_hadir_count, data.izin_count + data.sakit_count];
          window.attendancePieChart.update('none');
        }
      })
      .catch(err => console.log('Polling stats err:', err));
  }

  function updateCounter(elementId, newValue) {
    const el = document.getElementById(elementId);
    if (el && el.textContent !== String(newValue)) {
      el.classList.add('scale-105', 'text-blue-600');
      el.textContent = newValue;
      setTimeout(() => el.classList.remove('scale-105', 'text-blue-600'), 300);
    }
  }

  // Poll stats every 5 seconds
  setInterval(fetchRealtimeStats, 5000);
});

// Chart.js Configuration for Command Center Dashboard

document.addEventListener('DOMContentLoaded', () => {
  const pieCtx = document.getElementById('attendancePieChart');
  const barCtx = document.getElementById('classBarChart');

  if (pieCtx && window.Chart) {
    const hadir = parseInt(pieCtx.dataset.hadir || 0);
    const terlambat = parseInt(pieCtx.dataset.terlambat || 0);
    const belum = parseInt(pieCtx.dataset.belum || 0);

    window.attendancePieChart = new Chart(pieCtx, {
      type: 'doughnut',
      data: {
        labels: ['Hadir Tepat Waktu', 'Terlambat', 'Belum Hadir'],
        datasets: [{
          data: [hadir, terlambat, belum],
          backgroundColor: ['#22c55e', '#f59e0b', '#ef4444'],
          borderWidth: 0,
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              usePointStyle: true,
              padding: 16,
              font: { family: 'Inter', size: 12 }
            }
          }
        },
        cutout: '70%'
      }
    });
  }

  if (barCtx && window.Chart) {
    new Chart(barCtx, {
      type: 'bar',
      data: {
        labels: ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat'],
        datasets: [
          {
            label: 'Persentase Kehadiran (%)',
            data: [96.5, 94.1, 97.8, 95.2, 98.0],
            backgroundColor: '#2563eb',
            borderRadius: 8
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            grid: { color: 'rgba(226, 232, 240, 0.5)' }
          },
          x: {
            grid: { display: false }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
});

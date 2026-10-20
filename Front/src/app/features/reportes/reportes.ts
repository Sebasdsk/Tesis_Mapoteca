import { Component, inject, signal, OnInit, OnDestroy, ElementRef, viewChild } from '@angular/core';
import { DatePipe } from '@angular/common';
import { firstValueFrom } from 'rxjs';
import Chart from 'chart.js/auto';
import { ReporteService } from '../../core/service/reporte';
import {
  ReporteGeneral,
  CartaEstadistica,
  PrestamoVencido,
  PrestamoActivo,
  DistribucionUsuarios,
  ActividadMensual,
} from '../../core/models/reporte';

@Component({
  selector: 'app-reportes',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './reportes.html',
  styleUrl: './reportes.css',
})
export default class ReportesComponent implements OnInit, OnDestroy {
  private reporteService = inject(ReporteService);

  isLoading = signal(true);
  errorMessage = signal('');

  resumen = signal<ReporteGeneral | null>(null);
  masBuscadas = signal<CartaEstadistica[]>([]);
  masPrestadas = signal<CartaEstadistica[]>([]);
  vencidos = signal<PrestamoVencido[]>([]);
  prestadosActivos = signal<PrestamoActivo[]>([]);
  distribucion = signal<DistribucionUsuarios[]>([]);
  actividad = signal<ActividadMensual[]>([]);

  // Canvas refs
  barCanvas = viewChild<ElementRef>('barChart');
  donutCanvas = viewChild<ElementRef>('donutChart');
  lineCanvas = viewChild<ElementRef>('lineChart');

  private barChartInstance: Chart | null = null;
  private donutChartInstance: Chart | null = null;
  private lineChartInstance: Chart | null = null;

  ngOnInit() {
    this.loadData();
  }

  ngOnDestroy() {
    this.barChartInstance?.destroy();
    this.donutChartInstance?.destroy();
    this.lineChartInstance?.destroy();
  }

  loadData() {
    this.isLoading.set(true);
    this.errorMessage.set('');

    Promise.all([
      firstValueFrom(this.reporteService.getReporteGeneral()),
      firstValueFrom(this.reporteService.getCartasMasBuscadas(5)),
      firstValueFrom(this.reporteService.getCartasMasPrestadas(5)),
      firstValueFrom(this.reporteService.getPrestamosVencidos()),
      firstValueFrom(this.reporteService.getPrestamosActivos()),
      firstValueFrom(this.reporteService.getDistribucionUsuarios()),
      firstValueFrom(this.reporteService.getActividadMensual(12)),
    ])
      .then(([resumenRes, buscadasRes, prestadasRes, vencidosRes, activosRes, distRes, actRes]) => {
        this.resumen.set(resumenRes || null);
        this.masBuscadas.set(buscadasRes || []);
        this.masPrestadas.set(prestadasRes || []);
        this.vencidos.set(vencidosRes || []);
        this.prestadosActivos.set(activosRes || []);
        this.distribucion.set(distRes || []);
        this.actividad.set(actRes || []);
        // Render charts after a tick so canvas elements exist
        setTimeout(() => this.renderCharts(), 100);
      })
      .catch((err) => {
        this.errorMessage.set(
          err.error?.detail || 'Error al cargar los reportes. Verifica tu conexion.'
        );
      })
      .finally(() => {
        this.isLoading.set(false);
      });
  }

  private renderCharts() {
    this.renderBarChart();
    this.renderDonutChart();
    this.renderLineChart();
  }

  private renderBarChart() {
    const canvas = this.barCanvas();
    if (!canvas) return;
    if (this.barChartInstance) this.barChartInstance.destroy();

    const data = this.masPrestadas();
    this.barChartInstance = new Chart(canvas.nativeElement, {
      type: 'bar',
      data: {
        labels: data.map(d => d.nomenclatura),
        datasets: [{
          label: 'Prestamos',
          data: data.map(d => d.cantidad),
          backgroundColor: 'rgba(0, 51, 102, 0.8)',
          borderColor: '#003366',
          borderWidth: 1,
          borderRadius: 6,
          barThickness: 40,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: (items: any) => {
                const idx = items[0].dataIndex;
                return data[idx]?.nombre || '';
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1, font: { family: 'Inter' } },
            grid: { color: '#f1f5f9' },
          },
          x: {
            ticks: { font: { family: 'Inter', size: 11 } },
            grid: { display: false },
          },
        },
      },
    });
  }

  private renderDonutChart() {
    const canvas = this.donutCanvas();
    if (!canvas) return;
    if (this.donutChartInstance) this.donutChartInstance.destroy();

    const data = this.distribucion();
    const colors = ['#003366', '#f59e0b', '#64748b', '#10b981'];
    const labels_map: Record<string, string> = {
      ADMIN: 'Administradores',
      ESTUDIANTE: 'Estudiantes',
      MAESTRO: 'Maestros',
      EXTERNO: 'Externos',
    };

    this.donutChartInstance = new Chart(canvas.nativeElement, {
      type: 'doughnut',
      data: {
        labels: data.map(d => labels_map[d.tipo_usuario] || d.tipo_usuario),
        datasets: [{
          data: data.map(d => d.cantidad),
          backgroundColor: colors.slice(0, data.length),
          borderWidth: 2,
          borderColor: '#ffffff',
          hoverOffset: 8,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '60%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 16,
              font: { family: 'Inter', size: 12 },
              usePointStyle: true,
              pointStyleWidth: 10,
            },
          },
        },
      },
    });
  }

  private renderLineChart() {
    const canvas = this.lineCanvas();
    if (!canvas) return;
    if (this.lineChartInstance) this.lineChartInstance.destroy();

    const data = this.actividad();
    const meses_map: Record<string, string> = {
      '01': 'Ene', '02': 'Feb', '03': 'Mar', '04': 'Abr',
      '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Ago',
      '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic',
    };

    this.lineChartInstance = new Chart(canvas.nativeElement, {
      type: 'line',
      data: {
        labels: data.map(d => {
          const parts = d.mes.split('-');
          return meses_map[parts[1]] || parts[1];
        }),
        datasets: [{
          label: 'Prestamos',
          data: data.map(d => d.cantidad),
          borderColor: '#003366',
          backgroundColor: 'rgba(0, 51, 102, 0.1)',
          borderWidth: 2.5,
          pointBackgroundColor: '#003366',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: 5,
          pointHoverRadius: 7,
          fill: true,
          tension: 0.35,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1, font: { family: 'Inter' } },
            grid: { color: '#f1f5f9' },
          },
          x: {
            ticks: { font: { family: 'Inter', size: 11 } },
            grid: { display: false },
          },
        },
      },
    });
  }
}

import { Component, inject, signal } from '@angular/core';
import { NgClass } from '@angular/common';
import { RouterLink } from '@angular/router';
import { CartaService } from '../../../core/service/carta';
import { ToastService } from '../../../core/service/toast';

interface ResultRow {
  fila: number;
  nomenclatura: string;
  nombre: string;
  exito: boolean;
  mensaje: string;
}

interface CargaResult {
  total_procesadas: number;
  exitosas: number;
  errores: number;
  detalle: ResultRow[];
}

@Component({
  selector: 'app-carga-masiva',
  standalone: true,
  imports: [NgClass, RouterLink],
  templateUrl: './carga-masiva.html',
  styleUrl: './carga-masiva.css',
})
export default class CargaMasivaComponent {
  private cartaService = inject(CartaService);
  private toast = inject(ToastService);

  selectedFile = signal<File | null>(null);
  isDragging = signal(false);
  isUploading = signal(false);
  result = signal<CargaResult | null>(null);
  errorMessage = signal('');

  onDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(true);
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(false);
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging.set(false);
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.handleFile(files[0]);
    }
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.handleFile(input.files[0]);
    }
  }

  private handleFile(file: File) {
    if (!file.name.endsWith('.csv')) {
      this.errorMessage.set('Por favor selecciona un archivo CSV (.csv)');
      return;
    }
    this.selectedFile.set(file);
    this.errorMessage.set('');
    this.result.set(null);
  }

  removeFile() {
    this.selectedFile.set(null);
    this.result.set(null);
    this.errorMessage.set('');
  }

  uploadFile() {
    const file = this.selectedFile();
    if (!file) return;

    this.isUploading.set(true);
    this.errorMessage.set('');

    this.cartaService.cargaMasiva(file).subscribe({
      next: (res: CargaResult) => {
        this.result.set(res);
        this.isUploading.set(false);
        if (res.exitosas > 0) {
          const extra = res.errores > 0 ? `, ${res.errores} con error` : '';
          this.toast.success(`${res.exitosas} carta(s) cargada(s)${extra}`);
        } else {
          this.toast.error('No se pudo cargar ninguna carta. Revisa el detalle.');
        }
      },
      error: (err) => {
        this.errorMessage.set(
          err.error?.detail || 'Error al procesar el archivo. Verifica el formato e intenta de nuevo.'
        );
        this.isUploading.set(false);
      },
    });
  }

  downloadTemplate() {
    const headers = 'nomenclatura,nombre,escala,tipo_carta,estado_republica,zona_utm,elipsoide,proyeccion_cartografica,coordenadas_utm_x,coordenadas_utm_y,coordenadas_latitud,coordenadas_longitud,limites_detalle,disponibilidad,fecha_edicion,notas';
    const example1 = 'G13C56,Culiacan Rosales,1:50,000,TOPOGRAFICA,Sinaloa,13,CLARKE DE 1866,Transversa de Mercator,,,24° 48´,107° 23´,,FISICA,1983-01-01,Carta en buen estado';
    const example2 = 'E13B26,Nombre Carta,1:50,000,GEOLOGICA,"Durango, Sinaloa",13,GRS80,Transversa de Mercator,2794000,702000,,,,FISICA,1980-01-01,';
    const csv = [headers, example1, example2].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'plantilla_cartas_mapoteca.csv';
    a.click();
    URL.revokeObjectURL(url);
  }

  formatFileSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }
}

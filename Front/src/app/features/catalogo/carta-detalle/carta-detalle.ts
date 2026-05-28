import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { NgClass } from '@angular/common';
import { CartaService } from '../../../core/service/carta';
import { PrestamoService } from '../../../core/service/prestamo';
import { AuthService } from '../../../core/service/auth';
import { Carta } from '../../../core/models/carta';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';
import * as L from 'leaflet';

@Component({
  selector: 'app-carta-detalle',
  standalone: true,
  imports: [RouterLink, NgClass, FormsModule],
  templateUrl: './carta-detalle.html',
  styleUrl: './carta-detalle.css',
})
export default class CartaDetalleComponent implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private cartaService = inject(CartaService);
  private prestamoService = inject(PrestamoService);
  private http = inject(HttpClient);
  authService = inject(AuthService);

  carta = signal<Carta | null>(null);
  isLoading = signal(true);
  errorMessage = signal('');

  private map: L.Map | null = null;

  // Baja modal
  showBajaModal = signal(false);
  bajaMotivo = 'PERDIDA';
  bajaDescripcion = '';
  bajaLoading = signal(false);

  // Confirm delete
  showDeleteConfirm = signal(false);

  // Solicitar préstamo
  showPrestamoModal = signal(false);
  prestamoNotas = '';
  prestamoLoading = signal(false);
  prestamoSuccess = signal('');
  prestamoError = signal('');

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.router.navigate(['/catalogo']);
      return;
    }
    this.loadCarta(id);
  }

  ngOnDestroy() {
    this.destroyMap();
  }

  private destroyMap() {
    if (this.map) {
      this.map.remove();
      this.map = null;
    }
  }

  parseDMSToDecimal(dmsStr: string | null | undefined, isLongitude = false): number | null {
    if (!dmsStr) return null;
    const clean = dmsStr.trim();
    // Regex para grados, minutos y segundos opcionales (ej: "25° 15´", "25°15'", "109° 00´")
    const dmsRegex = /(\d+)\s*°\s*(\d+)\s*[´']?\s*(\d+)?/;
    const match = clean.match(dmsRegex);
    if (match) {
      const deg = parseFloat(match[1]);
      const min = parseFloat(match[2]) || 0;
      const sec = parseFloat(match[3]) || 0;
      let decimal = deg + (min / 60) + (sec / 3600);
      if (isLongitude && decimal > 0) {
        decimal = -decimal;
      }
      return decimal;
    }
    const num = Number(clean.replace(/,/g, ''));
    if (!isNaN(num)) {
      if (isLongitude && num > 0) {
        return -num;
      }
      return num;
    }
    return null;
  }

  private initMap(carta: Carta) {
    this.destroyMap();

    let lat: number | null = null;
    let lng: number | null = null;

    if (carta.tipo_coordenadas === 'LIMITES' || (!carta.coordenadas_latitud && carta.limites_norte)) {
      const norte = Number(carta.limites_norte);
      const sur = Number(carta.limites_sur);
      const este = Number(carta.limites_este);
      const oeste = Number(carta.limites_oeste);
      if (norte && sur && este && oeste) {
        lat = (norte + sur) / 2;
        lng = (este + oeste) / 2;
      }
    } else {
      lat = this.parseDMSToDecimal(carta.coordenadas_latitud, false);
      lng = this.parseDMSToDecimal(carta.coordenadas_longitud, true);
    }

    // Si no se cuenta con coordenadas válidas, no se genera el visor
    if (lat === null || lng === null) {
      return;
    }

    setTimeout(() => {
      const mapEl = document.getElementById('map-detail');
      if (!mapEl) return;

      // Configuración de los iconos por defecto desde CDN para evitar problemas de rutas de bundle
      const iconDefault = L.icon({
        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
      });
      L.Marker.prototype.options.icon = iconDefault;

      this.map = L.map('map-detail', {
        center: [lat!, lng!],
        zoom: 11,
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contribuyentes'
      }).addTo(this.map);

      L.marker([lat!, lng!]).addTo(this.map)
        .bindPopup(`<b>${carta.nombre}</b><br>${carta.nomenclatura}`)
        .openPopup();
    }, 50);
  }

  openBajaModal() { this.showBajaModal.set(true); }
  closeBajaModal() { this.showBajaModal.set(false); }

  submitBaja() {
    const carta = this.carta();
    if (!carta) return;
    this.bajaLoading.set(true);
    this.http.post(`${environment.apiUrl}/cartas/${carta.id}/baja`, {
      motivo: this.bajaMotivo,
      descripcion: this.bajaDescripcion || undefined,
    }).subscribe({
      next: () => {
        this.bajaLoading.set(false);
        this.showBajaModal.set(false);
        this.loadCarta(carta.id);
      },
      error: (err) => {
        this.bajaLoading.set(false);
        this.errorMessage.set(err.error?.detail || 'Error al dar de baja');
      },
    });
  }

  deleteCarta() {
    const carta = this.carta();
    if (!carta) return;
    this.cartaService.deleteCarta(carta.id).subscribe({
      next: () => this.router.navigate(['/catalogo']),
      error: (err) => this.errorMessage.set(err.error?.detail || 'Error al eliminar'),
    });
  }

  getDisponibilidadClass(d: string): string {
    switch (d) {
      case 'FISICA': case 'AMBAS': return 'badge-disponible';
      case 'SOLO_DIGITAL': return 'badge-digital';
      case 'EXTRAVIADA': case 'DANADA': return 'badge-no-disponible';
      default: return 'badge-default';
    }
  }

  getDisponibilidadLabel(d: string): string {
    const map: Record<string, string> = {
      FISICA: 'Física', SOLO_DIGITAL: 'Solo Digital', AMBAS: 'Física + Digital',
      EXTRAVIADA: 'Extraviada', DANADA: 'Dañada',
    };
    return map[d] || d;
  }

  getTipoLabel(t: string): string {
    const map: Record<string, string> = {
      TOPOGRAFICA: 'Topográfica', GEOLOGICA: 'Geológica', HIDROLOGICA: 'Hidrológica',
      EDAFOLOGICA: 'Edafológica', USO_SUELO: 'Uso de Suelo', CLIMATICA: 'Climática', OTRA: 'Otra',
    };
    return map[t] || t;
  }

  // --- Solicitar Préstamo ---

  openPrestamoModal() {
    this.prestamoNotas = '';
    this.prestamoError.set('');
    this.showPrestamoModal.set(true);
  }

  closePrestamoModal() {
    this.showPrestamoModal.set(false);
  }

  submitPrestamo() {
    const carta = this.carta();
    if (!carta) return;
    this.prestamoLoading.set(true);
    this.prestamoError.set('');

    this.prestamoService.solicitarPrestamo({
      carta_id: carta.id,
      notas_solicitud: this.prestamoNotas || undefined,
    }).subscribe({
      next: () => {
        this.prestamoLoading.set(false);
        this.showPrestamoModal.set(false);
        this.prestamoSuccess.set('¡Solicitud enviada! El administrador revisará tu petición.');
        setTimeout(() => this.prestamoSuccess.set(''), 5000);
      },
      error: (err) => {
        this.prestamoLoading.set(false);
        this.prestamoError.set(err.error?.detail || 'Error al solicitar préstamo');
      },
    });
  }

  canRequestLoan(): boolean {
    const carta = this.carta();
    if (!carta) return false;
    return carta.disponibilidad === 'FISICA' || carta.disponibilidad === 'AMBAS';
  }

  private loadCarta(id: string) {
    this.isLoading.set(true);
    this.cartaService.getCarta(id).subscribe({
      next: (data) => {
        this.carta.set(data);
        this.isLoading.set(false);
        this.initMap(data);
      },
      error: () => {
        this.errorMessage.set('No se pudo cargar la carta.');
        this.isLoading.set(false);
      },
    });
  }
}

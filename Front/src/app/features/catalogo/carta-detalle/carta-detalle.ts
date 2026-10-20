import { Component, inject, signal, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { NgClass, DatePipe } from '@angular/common';
import { CartaService } from '../../../core/service/carta';
import { PrestamoService } from '../../../core/service/prestamo';
import { AuthService } from '../../../core/service/auth';
import { ToastService } from '../../../core/service/toast';
import { UsuarioService, UsuarioLookup } from '../../../core/service/usuario';
import { Carta } from '../../../core/models/carta';
import { parseCoordinate } from '../../../core/utils/coordinates';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';
import * as L from 'leaflet';

@Component({
  selector: 'app-carta-detalle',
  standalone: true,
  imports: [RouterLink, NgClass, FormsModule, DatePipe],
  templateUrl: './carta-detalle.html',
  styleUrl: './carta-detalle.css',
})
export default class CartaDetalleComponent implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private cartaService = inject(CartaService);
  private prestamoService = inject(PrestamoService);
  private http = inject(HttpClient);
  private usuarioService = inject(UsuarioService);
  authService = inject(AuthService);
  private toast = inject(ToastService);

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

  // Préstamo directo (ADMIN/MAESTRO)
  showDirectoModal = signal(false);
  directoFecha = '';
  directoNotas = '';
  directoLoading = signal(false);
  directoError = signal('');
  userSearch = '';
  userResults = signal<UsuarioLookup[]>([]);
  selectedUser = signal<UsuarioLookup | null>(null);

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

  async copiarClaveInegi(): Promise<void> {
    const clave = this.carta()?.nomenclatura;
    if (!clave) return;
    try {
      await navigator.clipboard.writeText(clave);
      this.toast.success('Clave INEGI copiada');
    } catch {
      this.toast.info(`No se pudo copiar automáticamente. La clave es: ${clave}`);
    }
  }

  private getBounds(carta: Carta): L.LatLngBounds | null {
    const toNumber = (valor: number | string | null | undefined): number => {
      if (valor === null || valor === undefined || valor === '') return NaN;
      return Number(valor);
    };

    const norte = toNumber(carta.limites_norte);
    const sur = toNumber(carta.limites_sur);
    const este = toNumber(carta.limites_este);
    const oeste = toNumber(carta.limites_oeste);

    if (![norte, sur, este, oeste].every((v) => Number.isFinite(v))) return null;

    const latNorte = Math.max(norte, sur);
    const latSur = Math.min(norte, sur);
    const lngEste = Math.max(este, oeste);
    const lngOeste = Math.min(este, oeste);

    const limitesValidos =
      latNorte > latSur &&
      lngEste > lngOeste &&
      latSur >= -90 &&
      latNorte <= 90 &&
      lngOeste >= -180 &&
      lngEste <= 180;

    if (!limitesValidos) return null;

    return L.latLngBounds([latSur, lngOeste], [latNorte, lngEste]);
  }

  private escapeHtml(texto: string): string {
    const mapa: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;',
    };
    return texto.replace(/[&<>"']/g, (c) => mapa[c]);
  }

  private initMap(carta: Carta) {
    this.destroyMap();

    const lat = parseCoordinate(carta.coordenadas_latitud, 'lat');
    const lng = parseCoordinate(carta.coordenadas_longitud, 'lng');
    const bounds = this.getBounds(carta);

    // Si no se cuenta con coordenadas válidas, no se genera el visor
    if (!bounds && (lat === null || lng === null)) {
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

      const centro: L.LatLngTuple = bounds
        ? [bounds.getCenter().lat, bounds.getCenter().lng]
        : [lat!, lng!];

      this.map = L.map('map-detail', {
        center: centro,
        zoom: 12,
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contribuyentes'
      }).addTo(this.map);

      const popup = `<b>${this.escapeHtml(carta.nombre)}</b><br>${this.escapeHtml(carta.nomenclatura)}`;

      // Los límites dibujan el área real de la carta (mapa preciso).
      if (bounds) {
        L.rectangle(bounds, {
          color: '#0f766e',
          weight: 2,
          fillColor: '#0f766e',
          fillOpacity: 0.08,
        }).addTo(this.map).bindPopup(popup);
        this.map.fitBounds(bounds, { padding: [20, 20] });
      }

      if (lat !== null && lng !== null) {
        L.marker([lat, lng]).addTo(this.map).bindPopup(popup).openPopup();
        if (!bounds) {
          this.map.setView([lat, lng], 12);
        }
      }
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
        this.toast.success('Solicitud de préstamo enviada');
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

  // --- Préstamo directo (ADMIN/MAESTRO) ---

  openDirectoModal() {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    this.directoFecha = d.toISOString().split('T')[0];
    this.directoNotas = '';
    this.directoError.set('');
    this.userSearch = '';
    this.userResults.set([]);
    this.selectedUser.set(null);
    this.showDirectoModal.set(true);
  }

  closeDirectoModal() {
    this.showDirectoModal.set(false);
  }

  onUserSearchInput(term: string) {
    this.userSearch = term;
    this.selectedUser.set(null);
    if (term.trim().length < 2) {
      this.userResults.set([]);
      return;
    }
    this.usuarioService.lookup(term).subscribe({
      next: (results) => this.userResults.set(results),
      error: () => this.userResults.set([]),
    });
  }

  selectUser(user: UsuarioLookup) {
    this.selectedUser.set(user);
    this.userResults.set([]);
    this.userSearch = user.nombre_completo;
  }

  submitDirecto() {
    const carta = this.carta();
    const user = this.selectedUser();
    if (!carta || !user || !this.directoFecha) return;

    this.directoLoading.set(true);
    this.directoError.set('');

    this.prestamoService
      .registrarPrestamoDirecto({
        usuario_id: user.id,
        carta_id: carta.id,
        fecha_limite: this.directoFecha,
        notas_admin: this.directoNotas || undefined,
      })
      .subscribe({
        next: () => {
          this.directoLoading.set(false);
          this.showDirectoModal.set(false);
          this.toast.success('Préstamo registrado: la carta queda ocupada');
        },
        error: (err) => {
          this.directoLoading.set(false);
          this.directoError.set(err.error?.detail || 'Error al registrar el préstamo');
        },
      });
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

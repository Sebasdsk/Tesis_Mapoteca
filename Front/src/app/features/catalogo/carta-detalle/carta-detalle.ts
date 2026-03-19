import { Component, inject, signal, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { NgClass } from '@angular/common';
import { CartaService } from '../../../core/service/carta';
import { AuthService } from '../../../core/service/auth';
import { Carta } from '../../../core/models/carta';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-carta-detalle',
  standalone: true,
  imports: [RouterLink, NgClass, FormsModule],
  templateUrl: './carta-detalle.html',
  styleUrl: './carta-detalle.css',
})
export default class CartaDetalleComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private cartaService = inject(CartaService);
  private http = inject(HttpClient);
  authService = inject(AuthService);

  carta = signal<Carta | null>(null);
  isLoading = signal(true);
  errorMessage = signal('');

  // Baja modal
  showBajaModal = signal(false);
  bajaMotivo = 'PERDIDA';
  bajaDescripcion = '';
  bajaLoading = signal(false);

  // Confirm delete
  showDeleteConfirm = signal(false);

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.router.navigate(['/catalogo']);
      return;
    }
    this.loadCarta(id);
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

  private loadCarta(id: string) {
    this.isLoading.set(true);
    this.cartaService.getCarta(id).subscribe({
      next: (data) => { this.carta.set(data); this.isLoading.set(false); },
      error: () => { this.errorMessage.set('No se pudo cargar la carta.'); this.isLoading.set(false); },
    });
  }
}

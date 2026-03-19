import { Component, inject, signal, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CartaService } from '../../../core/service/carta';
import { Carta } from '../../../core/models/carta';

@Component({
  selector: 'app-carta-form',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './carta-form.html',
  styleUrl: './carta-form.css',
})
export default class CartaFormComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private cartaService = inject(CartaService);

  isEditing = signal(false);
  isLoading = signal(false);
  isSaving = signal(false);
  errorMessage = signal('');
  successMessage = signal('');

  editId = '';

  formData: any = {
    nomenclatura: '',
    nombre: '',
    escala: '1:50,000',
    tipo_carta: 'TOPOGRAFICA',
    elipsoide: '',
    zona_utm: '',
    tipo_coordenadas: '',
    limites_norte: null,
    limites_sur: null,
    limites_este: null,
    limites_oeste: null,
    fecha_edicion: '',
    estado_republica: '',
    disponibilidad: 'FISICA',
    url_inegi: '',
    notas: '',
  };

  tiposCarta = [
    { value: 'TOPOGRAFICA', label: 'Topográfica' },
    { value: 'GEOLOGICA', label: 'Geológica' },
    { value: 'HIDROLOGICA', label: 'Hidrológica' },
    { value: 'EDAFOLOGICA', label: 'Edafológica' },
    { value: 'USO_SUELO', label: 'Uso de Suelo' },
    { value: 'CLIMATICA', label: 'Climática' },
    { value: 'OTRA', label: 'Otra' },
  ];

  disponibilidades = [
    { value: 'FISICA', label: 'Física' },
    { value: 'SOLO_DIGITAL', label: 'Solo Digital' },
    { value: 'AMBAS', label: 'Física + Digital' },
    { value: 'EXTRAVIADA', label: 'Extraviada' },
    { value: 'DANADA', label: 'Dañada' },
  ];

  tiposCoordenadas = [
    { value: 'GEOGRAFICAS', label: 'Geográficas' },
    { value: 'UTM', label: 'UTM' },
    { value: 'AMBAS', label: 'Ambas' },
  ];

  escalas = ['1:50,000', '1:250,000', '1:1,000,000'];

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEditing.set(true);
      this.editId = id;
      this.loadCarta(id);
    }
  }

  submit() {
    this.isSaving.set(true);
    this.errorMessage.set('');
    this.successMessage.set('');

    // Limpiar campos vacíos
    const data = this.cleanFormData();

    if (this.isEditing()) {
      this.cartaService.updateCarta(this.editId, data).subscribe({
        next: () => {
          this.isSaving.set(false);
          this.router.navigate(['/catalogo', this.editId]);
        },
        error: (err) => {
          this.isSaving.set(false);
          this.errorMessage.set(err.error?.detail || 'Error al actualizar la carta');
        },
      });
    } else {
      this.cartaService.createCarta(data).subscribe({
        next: (created) => {
          this.isSaving.set(false);
          this.router.navigate(['/catalogo', created.id]);
        },
        error: (err) => {
          this.isSaving.set(false);
          this.errorMessage.set(err.error?.detail || 'Error al crear la carta');
        },
      });
    }
  }

  private loadCarta(id: string) {
    this.isLoading.set(true);
    this.cartaService.getCarta(id).subscribe({
      next: (carta) => {
        this.formData = {
          nomenclatura: carta.nomenclatura || '',
          nombre: carta.nombre || '',
          escala: carta.escala || '1:50,000',
          tipo_carta: carta.tipo_carta || 'TOPOGRAFICA',
          elipsoide: carta.elipsoide || '',
          zona_utm: carta.zona_utm || '',
          tipo_coordenadas: carta.tipo_coordenadas || '',
          limites_norte: carta.limites_norte,
          limites_sur: carta.limites_sur,
          limites_este: carta.limites_este,
          limites_oeste: carta.limites_oeste,
          fecha_edicion: carta.fecha_edicion || '',
          estado_republica: carta.estado_republica || '',
          disponibilidad: carta.disponibilidad || 'FISICA',
          url_inegi: carta.url_inegi || '',
          notas: carta.notas || '',
        };
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('No se pudo cargar la carta.');
        this.isLoading.set(false);
      },
    });
  }

  private cleanFormData(): any {
    const d: any = { ...this.formData };
    // Remover campos vacíos para no enviar strings vacíos al backend
    Object.keys(d).forEach((key) => {
      if (d[key] === '' || d[key] === null || d[key] === undefined) {
        delete d[key];
      }
    });
    // Siempre enviar campos requeridos
    d.nomenclatura = this.formData.nomenclatura;
    d.nombre = this.formData.nombre;
    d.escala = this.formData.escala;
    d.tipo_carta = this.formData.tipo_carta;
    return d;
  }
}

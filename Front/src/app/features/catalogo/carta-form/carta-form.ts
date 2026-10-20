import { Component, inject, signal, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CartaService } from '../../../core/service/carta';
import { ToastService } from '../../../core/service/toast';
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
  private toast = inject(ToastService);

  isEditing = signal(false);
  isLoading = signal(false);
  isSaving = signal(false);
  errorMessage = signal('');
  successMessage = signal('');

  editId = '';

  edicionModo: 'anio' | 'fecha' = 'anio';

  formData: any = {
    nomenclatura: '',
    nombre: '',
    escala: '1:50,000',
    tipo_carta: 'TOPOGRAFICA',
    elipsoide: 'CLARKE DE 1866',
    zona_utm: '',
    tipo_coordenadas: 'LIMITES',
    proyeccion_cartografica: 'TRANSEVERSA DE MERCATOR',
    coordenadas_utm_x: '',
    coordenadas_utm_y: '',
    coordenadas_latitud: '',
    coordenadas_longitud: '',
    limites_detalle: '',
    limites_norte: null,
    limites_sur: null,
    limites_este: null,
    limites_oeste: null,
    anio_edicion: null,
    fecha_edicion: '',
    estado_republica: '',
    disponibilidad: 'FISICA',
    unidades_total: 1,
    url_inegi: '',
    notes: '',
    notas: '',
  };

  selectedEstados: string[] = ['', '', '', ''];

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
    { value: 'LIMITES', label: 'Límites Geográficos' },
    { value: 'UTM', label: 'Coordenadas UTM' },
    { value: 'GEODESICO', label: 'Coordenadas Geodésicas' },
    { value: 'AMBAS', label: 'Ambas (UTM y Geodésicas)' },
  ];

  elipsoides = ['CLARKE DE 1866', 'GRS80', 'WGS84', 'S/N'];

  estadosMexico = [
    'Aguascalientes', 'Baja California', 'Baja California Sur', 'Campeche', 'Chiapas', 'Chihuahua',
    'Ciudad de México', 'Coahuila', 'Colima', 'Durango', 'Guanajuato', 'Guerrero', 'Hidalgo',
    'Jalisco', 'México', 'Michoacán', 'Morelos', 'Nayarit', 'Nuevo León', 'Oaxaca', 'Puebla',
    'Querétaro', 'Quintana Roo', 'San Luis Potosí', 'Sinaloa', 'Sonora', 'Tabasco', 'Tamaulipas',
    'Tlaxcala', 'Veracruz', 'Yucatán', 'Zacatecas', 'Nacional', 'S/N'
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

    if (this.edicionModo === 'anio' && this.formData.anio_edicion) {
      const anio = Number(this.formData.anio_edicion);
      if (!Number.isInteger(anio) || anio < 1500 || anio > 2100) {
        this.isSaving.set(false);
        this.errorMessage.set('El año de edición debe ser un número entre 1500 y 2100.');
        return;
      }
    }

    // Combinar estados seleccionados
    const activeEstados = this.selectedEstados.filter(s => !!s);
    this.formData.estado_republica = activeEstados.length > 0 ? activeEstados.join(', ') : '';

    // Limpiar campos vacíos
    const data = this.cleanFormData();

    if (this.isEditing()) {
      this.cartaService.updateCarta(this.editId, data).subscribe({
        next: () => {
          this.isSaving.set(false);
          this.toast.success('Carta actualizada correctamente');
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
          this.toast.success('Carta registrada correctamente');
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
      next: (carta: any) => {
        // Detectar tipo de coordenadas si no viene definido
        let tipoCoord = carta.tipo_coordenadas;
        if (!tipoCoord) {
          if (carta.coordenadas_utm_x && carta.coordenadas_latitud) {
            tipoCoord = 'AMBAS';
          } else if (carta.coordenadas_utm_x) {
            tipoCoord = 'UTM';
          } else if (carta.coordenadas_latitud) {
            tipoCoord = 'GEODESICO';
          } else {
            tipoCoord = 'LIMITES';
          }
        }

        // Cargar estados
        const states = carta.estado_republica
          ? carta.estado_republica.split(/,\s*/).map((s: string) => s.trim())
          : [];
        this.selectedEstados = ['', '', '', ''];
        for (let i = 0; i < 4; i++) {
          this.selectedEstados[i] = states[i] || '';
        }

        this.edicionModo = carta.fecha_edicion ? 'fecha' : 'anio';

        this.formData = {
          nomenclatura: carta.nomenclatura || '',
          nombre: carta.nombre || '',
          escala: carta.escala || '1:50,000',
          tipo_carta: carta.tipo_carta || 'TOPOGRAFICA',
          elipsoide: carta.elipsoide || 'CLARKE DE 1866',
          zona_utm: carta.zona_utm || '',
          tipo_coordenadas: tipoCoord,
          proyeccion_cartografica: carta.proyeccion_cartografica || 'TRANSEVERSA DE MERCATOR',
          coordenadas_utm_x: carta.coordenadas_utm_x || '',
          coordenadas_utm_y: carta.coordenadas_utm_y || '',
          coordenadas_latitud: carta.coordenadas_latitud || '',
          coordenadas_longitud: carta.coordenadas_longitud || '',
          limites_detalle: carta.limites_detalle || '',
          limites_norte: carta.limites_norte,
          limites_sur: carta.limites_sur,
          limites_este: carta.limites_este,
          limites_oeste: carta.limites_oeste,
          anio_edicion: carta.anio_edicion ?? null,
          fecha_edicion: carta.fecha_edicion || '',
          estado_republica: carta.estado_republica || '',
          disponibilidad: carta.disponibilidad || 'FISICA',
          unidades_total: carta.unidades_total ?? 1,
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

    // Según el tipo de coordenadas, eliminar los campos del otro tipo para evitar conflictos
    if (this.formData.tipo_coordenadas === 'LIMITES') {
      delete d.coordenadas_utm_x;
      delete d.coordenadas_utm_y;
      delete d.coordenadas_latitud;
      delete d.coordenadas_longitud;
      delete d.limites_detalle;
    } else if (this.formData.tipo_coordenadas === 'UTM') {
      delete d.coordenadas_latitud;
      delete d.coordenadas_longitud;
      delete d.limites_norte;
      delete d.limites_sur;
      delete d.limites_este;
      delete d.limites_oeste;
    } else if (this.formData.tipo_coordenadas === 'GEODESICO') {
      delete d.coordenadas_utm_x;
      delete d.coordenadas_utm_y;
      delete d.zona_utm;
      delete d.limites_norte;
      delete d.limites_sur;
      delete d.limites_este;
      delete d.limites_oeste;
    } else if (this.formData.tipo_coordenadas === 'AMBAS') {
      delete d.limites_norte;
      delete d.limites_sur;
      delete d.limites_este;
      delete d.limites_oeste;
    }

    // Siempre enviar campos requeridos
    d.nomenclatura = this.formData.nomenclatura;
    d.nombre = this.formData.nombre;
    d.escala = this.formData.escala;
    d.tipo_carta = this.formData.tipo_carta;
    d.unidades_total = Number(this.formData.unidades_total) || 1;

    // Edición: solo año o fecha completa. Se envían ambos campos explícitamente
    // (aunque uno sea null) para limpiar el que no corresponde al modo elegido.
    if (this.edicionModo === 'anio') {
      const raw = this.formData.anio_edicion;
      const anio = raw === null || raw === '' ? NaN : Number(raw);
      d.anio_edicion = Number.isInteger(anio) ? anio : null;
      d.fecha_edicion = null;
    } else {
      d.fecha_edicion = this.formData.fecha_edicion || null;
      d.anio_edicion = null;
    }
    return d;
  }
}

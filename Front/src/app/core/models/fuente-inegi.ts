import { TipoCarta } from './carta';

export type EstadoEnlaceInegi = 'sin_verificar' | 'valido' | 'no_responde';

export interface FuenteInegiDatos {
  escala: string;
  tipo_carta: TipoCarta;
  nombre: string;
  url: string;
}

export interface FuenteInegi extends FuenteInegiDatos {
  id: string;
  estado_enlace: EstadoEnlaceInegi;
  fecha_verificacion: string | null;
  created_at: string;
  updated_at: string;
}

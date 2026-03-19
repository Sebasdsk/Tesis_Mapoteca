/**
 * Tipos de carta
 */
export type TipoCarta =
  | 'TOPOGRAFICA'
  | 'GEOLOGICA'
  | 'HIDROLOGICA'
  | 'EDAFOLOGICA'
  | 'USO_SUELO'
  | 'CLIMATICA'
  | 'OTRA';

/**
 * Estados de disponibilidad
 */
export type Disponibilidad =
  | 'FISICA'
  | 'SOLO_DIGITAL'
  | 'AMBAS'
  | 'EXTRAVIADA'
  | 'DANADA';

/**
 * Tipo de coordenadas
 */
export type TipoCoordenadas = 'ALTOMETRICO' | 'GEODESICO';

/**
 * Metadata de INEGI almacenada en JSONB
 */
export interface MetadataInegi {
  año_digital?: number;
  formatos_disponibles?: string[];
  escala_digital?: string;
  fecha_actualizacion?: string;
}

/**
 * Modelo completo de Carta (respuesta del backend)
 */
export interface Carta {
  id: string;
  nomenclatura: string;
  nombre: string;
  escala: string;
  tipo_carta: TipoCarta;
  elipsoide: string | null;
  zona_utm: string | null;
  tipo_coordenadas: TipoCoordenadas | null;
  limites_norte: number | null;
  limites_sur: number | null;
  limites_este: number | null;
  limites_oeste: number | null;
  fecha_edicion: string | null;
  estado_republica: string | null;
  disponibilidad: Disponibilidad;
  url_inegi: string | null;
  metadata_inegi: MetadataInegi | null;
  notas: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Versión simplificada para listas
 */
export interface CartaSimple {
  id: string;
  nomenclatura: string;
  nombre: string;
  escala: string;
  tipo_carta: TipoCarta;
  estado_republica: string | null;
  disponibilidad: Disponibilidad;
}

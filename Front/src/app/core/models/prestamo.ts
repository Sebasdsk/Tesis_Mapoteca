/**
 * Estados posibles de un préstamo
 */
export type EstadoPrestamo =
  | 'SOLICITADO'
  | 'APROBADO'
  | 'RECHAZADO'
  | 'ENTREGADO'
  | 'DEVUELTO'
  | 'VENCIDO';

/**
 * Evaluación del estado físico al devolver
 */
export type EvaluacionEstado = 'BUENO' | 'REGULAR' | 'MALO';

/**
 * Carta simplificada embebida en respuestas de préstamo
 */
export interface CartaEnPrestamo {
  id: string;
  nomenclatura: string;
  nombre: string;
  escala: string;
}

/**
 * Usuario simplificado embebido en respuestas de préstamo
 */
export interface UsuarioEnPrestamo {
  id: string;
  nombre_completo: string;
  tipo_usuario: string;
  numero_identificacion: string | null;
}

/**
 * Modelo completo de Préstamo (respuesta del backend)
 */
export interface Prestamo {
  id: string;
  estado: EstadoPrestamo;
  fecha_solicitud: string;
  fecha_aprobacion: string | null;
  fecha_entrega: string | null;
  fecha_devolucion: string | null;
  fecha_limite: string | null;
  evaluacion_estado: EvaluacionEstado | null;
  evaluacion_notas: string | null;
  notas_solicitud: string | null;
  notas_admin: string | null;
  motivo_rechazo: string | null;
  created_at: string;
  updated_at: string;
  usuario: UsuarioEnPrestamo;
  carta: CartaEnPrestamo;
}

/**
 * Request: Solicitar préstamo (CU-08)
 */
export interface PrestamoSolicitar {
  carta_id: string;
  notas_solicitud?: string;
}

/**
 * Request: Aprobar préstamo (CU-09)
 */
export interface PrestamoAprobar {
  fecha_limite: string; // YYYY-MM-DD
  notas_admin?: string;
}

/**
 * Request: Rechazar préstamo (CU-09)
 */
export interface PrestamoRechazar {
  motivo_rechazo: string;
}

/**
 * Request: Entregar préstamo (CU-09)
 */
export interface PrestamoEntregar {
  notas_admin?: string;
}

/**
 * Request: Devolver préstamo (CU-10)
 */
export interface PrestamoDevolver {
  evaluacion_estado: EvaluacionEstado;
  evaluacion_notas?: string;
}

/**
 * Filtros para listar préstamos
 */
export interface PrestamoFilters {
  estado?: EstadoPrestamo;
  usuario_id?: string;
  carta_id?: string;
  skip?: number;
  limit?: number;
}

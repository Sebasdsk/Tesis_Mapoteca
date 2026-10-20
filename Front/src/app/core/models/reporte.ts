export interface ReporteGeneral {
  total_usuarios: number;
  total_cartas: number;
  prestamos_activos: number;
  consultas_totales: number;
}

export interface CartaEstadistica {
  carta_id: string;
  nomenclatura: string;
  nombre: string;
  escala: string;
  cantidad: number;
}

export interface PrestamoVencido {
  prestamo_id: string;
  usuario_nombre: string;
  usuario_email: string | null;
  carta_nomenclatura: string;
  carta_nombre: string;
  fecha_solicitud: string;
  fecha_limite: string;
  dias_retraso: number;
}

export interface PrestamoActivo {
  prestamo_id: string;
  usuario_nombre: string;
  usuario_email: string | null;
  usuario_telefono: string | null;
  usuario_identificacion: string | null;
  carta_nomenclatura: string;
  carta_nombre: string;
  fecha_entrega: string | null;
  fecha_limite: string | null;
  dias_retraso: number;
}

export interface DistribucionUsuarios {
  tipo_usuario: string;
  cantidad: number;
}

export interface ActividadMensual {
  mes: string;
  cantidad: number;
}


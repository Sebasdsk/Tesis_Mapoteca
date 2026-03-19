/**
 * Tipos de usuario del sistema
 */
export type TipoUsuario = 'ADMIN' | 'ESTUDIANTE' | 'MAESTRO' | 'EXTERNO';

/**
 * Request para login
 */
export interface LoginRequest {
  username: string;
  password: string;
}

/**
 * Información del usuario incluida en la respuesta del token
 */
export interface TokenUser {
  id: string;
  tipo_usuario: TipoUsuario;
  nombre_completo: string;
  email: string | null;
  debe_cambiar_password: boolean;
}

/**
 * Respuesta del endpoint /auth/login
 */
export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: TokenUser;
}

/**
 * Request para cambio de contraseña
 */
export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

/**
 * Respuesta del cambio de contraseña
 */
export interface PasswordChangeResponse {
  message: string;
  debe_cambiar_password: boolean;
}

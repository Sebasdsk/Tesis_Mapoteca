import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface Usuario {
  id: string;
  tipo_usuario: string;
  numero_identificacion: string | null;
  nombre_completo: string;
  email: string | null;
  institucion: string | null;
  activo: boolean;
  debe_cambiar_password: boolean;
  created_at: string;
  updated_at: string;
}

export interface UsuarioCreate {
  tipo_usuario: string;
  numero_identificacion?: string;
  nombre_completo: string;
  email?: string;
  institucion?: string;
}

export interface UsuarioUpdate {
  nombre_completo?: string;
  email?: string;
  activo?: boolean;
  institucion?: string;
}

export interface UsuarioCreateResponse extends Usuario {
  password_temporal: string;
}

export interface PasswordResetResponse {
  message: string;
  password_temporal: string;
}

export interface UsuarioFilters {
  tipo_usuario?: string;
  activo?: boolean;
  skip?: number;
  limit?: number;
}

@Injectable({ providedIn: 'root' })
export class UsuarioService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/usuarios`;

  getUsuarios(filters: UsuarioFilters = {}): Observable<Usuario[]> {
    let params = new HttpParams();
    if (filters.tipo_usuario) params = params.set('tipo_usuario', filters.tipo_usuario);
    if (filters.activo != null) params = params.set('activo', filters.activo.toString());
    if (filters.skip != null) params = params.set('skip', filters.skip.toString());
    if (filters.limit != null) params = params.set('limit', filters.limit.toString());
    return this.http.get<Usuario[]>(this.apiUrl, { params });
  }

  getUsuario(id: string): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.apiUrl}/${id}`);
  }

  createUsuario(data: UsuarioCreate): Observable<UsuarioCreateResponse> {
    return this.http.post<UsuarioCreateResponse>(this.apiUrl, data);
  }

  updateUsuario(id: string, data: UsuarioUpdate): Observable<Usuario> {
    return this.http.put<Usuario>(`${this.apiUrl}/${id}`, data);
  }

  deactivateUsuario(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }

  activateUsuario(id: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/${id}/activate`, {});
  }

  resetPassword(usuarioId: string): Observable<PasswordResetResponse> {
    return this.http.post<PasswordResetResponse>(`${this.apiUrl}/reset-password`, {
      usuario_id: usuarioId,
    });
  }
}

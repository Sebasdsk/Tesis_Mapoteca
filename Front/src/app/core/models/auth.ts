export type RolUsuario = 'Estudiante' | 'Profesor' | 'Externo' | 'Admin';


export interface User {
  id: string;
  Nombre: string;
  Apellido: string;
  email: string;
  rol: RolUsuario;
}

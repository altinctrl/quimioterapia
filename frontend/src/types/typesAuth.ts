export type UserRole = 'enfermeiro' | 'medico' | 'farmacia' | 'admin';

export interface User {
  id: string;
  nome: string;
  username: string;
  role: UserRole;
  grupo: string;
  email?: string;
  token?: string;
}

export type TipoUsuario = UserRole;
export type Usuario = User;

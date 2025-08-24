import { api } from './api';

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export async function register(email: string, password: string): Promise<AuthToken> {
  const res = await api.post('/auth/register', { email, password });
  return res.data;
}

export async function login(email: string, password: string): Promise<AuthToken> {
  const res = await api.post('/auth/login', { email, password });
  return res.data;
}

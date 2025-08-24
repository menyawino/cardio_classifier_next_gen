import axios from 'axios';

export interface AppliedRule {
  code: string;
  strength: string;
  description?: string;
}

export interface VariantResponse {
  id?: number;
  hgvs?: string;
  genome_build?: string;
  classification: string;
  applied_rules: AppliedRule[];
  rationale: string;
}

export const api = axios.create({ baseURL: '/api' });

export function setAuthToken(token: string | null) {
  if(token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
}

export async function classifyVariant(hgvs: string): Promise<VariantResponse> {
  const res = await api.post('/variants/classify', { hgvs });
  return res.data;
}

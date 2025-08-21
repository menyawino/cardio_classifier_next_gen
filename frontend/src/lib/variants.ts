import axios from 'axios';

export interface StoredVariant {
  id: number;
  hgvs: string;
  genome_build: string;
  classification: string;
  applied_rules?: any[];
  rationale?: string;
}

export interface ClassificationEvent {
  id: number;
  classification: string;
  evidence: any[];
  created_at: string;
  user_id: number | null;
}

export async function listVariants(): Promise<StoredVariant[]> {
  const res = await axios.get('/api/variants');
  return res.data;
}

export async function getVariantHistory(id: number): Promise<ClassificationEvent[]> {
  const res = await axios.get(`/api/variants/${id}/history`);
  return res.data;
}

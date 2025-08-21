import axios from 'axios';

export interface VariantResponse {
  classification: string;
  applied_rules: any[];
  rationale: string;
}

export async function classifyVariant(hgvs: string): Promise<VariantResponse> {
  const res = await axios.post('/api/variants/classify', { hgvs });
  return res.data;
}

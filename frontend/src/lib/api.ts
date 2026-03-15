const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface TaricSuggestion {
  code: string;
  description: string;
  confidence: number;
  reasoning: string;
  duty_rate: string | null;
  chapter: string;
  section: string;
}

export interface ClassifyResponse {
  product_description: string;
  suggestions: TaricSuggestion[];
  top_code: string;
  top_confidence: number;
  notes: string | null;
  source: string;
}

export interface ClassifyRequest {
  description: string;
  origin_country?: string;
  additional_context?: string;
}

export async function classifyProduct(
  request: ClassifyRequest
): Promise<ClassifyResponse> {
  const res = await fetch(`${API_BASE}/api/v1/classify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: "Error desconocido" }));
    throw new Error(error.detail || error.error || `Error ${res.status}`);
  }

  return res.json();
}

export async function checkHealth(): Promise<{
  status: string;
  anthropic_configured: boolean;
  pinecone_configured: boolean;
}> {
  const res = await fetch(`${API_BASE}/api/v1/health`);
  return res.json();
}

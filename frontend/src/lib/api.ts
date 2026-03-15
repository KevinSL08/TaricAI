import { createClient, isSupabaseConfigured } from "@/lib/supabase";

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

async function getAuthHeaders(): Promise<Record<string, string>> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (isSupabaseConfigured()) {
    try {
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (session?.access_token) {
        headers["Authorization"] = `Bearer ${session.access_token}`;
      }
    } catch {
      // No auth available, continue without token
    }
  }

  return headers;
}

export async function classifyProduct(
  request: ClassifyRequest
): Promise<ClassifyResponse> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/v1/classify`, {
    method: "POST",
    headers,
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: "Error desconocido" }));
    throw new Error(error.detail || error.error || `Error ${res.status}`);
  }

  return res.json();
}

// --- Duty Calculator ---

export interface DutyCalculationRequest {
  commodity_code: string;
  origin_country?: string;
  customs_value_eur: number;
  weight_kg?: number;
  iva_type?: string;
}

export interface DutyMeasureInfo {
  measure_type: string;
  duty_expression: string;
  geographical_area: string;
}

export interface DutyCalculationResponse {
  commodity_code: string;
  commodity_description: string;
  origin_country: string | null;
  customs_value_eur: number;
  duty_rate: string;
  duty_amount_eur: number;
  iva_type: string;
  iva_rate_pct: number;
  iva_base_eur: number;
  iva_amount_eur: number;
  total_import_cost_eur: number;
  applicable_measure: DutyMeasureInfo;
  all_measures: DutyMeasureInfo[];
  source: string;
  notes: string | null;
}

export async function calculateDuties(
  request: DutyCalculationRequest
): Promise<DutyCalculationResponse> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_BASE}/api/v1/calculate-duties`, {
    method: "POST",
    headers,
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

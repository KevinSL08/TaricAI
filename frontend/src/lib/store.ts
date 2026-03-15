import { type ClassifyResponse } from "./api";

export interface HistoryEntry {
  id: string;
  timestamp: string;
  description: string;
  origin_country?: string;
  result: ClassifyResponse;
}

const STORAGE_KEY = "taricai_history";

export function getHistory(): HistoryEntry[] {
  if (typeof window === "undefined") return [];
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

export function addToHistory(
  description: string,
  origin_country: string | undefined,
  result: ClassifyResponse
): HistoryEntry {
  const entry: HistoryEntry = {
    id: crypto.randomUUID(),
    timestamp: new Date().toISOString(),
    description,
    origin_country,
    result,
  };
  const history = getHistory();
  history.unshift(entry);
  // Keep last 100 entries
  const trimmed = history.slice(0, 100);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
  return entry;
}

export function clearHistory(): void {
  localStorage.removeItem(STORAGE_KEY);
}

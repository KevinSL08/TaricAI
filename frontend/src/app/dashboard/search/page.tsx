"use client";

import { useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Search, Loader2, Copy, Check } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface SearchResult {
  code: string;
  description: string;
  score: number;
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  async function handleSearch() {
    if (!query.trim() || query.trim().length < 2) return;
    setLoading(true);
    setError(null);
    setSearched(true);

    try {
      const res = await fetch(
        `${API_BASE}/api/v1/search?q=${encodeURIComponent(query.trim())}&top_k=20`
      );
      if (!res.ok) throw new Error(`Error ${res.status}`);
      const data = await res.json();
      setResults(data.results || data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Error al buscar. Verifica que el backend este activo."
      );
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  function copyCode(code: string) {
    navigator.clipboard.writeText(code);
    setCopied(code);
    setTimeout(() => setCopied(null), 2000);
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Buscar TARIC</h1>
        <p className="text-muted-foreground mt-1">
          Busqueda semantica en la nomenclatura combinada TARIC (16,457 codigos)
        </p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search
                size={16}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
              />
              <Input
                placeholder="Buscar por descripcion: cafe, textil, electronica..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                className="pl-9"
              />
            </div>
            <Button
              onClick={handleSearch}
              disabled={loading || query.trim().length < 2}
            >
              {loading ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                "Buscar"
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-700 text-sm">{error}</p>
          </CardContent>
        </Card>
      )}

      {searched && !loading && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">
              {results.length} resultado{results.length !== 1 ? "s" : ""}
            </CardTitle>
            <CardDescription>
              Codigos TARIC ordenados por relevancia semantica
            </CardDescription>
          </CardHeader>
          <CardContent>
            {results.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Search size={40} className="mx-auto mb-3 opacity-50" />
                <p>No se encontraron codigos para esa busqueda.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {results.map((r, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-3 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center gap-4 min-w-0">
                      <span className="text-xs text-muted-foreground w-6">
                        {i + 1}
                      </span>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <code className="font-mono font-semibold text-sm">
                            {r.code}
                          </code>
                          <button
                            onClick={() => copyCode(r.code)}
                            className="p-1 hover:bg-muted rounded"
                          >
                            {copied === r.code ? (
                              <Check size={14} />
                            ) : (
                              <Copy size={14} />
                            )}
                          </button>
                        </div>
                        <p className="text-sm text-muted-foreground truncate">
                          {r.description}
                        </p>
                      </div>
                    </div>
                    <Badge variant="outline" className="ml-3 shrink-0">
                      {Math.round(r.score * 100)}%
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

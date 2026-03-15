"use client";

import { useEffect, useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Trash2, Search, Copy, Check, PackageSearch } from "lucide-react";
import { getHistory, clearHistory, type HistoryEntry } from "@/lib/store";

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [search, setSearch] = useState("");
  const [copied, setCopied] = useState<string | null>(null);
  const [selectedEntry, setSelectedEntry] = useState<HistoryEntry | null>(null);

  useEffect(() => {
    setHistory(getHistory());
  }, []);

  const filtered = search.trim()
    ? history.filter(
        (h) =>
          h.description.toLowerCase().includes(search.toLowerCase()) ||
          h.result.top_code.includes(search)
      )
    : history;

  function handleClear() {
    if (confirm("Estas seguro de que quieres borrar todo el historial?")) {
      clearHistory();
      setHistory([]);
      setSelectedEntry(null);
    }
  }

  function copyCode(code: string) {
    navigator.clipboard.writeText(code);
    setCopied(code);
    setTimeout(() => setCopied(null), 2000);
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Historial</h1>
          <p className="text-muted-foreground mt-1">
            {history.length} clasificacion{history.length !== 1 ? "es" : ""}{" "}
            realizadas
          </p>
        </div>
        {history.length > 0 && (
          <Button variant="outline" size="sm" onClick={handleClear}>
            <Trash2 size={16} className="mr-2" />
            Limpiar historial
          </Button>
        )}
      </div>

      {history.length > 0 && (
        <div className="relative">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            placeholder="Buscar por descripcion o codigo..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
      )}

      <div className="grid lg:grid-cols-[1fr_400px] gap-6">
        {/* List */}
        <Card>
          <CardContent className="pt-6">
            {filtered.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <PackageSearch size={40} className="mx-auto mb-3 opacity-50" />
                <p>
                  {history.length === 0
                    ? "No hay clasificaciones aun."
                    : "No se encontraron resultados."}
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {filtered.map((entry) => (
                  <div
                    key={entry.id}
                    onClick={() => setSelectedEntry(entry)}
                    className={`flex items-center justify-between p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedEntry?.id === entry.id
                        ? "border-blue-300 bg-blue-50"
                        : "border-border hover:bg-muted/50"
                    }`}
                  >
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium truncate">
                        {entry.description}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(entry.timestamp).toLocaleString("es-ES")}
                        {entry.origin_country &&
                          ` · ${entry.origin_country}`}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 ml-3 shrink-0">
                      <code className="text-xs font-mono bg-muted px-2 py-1 rounded">
                        {entry.result.top_code}
                      </code>
                      <Badge variant="secondary" className="text-xs">
                        {Math.round(entry.result.top_confidence * 100)}%
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Detail panel */}
        <div className="hidden lg:block">
          {selectedEntry ? (
            <Card className="sticky top-8">
              <CardHeader>
                <CardTitle className="text-lg">Detalle</CardTitle>
                <CardDescription className="truncate">
                  {selectedEntry.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">
                    Codigo TARIC
                  </p>
                  <div className="flex items-center gap-2">
                    <code className="text-2xl font-mono font-bold">
                      {selectedEntry.result.top_code}
                    </code>
                    <button
                      onClick={() =>
                        copyCode(selectedEntry.result.top_code)
                      }
                      className="p-1.5 hover:bg-muted rounded"
                    >
                      {copied === selectedEntry.result.top_code ? (
                        <Check size={16} />
                      ) : (
                        <Copy size={16} />
                      )}
                    </button>
                  </div>
                </div>

                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">
                    Confianza
                  </p>
                  <Badge>
                    {Math.round(selectedEntry.result.top_confidence * 100)}%
                  </Badge>
                </div>

                {selectedEntry.result.suggestions.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-muted-foreground mb-2">
                      Sugerencias ({selectedEntry.result.suggestions.length})
                    </p>
                    <div className="space-y-2">
                      {selectedEntry.result.suggestions.map((s, i) => (
                        <div
                          key={i}
                          className="p-2 border border-border rounded text-sm"
                        >
                          <div className="flex items-center justify-between">
                            <code className="font-mono text-xs">{s.code}</code>
                            <span className="text-xs text-muted-foreground">
                              {Math.round(s.confidence * 100)}%
                            </span>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                            {s.description}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">
                    Fecha
                  </p>
                  <p className="text-sm">
                    {new Date(selectedEntry.timestamp).toLocaleString("es-ES")}
                  </p>
                </div>

                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-1">
                    Fuente
                  </p>
                  <p className="text-sm">{selectedEntry.result.source}</p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-8 text-muted-foreground">
                  <p className="text-sm">
                    Selecciona una clasificacion para ver los detalles
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

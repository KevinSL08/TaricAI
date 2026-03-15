"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, Search, ChevronDown, ChevronUp } from "lucide-react";
import { classifyProduct, type ClassifyResponse } from "@/lib/api";

const examples = [
  "Cafe tostado en grano arabica de Colombia",
  "Camiseta de algodon para hombre talla M",
  "Aceite de oliva virgen extra 5 litros",
  "Smartphone Samsung Galaxy 128GB",
  "Vino tinto Rioja reserva 2019",
];

export function ClassifierDemo() {
  const [description, setDescription] = useState("");
  const [country, setCountry] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ClassifyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  async function handleClassify() {
    if (!description.trim() || description.trim().length < 5) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await classifyProduct({
        description: description.trim(),
        origin_country: country.trim() || undefined,
      });
      setResult(res);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error al clasificar. Verifica que el backend este activo."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section id="demo" className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            Prueba la clasificacion en vivo
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Describe un producto y obtendras su codigo TARIC en segundos.
          </p>
        </div>

        <Card className="p-6 sm:p-8">
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-1.5 block">
                Descripcion del producto
              </label>
              <Textarea
                placeholder="Ej: Cafe tostado en grano arabica de Colombia"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                className="resize-none"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-foreground mb-1.5 block">
                Pais de origen (opcional)
              </label>
              <Input
                placeholder="Ej: CO, CN, US, DE"
                value={country}
                onChange={(e) => setCountry(e.target.value.toUpperCase().slice(0, 2))}
                maxLength={2}
                className="max-w-[120px]"
              />
            </div>

            <Button
              onClick={handleClassify}
              disabled={loading || description.trim().length < 5}
              className="w-full sm:w-auto"
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 size={18} className="mr-2 animate-spin" />
                  Clasificando...
                </>
              ) : (
                <>
                  <Search size={18} className="mr-2" />
                  Clasificar
                </>
              )}
            </Button>

            <div className="flex flex-wrap gap-2 pt-2">
              <span className="text-xs text-muted-foreground">Ejemplos:</span>
              {examples.map((ex) => (
                <button
                  key={ex}
                  onClick={() => setDescription(ex)}
                  className="text-xs text-blue-600 hover:text-blue-800 hover:underline"
                >
                  {ex}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {result && (
            <div className="mt-6 space-y-4">
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div>
                    <p className="text-sm text-green-700 font-medium">
                      Codigo TARIC recomendado
                    </p>
                    <p className="text-2xl font-mono font-bold text-green-900 mt-1">
                      {result.top_code}
                    </p>
                  </div>
                  <Badge
                    variant={
                      result.top_confidence >= 0.8
                        ? "default"
                        : result.top_confidence >= 0.6
                        ? "secondary"
                        : "outline"
                    }
                    className="text-sm"
                  >
                    {Math.round(result.top_confidence * 100)}% confianza
                  </Badge>
                </div>
              </div>

              {result.suggestions.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-foreground">
                    {result.suggestions.length} sugerencia
                    {result.suggestions.length > 1 ? "s" : ""}
                  </p>
                  {result.suggestions.map((s, i) => (
                    <div
                      key={i}
                      className="border border-border rounded-lg p-4"
                    >
                      <div
                        className="flex items-center justify-between cursor-pointer"
                        onClick={() => setExpanded(expanded === i ? null : i)}
                      >
                        <div className="flex items-center gap-3">
                          <span className="font-mono font-semibold text-sm">
                            {s.code}
                          </span>
                          <span className="text-sm text-muted-foreground truncate max-w-[300px]">
                            {s.description}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground">
                            {Math.round(s.confidence * 100)}%
                          </span>
                          {expanded === i ? (
                            <ChevronUp size={16} />
                          ) : (
                            <ChevronDown size={16} />
                          )}
                        </div>
                      </div>
                      {expanded === i && (
                        <div className="mt-3 pt-3 border-t border-border text-sm space-y-2">
                          <p>
                            <span className="font-medium">Razonamiento:</span>{" "}
                            <span className="text-muted-foreground">
                              {s.reasoning}
                            </span>
                          </p>
                          {s.duty_rate && (
                            <p>
                              <span className="font-medium">Arancel:</span>{" "}
                              <span className="text-muted-foreground">
                                {s.duty_rate}
                              </span>
                            </p>
                          )}
                          <p>
                            <span className="font-medium">Capitulo:</span>{" "}
                            <span className="text-muted-foreground">
                              {s.chapter}
                            </span>{" "}
                            | <span className="font-medium">Seccion:</span>{" "}
                            <span className="text-muted-foreground">
                              {s.section}
                            </span>
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              <p className="text-xs text-muted-foreground text-right">
                Fuente: {result.source}
              </p>
            </div>
          )}
        </Card>
      </div>
    </section>
  );
}

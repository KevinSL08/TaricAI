"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Loader2,
  PackageSearch,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Calculator,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { classifyProduct, type ClassifyResponse } from "@/lib/api";
import { addToHistory } from "@/lib/store";

export default function ClassifyPage() {
  const [description, setDescription] = useState("");
  const [country, setCountry] = useState("");
  const [context, setContext] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ClassifyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  async function handleClassify() {
    if (!description.trim() || description.trim().length < 5) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await classifyProduct({
        description: description.trim(),
        origin_country: country.trim() || undefined,
        additional_context: context.trim() || undefined,
      });
      setResult(res);
      addToHistory(description.trim(), country.trim() || undefined, res);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Error al clasificar. Verifica que el backend este activo."
      );
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
        <h1 className="text-2xl font-bold text-foreground">
          Clasificar producto
        </h1>
        <p className="text-muted-foreground mt-1">
          Describe un producto para obtener su codigo TARIC de 10 digitos
        </p>
      </div>

      <Card>
        <CardContent className="pt-6 space-y-4">
          <div>
            <label className="text-sm font-medium text-foreground mb-1.5 block">
              Descripcion del producto *
            </label>
            <Textarea
              placeholder="Describe el producto con el mayor detalle posible: material, uso, composicion, presentacion..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              className="resize-none"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Minimo 5 caracteres. Cuanto mas detallada la descripcion, mejor la
              clasificacion.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-foreground mb-1.5 block">
                Pais de origen
              </label>
              <Input
                placeholder="Ej: CO, CN, US, DE"
                value={country}
                onChange={(e) =>
                  setCountry(e.target.value.toUpperCase().slice(0, 2))
                }
                maxLength={2}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Codigo ISO de 2 letras (opcional)
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-foreground mb-1.5 block">
                Contexto adicional
              </label>
              <Input
                placeholder="Ej: para uso industrial, para consumo humano"
                value={context}
                onChange={(e) => setContext(e.target.value)}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Informacion extra que ayude a la clasificacion
              </p>
            </div>
          </div>

          <Button
            onClick={handleClassify}
            disabled={loading || description.trim().length < 5}
            size="lg"
            className="w-full sm:w-auto"
          >
            {loading ? (
              <>
                <Loader2 size={18} className="mr-2 animate-spin" />
                Clasificando...
              </>
            ) : (
              <>
                <PackageSearch size={18} className="mr-2" />
                Clasificar
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-red-200 dark:border-red-900/50 bg-red-50 dark:bg-red-950/30">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertCircle size={20} className="text-red-600 dark:text-red-400 mt-0.5 shrink-0" />
              <div className="flex-1">
                <p className="font-medium text-red-800 dark:text-red-300">
                  Error al clasificar
                </p>
                <p className="text-sm text-red-700 dark:text-red-400 mt-1">{error}</p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleClassify}
                  className="mt-3"
                  disabled={loading}
                >
                  <RefreshCw size={14} className="mr-1.5" />
                  Reintentar
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {result && (
        <div className="space-y-4">
          {/* Top result */}
          <Card className="border-green-200 dark:border-green-900/50 bg-green-50 dark:bg-green-950/30">
            <CardContent className="pt-6">
              <div className="flex items-start justify-between flex-wrap gap-4">
                <div>
                  <p className="text-sm font-medium text-green-700 dark:text-green-400">
                    Codigo TARIC recomendado
                  </p>
                  <div className="flex items-center gap-3 mt-2">
                    <p className="text-3xl font-mono font-bold text-green-900 dark:text-green-200">
                      {result.top_code}
                    </p>
                    <button
                      onClick={() => copyCode(result.top_code)}
                      className="p-1.5 hover:bg-green-200 dark:hover:bg-green-800/50 rounded transition-colors"
                      title="Copiar codigo"
                    >
                      {copied === result.top_code ? (
                        <Check size={18} className="text-green-700 dark:text-green-400" />
                      ) : (
                        <Copy size={18} className="text-green-700 dark:text-green-400" />
                      )}
                    </button>
                  </div>
                </div>
                <Badge
                  variant={
                    result.top_confidence >= 0.8
                      ? "default"
                      : result.top_confidence >= 0.6
                      ? "secondary"
                      : "outline"
                  }
                  className="text-base px-4 py-1"
                >
                  {Math.round(result.top_confidence * 100)}% confianza
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* All suggestions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">
                {result.suggestions.length} sugerencia
                {result.suggestions.length > 1 ? "s" : ""}
              </CardTitle>
              <CardDescription>
                Ordenadas por nivel de confianza
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {result.suggestions.map((s, i) => (
                <div
                  key={i}
                  className="border border-border rounded-lg overflow-hidden"
                >
                  <div
                    className="flex items-center justify-between p-4 cursor-pointer hover:bg-muted/50 transition-colors"
                    onClick={() => setExpanded(expanded === i ? null : i)}
                  >
                    <div className="flex items-center gap-4 min-w-0">
                      <span className="text-sm font-medium text-muted-foreground w-6">
                        #{i + 1}
                      </span>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <code className="font-mono font-semibold">
                            {s.code}
                          </code>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              copyCode(s.code);
                            }}
                            className="p-1 hover:bg-muted rounded"
                          >
                            {copied === s.code ? (
                              <Check size={14} />
                            ) : (
                              <Copy size={14} />
                            )}
                          </button>
                        </div>
                        <p className="text-sm text-muted-foreground truncate max-w-md">
                          {s.description}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 ml-4 shrink-0">
                      <Badge variant="outline">
                        {Math.round(s.confidence * 100)}%
                      </Badge>
                      {expanded === i ? (
                        <ChevronUp size={16} />
                      ) : (
                        <ChevronDown size={16} />
                      )}
                    </div>
                  </div>

                  {expanded === i && (
                    <div className="px-4 pb-4 pt-0 border-t border-border bg-muted/30">
                      <div className="pt-4 space-y-3 text-sm">
                        <div>
                          <span className="font-medium">Razonamiento:</span>
                          <p className="text-muted-foreground mt-1">
                            {s.reasoning}
                          </p>
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                          {s.duty_rate && (
                            <div>
                              <span className="font-medium">Arancel:</span>
                              <p className="text-muted-foreground">
                                {s.duty_rate}
                              </p>
                            </div>
                          )}
                          <div>
                            <span className="font-medium">Capitulo:</span>
                            <p className="text-muted-foreground">{s.chapter}</p>
                          </div>
                          <div>
                            <span className="font-medium">Seccion:</span>
                            <p className="text-muted-foreground">{s.section}</p>
                          </div>
                        </div>
                        <div className="pt-2">
                          <Button
                            variant="outline"
                            size="sm"
                            render={
                              <Link
                                href={`/dashboard/aranceles?code=${s.code}${
                                  country ? `&origin=${country}` : ""
                                }`}
                              />
                            }
                          >
                            <Calculator size={14} className="mr-1.5" />
                            Calcular aranceles
                          </Button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>

          {result.notes && (
            <Card className="border-amber-200 dark:border-amber-900/50 bg-amber-50 dark:bg-amber-950/30">
              <CardContent className="pt-6">
                <p className="text-sm text-amber-800 dark:text-amber-300">
                  <span className="font-medium">Nota:</span> {result.notes}
                </p>
              </CardContent>
            </Card>
          )}

          <p className="text-xs text-muted-foreground text-right">
            Fuente: {result.source}
          </p>
        </div>
      )}
    </div>
  );
}

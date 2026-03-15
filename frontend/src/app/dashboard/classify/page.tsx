"use client";

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "motion/react";
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
  Send,
  Sparkles,
  CheckCircle,
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
      {/* Header */}
      <div className="space-y-1">
        <h2 className="text-[0.75rem] uppercase tracking-[0.4em] font-black text-cyan">
          CLASIFICADOR IA
        </h2>
        <p className="text-3xl font-black tracking-tighter">
          Clasificar Producto
        </p>
        <p className="text-sm text-on-surface/40 font-medium">
          Describe un producto para obtener su codigo TARIC de 10 digitos
        </p>
      </div>

      {/* Input Form */}
      <div className="bg-surface/30 backdrop-blur-md p-6 sm:p-8 rounded-[2rem] border border-outline-variant">
        <div className="space-y-4">
          <div>
            <label className="text-[10px] font-black text-cyan uppercase tracking-widest mb-2 block">
              Descripcion del producto *
            </label>
            <div className="relative">
              <textarea
                placeholder="Describe el producto con el mayor detalle posible: material, uso, composicion, presentacion..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                className="w-full bg-background/50 border border-outline-variant rounded-2xl py-4 px-6 text-sm focus:outline-none focus:border-cyan/50 transition-all resize-none placeholder:text-on-surface/30"
              />
            </div>
            <p className="text-[10px] text-on-surface/30 mt-1 font-medium">
              Minimo 5 caracteres. Cuanto mas detallada, mejor la clasificacion.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="text-[10px] font-black text-on-surface/50 uppercase tracking-widest mb-2 block">
                Pais de origen
              </label>
              <input
                placeholder="Ej: CO, CN, US, DE"
                value={country}
                onChange={(e) =>
                  setCountry(e.target.value.toUpperCase().slice(0, 2))
                }
                maxLength={2}
                className="w-full bg-background/50 border border-outline-variant rounded-xl py-3 px-4 text-sm focus:outline-none focus:border-cyan/50 transition-all placeholder:text-on-surface/30"
              />
            </div>
            <div>
              <label className="text-[10px] font-black text-on-surface/50 uppercase tracking-widest mb-2 block">
                Contexto adicional
              </label>
              <input
                placeholder="Ej: para uso industrial"
                value={context}
                onChange={(e) => setContext(e.target.value)}
                className="w-full bg-background/50 border border-outline-variant rounded-xl py-3 px-4 text-sm focus:outline-none focus:border-cyan/50 transition-all placeholder:text-on-surface/30"
              />
            </div>
          </div>

          <motion.button
            whileHover={{
              scale: 1.02,
              boxShadow: "0 0 20px rgba(0, 210, 255, 0.3)",
            }}
            whileTap={{ scale: 0.98 }}
            onClick={handleClassify}
            disabled={loading || description.trim().length < 5}
            className="kinetic-gradient text-[#0a0f14] font-black py-4 px-10 rounded-2xl flex items-center gap-3 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Clasificando...
              </>
            ) : (
              <>
                <Sparkles size={18} />
                Clasificar con IA
              </>
            )}
          </motion.button>
        </div>
      </div>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6"
          >
            <div className="flex items-start gap-3">
              <AlertCircle
                size={20}
                className="text-red-400 mt-0.5 shrink-0"
              />
              <div className="flex-1">
                <p className="font-bold text-red-300">Error al clasificar</p>
                <p className="text-sm text-red-400/80 mt-1">{error}</p>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  onClick={handleClassify}
                  disabled={loading}
                  className="mt-3 flex items-center gap-2 text-xs font-black text-red-400 uppercase tracking-widest hover:text-red-300 transition-colors"
                >
                  <RefreshCw size={14} />
                  Reintentar
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Result */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="space-y-4"
          >
            {/* Top result */}
            <div className="bg-cyan/5 border border-cyan/20 rounded-2xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-xs font-black uppercase tracking-widest text-green-400">
                  Clasificacion Exitosa
                </span>
              </div>

              <div className="flex items-start justify-between flex-wrap gap-4">
                <div>
                  <p className="text-[10px] font-black text-cyan uppercase tracking-widest mb-1">
                    Codigo TARIC
                  </p>
                  <div className="flex items-center gap-3">
                    <p className="text-3xl font-mono font-black text-cyan">
                      {result.top_code}
                    </p>
                    <button
                      onClick={() => copyCode(result.top_code)}
                      className="p-1.5 hover:bg-cyan/10 rounded-lg transition-colors"
                    >
                      {copied === result.top_code ? (
                        <Check size={18} className="text-green-400" />
                      ) : (
                        <Copy size={18} className="text-cyan/60" />
                      )}
                    </button>
                  </div>
                </div>
                <span
                  className={`text-sm font-black px-4 py-2 rounded-xl ${
                    result.top_confidence >= 0.8
                      ? "bg-green-400/10 text-green-400"
                      : result.top_confidence >= 0.6
                      ? "bg-orange/10 text-orange"
                      : "bg-red-400/10 text-red-400"
                  }`}
                >
                  {Math.round(result.top_confidence * 100)}% confianza
                </span>
              </div>
            </div>

            {/* All suggestions */}
            <div className="bg-surface/30 backdrop-blur-md p-6 sm:p-8 rounded-[2rem] border border-outline-variant">
              <div className="mb-6">
                <span className="text-[10px] font-black text-cyan uppercase tracking-[0.3em]">
                  SUGERENCIAS
                </span>
                <h3 className="text-xl font-black tracking-tight">
                  {result.suggestions.length} resultado
                  {result.suggestions.length > 1 ? "s" : ""}
                </h3>
              </div>

              <div className="space-y-3">
                {result.suggestions.map((s, i) => (
                  <div
                    key={i}
                    className="border border-outline-variant rounded-2xl overflow-hidden hover:border-cyan/30 transition-colors"
                  >
                    <div
                      className="flex items-center justify-between p-4 cursor-pointer hover:bg-surface-bright/30 transition-colors"
                      onClick={() => setExpanded(expanded === i ? null : i)}
                    >
                      <div className="flex items-center gap-4 min-w-0">
                        <span className="text-xs font-black text-on-surface/30 w-6">
                          #{i + 1}
                        </span>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2">
                            <code className="font-mono font-black text-cyan">
                              {s.code}
                            </code>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                copyCode(s.code);
                              }}
                              className="p-1 hover:bg-surface-bright rounded-lg"
                            >
                              {copied === s.code ? (
                                <Check size={14} className="text-green-400" />
                              ) : (
                                <Copy size={14} className="text-on-surface/30" />
                              )}
                            </button>
                          </div>
                          <p className="text-sm text-on-surface/50 truncate max-w-md">
                            {s.description}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 ml-4 shrink-0">
                        <span className="text-[10px] font-black px-2 py-1 rounded-lg bg-surface-bright border border-outline-variant">
                          {Math.round(s.confidence * 100)}%
                        </span>
                        {expanded === i ? (
                          <ChevronUp size={16} className="text-on-surface/30" />
                        ) : (
                          <ChevronDown
                            size={16}
                            className="text-on-surface/30"
                          />
                        )}
                      </div>
                    </div>

                    <AnimatePresence>
                      {expanded === i && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="border-t border-outline-variant bg-background/30"
                        >
                          <div className="p-4 space-y-3 text-sm">
                            <div>
                              <span className="text-[10px] font-black text-on-surface/40 uppercase tracking-widest">
                                Razonamiento
                              </span>
                              <p className="text-on-surface/60 mt-1">
                                {s.reasoning}
                              </p>
                            </div>
                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                              {s.duty_rate && (
                                <div className="p-3 bg-surface-bright/30 rounded-xl border border-outline-variant">
                                  <span className="text-[10px] font-black text-orange uppercase tracking-widest block mb-0.5">
                                    Arancel
                                  </span>
                                  <span className="font-bold">
                                    {s.duty_rate}
                                  </span>
                                </div>
                              )}
                              <div className="p-3 bg-surface-bright/30 rounded-xl border border-outline-variant">
                                <span className="text-[10px] font-black text-cyan uppercase tracking-widest block mb-0.5">
                                  Capitulo
                                </span>
                                <span className="font-bold">{s.chapter}</span>
                              </div>
                              <div className="p-3 bg-surface-bright/30 rounded-xl border border-outline-variant">
                                <span className="text-[10px] font-black text-cyan uppercase tracking-widest block mb-0.5">
                                  Seccion
                                </span>
                                <span className="font-bold">{s.section}</span>
                              </div>
                            </div>
                            <Link
                              href={`/dashboard/aranceles?code=${s.code}${
                                country ? `&origin=${country}` : ""
                              }`}
                            >
                              <motion.button
                                whileHover={{ scale: 1.05 }}
                                className="mt-2 flex items-center gap-2 text-xs font-black text-cyan uppercase tracking-widest"
                              >
                                <Calculator size={14} />
                                Calcular aranceles
                              </motion.button>
                            </Link>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                ))}
              </div>
            </div>

            {result.notes && (
              <div className="bg-orange/5 border border-orange/20 rounded-2xl p-6">
                <p className="text-sm text-orange/80">
                  <span className="font-black text-orange">Nota:</span>{" "}
                  {result.notes}
                </p>
              </div>
            )}

            <p className="text-[10px] text-on-surface/30 text-right font-bold uppercase tracking-widest">
              Fuente: {result.source}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

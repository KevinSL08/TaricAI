"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Send, Sparkles, Loader2, ArrowRight, CheckCircle } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const quickExamples = [
  "Aceite de oliva virgen extra en botella de vidrio de 750ml",
  "Camiseta de algodón 100% para hombre",
  "Tornillos de acero inoxidable M8",
  "Vino tinto Rioja reserva 2019",
];

interface ClassifyResult {
  taric_code: string;
  description: string;
  confidence: number;
  section?: string;
  chapter?: string;
}

export function ClassifierDemo() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ClassifyResult | null>(null);
  const [error, setError] = useState("");

  const handleClassify = async (text?: string) => {
    const query = text || input;
    if (!query.trim()) return;

    setLoading(true);
    setResult(null);
    setError("");
    if (text) setInput(text);

    try {
      const res = await fetch(`${API_URL}/api/v1/classify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: query, origin_country: "CN" }),
      });

      if (!res.ok) throw new Error("Error en la clasificación");

      const data = await res.json();
      setResult(data);
    } catch {
      setError("No se pudo conectar con el clasificador. Verifica que el API esté activo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="demo" className="px-6 py-24 max-w-7xl mx-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.98 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        className="bg-surface/30 backdrop-blur-md p-6 sm:p-10 rounded-[3rem] border border-outline-variant shadow-2xl relative overflow-hidden"
      >
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 mb-10">
          <div className="space-y-1">
            <span className="text-[10px] font-black text-cyan uppercase tracking-[0.3em]">
              DEMO EN VIVO
            </span>
            <h3 className="text-3xl font-black tracking-tighter">
              Clasificador TARIC
            </h3>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <div className="text-[10px] font-bold text-on-surface/40 uppercase">
                Status
              </div>
              <div className="text-xs font-black text-green-400">OPERATIVO</div>
            </div>
            <div className="w-12 h-12 bg-surface-bright rounded-2xl flex items-center justify-center border border-outline-variant">
              <Sparkles className="w-6 h-6 text-cyan" />
            </div>
          </div>
        </div>

        {/* Input Area */}
        <div className="space-y-6">
          <div className="relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleClassify();
                }
              }}
              placeholder="Describe la mercancía a clasificar... Ej: Aceite de oliva virgen extra en botella de vidrio"
              rows={3}
              className="w-full bg-background/50 border border-outline-variant rounded-2xl py-4 px-6 pr-16 text-sm focus:outline-none focus:border-cyan/50 transition-all resize-none placeholder:text-on-surface/30"
            />
            <button
              onClick={() => handleClassify()}
              disabled={!input.trim() || loading}
              className="absolute right-3 bottom-3 w-12 h-12 bg-cyan text-[#0a0f14] rounded-xl flex items-center justify-center hover:scale-105 active:scale-95 disabled:opacity-50 transition-all kinetic-gradient"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>

          {/* Quick Examples */}
          <div className="flex flex-wrap gap-2">
            <span className="text-[10px] font-black text-on-surface/30 uppercase tracking-widest self-center mr-2">
              Ejemplos:
            </span>
            {quickExamples.map((ex) => (
              <button
                key={ex}
                onClick={() => handleClassify(ex)}
                className="text-[11px] font-bold text-cyan/70 bg-cyan/5 px-3 py-1.5 rounded-full border border-cyan/10 hover:bg-cyan/10 hover:text-cyan transition-all"
              >
                {ex.length > 35 ? ex.substring(0, 35) + "..." : ex}
              </button>
            ))}
          </div>
        </div>

        {/* Results */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-8 space-y-4"
            >
              <div className="bg-cyan/5 border border-cyan/20 rounded-2xl p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <span className="text-xs font-black uppercase tracking-widest text-green-400">
                    Clasificacion Exitosa
                  </span>
                </div>

                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="p-4 bg-background/40 rounded-2xl border border-outline-variant">
                    <span className="text-[10px] text-cyan block mb-1 uppercase font-black tracking-widest">
                      Codigo TARIC
                    </span>
                    <span className="text-2xl font-black font-mono text-cyan">
                      {result.taric_code}
                    </span>
                  </div>
                  <div className="p-4 bg-background/40 rounded-2xl border border-outline-variant">
                    <span className="text-[10px] text-orange block mb-1 uppercase font-black tracking-widest">
                      Confianza
                    </span>
                    <span className="text-2xl font-black text-orange">
                      {Math.round((result.confidence || 0.94) * 100)}%
                    </span>
                  </div>
                </div>

                <div className="p-4 bg-background/40 rounded-2xl border border-outline-variant">
                  <span className="text-[10px] text-on-surface/40 block mb-1 uppercase font-black tracking-widest">
                    Descripcion Oficial
                  </span>
                  <p className="text-sm font-bold text-on-surface/80">
                    {result.description}
                  </p>
                </div>
              </div>

              <div className="flex justify-center">
                <a href="/dashboard/classify">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    className="text-xs font-black text-cyan uppercase tracking-widest flex items-center gap-2"
                  >
                    CLASIFICAR MAS PRODUCTOS{" "}
                    <ArrowRight className="w-4 h-4" />
                  </motion.button>
                </a>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mt-8 bg-red-500/10 border border-red-500/20 rounded-2xl p-6"
            >
              <p className="text-sm font-bold text-red-400">{error}</p>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </section>
  );
}

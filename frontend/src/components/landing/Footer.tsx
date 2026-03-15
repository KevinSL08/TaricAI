"use client";

import { Ship } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-surface/80 backdrop-blur-xl px-6 py-20 border-t border-outline-variant">
      <div className="max-w-7xl mx-auto grid md:grid-cols-2 lg:grid-cols-4 gap-12">
        <div className="space-y-6 lg:col-span-2">
          <div className="flex items-center gap-3">
            <Ship className="w-8 h-8 text-cyan" />
            <span className="font-black text-2xl tracking-tighter text-glow">
              Taric<span className="text-cyan">AI</span>
            </span>
          </div>
          <p className="text-on-surface/50 max-w-sm leading-relaxed text-sm">
            Revolucionando la clasificación arancelaria mediante inteligencia artificial.
            Precisión, velocidad y cumplimiento normativo para agencias de aduanas e importadores.
          </p>
          <div className="flex gap-3">
            <span className="text-[9px] font-black uppercase tracking-widest text-on-surface/20 bg-surface-bright px-3 py-1.5 rounded-full border border-outline-variant">
              TARIC
            </span>
            <span className="text-[9px] font-black uppercase tracking-widest text-on-surface/20 bg-surface-bright px-3 py-1.5 rounded-full border border-outline-variant">
              IA
            </span>
            <span className="text-[9px] font-black uppercase tracking-widest text-on-surface/20 bg-surface-bright px-3 py-1.5 rounded-full border border-outline-variant">
              ADUANAS
            </span>
          </div>
        </div>

        <div className="space-y-6">
          <h4 className="text-[11px] font-black uppercase tracking-[0.3em] text-cyan">
            Producto
          </h4>
          <div className="space-y-3">
            {["Clasificador IA", "Calculador de Aranceles", "Control Fitosanitario", "Documentación", "API"].map(
              (item) => (
                <div
                  key={item}
                  className="text-sm text-on-surface/40 hover:text-on-surface/70 transition-colors cursor-pointer font-medium"
                >
                  {item}
                </div>
              )
            )}
          </div>
        </div>

        <div className="space-y-6">
          <h4 className="text-[11px] font-black uppercase tracking-[0.3em] text-cyan">
            Empresa
          </h4>
          <div className="space-y-3">
            {["Sobre Nosotros", "Contacto", "Blog", "Privacidad", "Términos"].map(
              (item) => (
                <div
                  key={item}
                  className="text-sm text-on-surface/40 hover:text-on-surface/70 transition-colors cursor-pointer font-medium"
                >
                  {item}
                </div>
              )
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto mt-16 pt-8 border-t border-outline-variant flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="text-[11px] text-on-surface/30 font-bold uppercase tracking-widest">
          © 2026 TaricAI. Todos los derechos reservados.
        </p>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400 pulse-glow" />
          <span className="text-[10px] font-black text-green-400 uppercase tracking-widest">
            Todos los sistemas operativos
          </span>
        </div>
      </div>
    </footer>
  );
}

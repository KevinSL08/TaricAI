"use client";

import { motion } from "motion/react";
import {
  Brain,
  Calculator,
  Leaf,
  FileText,
  ShieldCheck,
  Globe,
  ArrowRight,
  Ship,
} from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "Clasificacion IA",
    description:
      "Clasificación automática de mercancías en el sistema TARIC con 94% de precisión a nivel de código completo (10 dígitos).",
    color: "cyan",
    stats: [
      { label: "Precision", value: "94%" },
      { label: "Codigos", value: "16.4k" },
    ],
  },
  {
    icon: Calculator,
    title: "Aranceles en Tiempo Real",
    description:
      "Cálculo instantáneo de derechos de importación, IVA, tasas especiales y preferencias arancelarias por país de origen.",
    color: "primary",
    stats: [
      { label: "Paises", value: "184+" },
      { label: "Acuerdos", value: "40+" },
    ],
  },
  {
    icon: ShieldCheck,
    title: "Compliance Proactivo",
    description:
      "Alertas automáticas sobre anti-dumping, sanciones, restricciones fitosanitarias y cambios regulatorios que afectan tus importaciones.",
    color: "cyan",
    badge: true,
  },
];

const bentoItems = [
  {
    icon: FileText,
    title: "Documentacion Automatica",
    description: "Genera DUA, EUR.1, certificados de origen y checklists de forma automática.",
    span: 2,
  },
  {
    icon: Globe,
    title: "Cobertura Global",
    stat: "184",
    unit: "PAISES",
  },
  {
    icon: Leaf,
    title: "Control Fitosanitario",
    stat: "99.9%",
    statColor: "text-green-400",
  },
];

export function Features() {
  return (
    <section id="features" className="px-6 py-24 max-w-7xl mx-auto space-y-16">
      {/* Section Header */}
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        className="flex flex-col md:flex-row md:items-end justify-between gap-4"
      >
        <div className="space-y-2">
          <h2 className="text-[0.75rem] uppercase tracking-[0.4em] font-black text-cyan">
            CAPACIDADES PRINCIPALES
          </h2>
          <p className="text-3xl sm:text-4xl font-black tracking-tight">
            Todo lo que Necesitas
          </p>
        </div>
        <p className="text-on-surface/40 text-sm max-w-xs">
          Tecnología diseñada para automatizar y optimizar el despacho aduanero.
        </p>
      </motion.div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {features.map((feature, i) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            whileHover={{
              y: -10,
              backgroundColor: feature.badge
                ? "rgba(0, 210, 255, 0.05)"
                : "rgba(255, 255, 255, 0.02)",
            }}
            className={`${
              feature.badge
                ? "bg-cyan/5 border-cyan/20"
                : "bg-surface/50 border-outline-variant"
            } p-8 rounded-3xl border relative overflow-hidden group cursor-pointer transition-all perspective-1000`}
          >
            <div className="relative z-10 space-y-6">
              {feature.badge && (
                <div className="inline-flex items-center gap-2 bg-cyan/20 px-3 py-1 rounded-full text-cyan border border-cyan/30">
                  <ShieldCheck className="w-4 h-4" />
                  <span className="text-[10px] font-black uppercase tracking-widest">
                    Compliance Shield
                  </span>
                </div>
              )}
              {!feature.badge && (
                <div className="w-14 h-14 bg-cyan/10 rounded-2xl flex items-center justify-center border border-cyan/20 group-hover:scale-110 transition-transform">
                  <feature.icon className="w-7 h-7 text-cyan" />
                </div>
              )}
              <div className="space-y-2">
                <h3 className="text-xl font-black uppercase tracking-tight">
                  {feature.title}
                </h3>
                <p className="text-sm text-on-surface/50 leading-relaxed">
                  {feature.description}
                </p>
              </div>
              {feature.stats && (
                <div className="pt-4 grid grid-cols-2 gap-3">
                  {feature.stats.map((stat) => (
                    <div
                      key={stat.label}
                      className="bg-background/40 p-4 rounded-2xl border border-outline-variant group-hover:border-cyan/30 transition-colors"
                    >
                      <span className="text-[10px] text-cyan block mb-1 uppercase font-black tracking-widest">
                        {stat.label}
                      </span>
                      <span className="text-xl font-black">{stat.value}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            {!feature.badge && (
              <feature.icon className="absolute -right-8 -bottom-8 w-40 h-40 text-on-surface/[0.03] group-hover:text-cyan/10 group-hover:rotate-12 transition-all duration-500" />
            )}
            {feature.badge && (
              <div className="absolute top-0 right-0 w-48 h-48 bg-cyan/10 rounded-full -mr-24 -mt-24 blur-[80px] group-hover:bg-cyan/20 transition-colors" />
            )}
          </motion.div>
        ))}
      </div>

      {/* Bento Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Docs - span 2 */}
        <div className="md:col-span-2 bento-item group overflow-hidden relative">
          <div className="relative z-10 h-full flex flex-col justify-between min-h-[200px]">
            <div className="space-y-2">
              <div className="w-10 h-10 bg-cyan/10 rounded-xl flex items-center justify-center border border-cyan/20">
                <FileText className="w-5 h-5 text-cyan" />
              </div>
              <h3 className="text-xl font-black uppercase tracking-tight">
                Documentacion Automatica
              </h3>
              <p className="text-xs text-on-surface/40">
                DUA, EUR.1, certificados de origen, T2L y checklists generados automáticamente.
              </p>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              className="text-xs font-black text-cyan uppercase tracking-widest flex items-center gap-2 mt-6"
            >
              EXPLORAR <ArrowRight className="w-4 h-4" />
            </motion.button>
          </div>
          <div className="absolute -right-10 -bottom-10 w-40 h-40 bg-cyan/5 rounded-full blur-3xl group-hover:bg-cyan/10 transition-all" />
        </div>

        {/* Global */}
        <div className="bento-item group">
          <div className="h-full flex flex-col justify-between min-h-[200px]">
            <div className="space-y-4">
              <div className="w-10 h-10 bg-orange/10 rounded-xl flex items-center justify-center border border-orange/20">
                <Globe className="w-5 h-5 text-orange" />
              </div>
              <h3 className="text-lg font-black uppercase tracking-tight">
                Cobertura Global
              </h3>
            </div>
            <div className="text-4xl font-black text-glow">
              184<span className="text-sm text-on-surface/30 ml-1">PAISES</span>
            </div>
          </div>
        </div>

        {/* Phyto */}
        <div className="bento-item group">
          <div className="h-full flex flex-col justify-between min-h-[200px]">
            <div className="space-y-4">
              <div className="w-10 h-10 bg-green-400/10 rounded-xl flex items-center justify-center border border-green-400/20">
                <Leaf className="w-5 h-5 text-green-400" />
              </div>
              <h3 className="text-lg font-black uppercase tracking-tight">
                Fitosanitario
              </h3>
            </div>
            <div className="text-4xl font-black text-green-400">MAPA</div>
          </div>
        </div>

        {/* CTA Full Width */}
        <div className="md:col-span-4 bento-item overflow-hidden relative group">
          <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="space-y-4 max-w-md">
              <h3 className="text-2xl font-black tracking-tighter">
                Optimizacion con TaricAI
              </h3>
              <p className="text-sm text-on-surface/60 leading-relaxed">
                Nuestra IA analiza la nomenclatura combinada TARIC, acuerdos preferenciales y
                medidas vigentes para encontrar la clasificación más precisa y el menor coste arancelario legal.
              </p>
              <a href="#demo">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  className="text-xs font-black text-cyan uppercase tracking-widest flex items-center gap-2"
                >
                  PROBAR CLASIFICADOR <ArrowRight className="w-4 h-4" />
                </motion.button>
              </a>
            </div>
            <div className="flex gap-4">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="w-24 h-32 bg-background/60 rounded-2xl border border-outline-variant flex flex-col items-center justify-center gap-3 group-hover:border-cyan/30 transition-all"
                >
                  <div className="w-8 h-8 bg-cyan/10 rounded-full flex items-center justify-center">
                    <Ship className="w-4 h-4 text-cyan" />
                  </div>
                  <div className="h-1 w-12 bg-cyan/20 rounded-full overflow-hidden">
                    <motion.div
                      animate={{ x: [-48, 48] }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "linear",
                      }}
                      className="h-full w-full bg-cyan"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

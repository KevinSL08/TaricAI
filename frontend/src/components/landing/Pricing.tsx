"use client";

import { motion } from "motion/react";
import { Check, ArrowRight, Sparkles } from "lucide-react";

const plans = [
  {
    name: "STARTER",
    price: "249",
    description: "Para agencias que inician su transformación digital",
    features: [
      "5 usuarios",
      "200 consultas/mes",
      "Clasificación TARIC con IA",
      "Cálculo de aranceles",
      "Soporte por email",
    ],
    highlighted: false,
  },
  {
    name: "PROFESSIONAL",
    price: "599",
    description: "Para agencias con volumen medio-alto de operaciones",
    features: [
      "15 usuarios",
      "Consultas ilimitadas",
      "Todo de Starter",
      "Control fitosanitario",
      "Documentación automática",
      "Soporte prioritario",
      "API access",
    ],
    highlighted: true,
  },
  {
    name: "ENTERPRISE",
    price: "1,499",
    description: "Solución completa para grandes operadores",
    features: [
      "Usuarios ilimitados",
      "Consultas ilimitadas",
      "Todo de Professional",
      "Integraciones custom",
      "SLA garantizado",
      "Account manager dedicado",
      "Onboarding personalizado",
    ],
    highlighted: false,
  },
];

export function Pricing() {
  return (
    <section id="pricing" className="px-6 py-24 max-w-7xl mx-auto space-y-16">
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        className="text-center space-y-4"
      >
        <h2 className="text-[0.75rem] uppercase tracking-[0.4em] font-black text-cyan">
          PLANES
        </h2>
        <p className="text-3xl sm:text-4xl font-black tracking-tight">
          Precio Justo, Valor Real
        </p>
        <p className="text-on-surface/40 text-sm max-w-md mx-auto">
          Cada plan incluye acceso a nuestra IA de clasificación TARIC con datos oficiales verificados.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((plan, i) => (
          <motion.div
            key={plan.name}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            whileHover={{ y: -8 }}
            className={`relative p-8 rounded-3xl border transition-all ${
              plan.highlighted
                ? "bg-cyan/5 border-cyan/30 shadow-[0_0_40px_rgba(0,210,255,0.1)]"
                : "bg-surface/40 border-outline-variant"
            }`}
          >
            {plan.highlighted && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <div className="inline-flex items-center gap-1.5 bg-cyan px-4 py-1 rounded-full text-[#0a0f14]">
                  <Sparkles className="w-3 h-3" />
                  <span className="text-[10px] font-black uppercase tracking-widest">
                    Popular
                  </span>
                </div>
              </div>
            )}

            <div className="space-y-6">
              <div>
                <h3 className="text-[11px] font-black uppercase tracking-[0.3em] text-cyan">
                  {plan.name}
                </h3>
                <div className="mt-4 flex items-baseline gap-1">
                  <span className="text-5xl font-black">€{plan.price}</span>
                  <span className="text-sm text-on-surface/40 font-bold">/mes</span>
                </div>
                <p className="mt-2 text-xs text-on-surface/40">{plan.description}</p>
              </div>

              <div className="space-y-3">
                {plan.features.map((feature) => (
                  <div key={feature} className="flex items-center gap-3">
                    <Check className="w-4 h-4 text-green-400 shrink-0" />
                    <span className="text-sm text-on-surface/70">{feature}</span>
                  </div>
                ))}
              </div>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`w-full py-4 rounded-2xl font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2 transition-all ${
                  plan.highlighted
                    ? "kinetic-gradient text-[#0a0f14]"
                    : "bg-surface-bright border border-outline-variant text-on-surface hover:border-cyan/30"
                }`}
              >
                EMPEZAR
                <ArrowRight className="w-4 h-4" />
              </motion.button>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

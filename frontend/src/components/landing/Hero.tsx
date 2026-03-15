"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { ArrowRight, BarChart3 } from "lucide-react";
import {
  AreaChart,
  Area,
  ResponsiveContainer,
} from "recharts";

const chartData = [
  { name: "1", val: 40 },
  { name: "2", val: 70 },
  { name: "3", val: 45 },
  { name: "4", val: 90 },
  { name: "5", val: 65 },
  { name: "6", val: 80 },
  { name: "7", val: 55 },
  { name: "8", val: 85 },
  { name: "9", val: 40 },
];

export function Hero() {
  return (
    <section className="relative px-6 pt-28 pb-16 overflow-hidden max-w-7xl mx-auto">
      {/* Background glows */}
      <div className="absolute top-1/4 -right-20 w-96 h-96 bg-cyan/10 rounded-full blur-[120px] animate-float" />
      <div
        className="absolute bottom-1/4 -left-20 w-72 h-72 bg-orange/5 rounded-full blur-[100px] animate-float"
        style={{ animationDelay: "-3s" }}
      />

      <div className="relative z-10 grid lg:grid-cols-2 gap-12 items-center">
        {/* Left - Text */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="space-y-8"
        >
          <div className="inline-flex items-center gap-2 bg-surface-bright/80 backdrop-blur-md px-4 py-1.5 rounded-full border border-outline-variant">
            <span className="w-2 h-2 rounded-full bg-cyan pulse-glow" />
            <span className="text-[10px] uppercase tracking-[0.3em] font-black text-cyan">
              Clasificacion Inteligente v1.0
            </span>
          </div>

          <div className="space-y-6">
            <h1 className="text-5xl sm:text-7xl lg:text-8xl font-black leading-none tracking-tighter text-glow flex flex-col">
              <span className="text-on-surface">CLASIFICA</span>
              <span className="text-cyan drop-shadow-[0_0_15px_rgba(0,210,255,0.3)]">
                CON IA
              </span>
            </h1>

            <div className="flex items-center gap-4">
              <div className="h-[1px] w-12 bg-cyan/30" />
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-cyan animate-pulse" />
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-cyan/70">
                  94% Precision TARIC
                </span>
              </div>
              <div className="h-[1px] flex-1 max-w-[100px] bg-gradient-to-r from-cyan/30 to-transparent" />
            </div>
          </div>

          <p className="text-on-surface/60 text-lg leading-relaxed max-w-lg font-medium">
            El primer agente de IA que clasifica mercancías en el sistema TARIC,
            calcula aranceles y genera documentación aduanera de forma autónoma.
          </p>

          <div className="flex flex-wrap gap-4">
            <Link href="/dashboard/classify">
              <motion.button
                whileHover={{
                  scale: 1.02,
                  boxShadow: "0 0 20px rgba(0, 210, 255, 0.3)",
                }}
                whileTap={{ scale: 0.98 }}
                className="kinetic-gradient text-[#0a0f14] font-black py-4 px-10 rounded-2xl flex items-center gap-3 transition-all"
              >
                CLASIFICAR AHORA
                <ArrowRight className="w-5 h-5" />
              </motion.button>
            </Link>
            <a href="#demo">
              <motion.button
                whileHover={{ backgroundColor: "rgba(255, 255, 255, 0.05)" }}
                className="bg-transparent text-on-surface font-bold py-4 px-10 rounded-2xl border border-outline-variant transition-colors"
              >
                VER DEMO
              </motion.button>
            </a>
          </div>
        </motion.div>

        {/* Right - Live Monitor Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9, rotateY: 20 }}
          animate={{ opacity: 1, scale: 1, rotateY: 0 }}
          transition={{ duration: 1, delay: 0.2 }}
          className="relative hidden lg:block perspective-1000"
        >
          <div className="relative z-10 bg-surface/40 backdrop-blur-xl p-8 rounded-[2.5rem] border border-outline-variant shadow-2xl glow-border preserve-3d">
            {/* Window dots */}
            <div className="flex items-center justify-between mb-8">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500/50" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
                <div className="w-3 h-3 rounded-full bg-green-500/50" />
              </div>
              <div className="text-[10px] font-mono text-cyan/50 uppercase tracking-widest">
                Live Classification Monitor
              </div>
            </div>

            {/* Chart */}
            <div className="space-y-6">
              <div className="h-40 w-full bg-background/50 rounded-2xl border border-outline-variant overflow-hidden p-2">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#00d2ff" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#00d2ff" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <Area
                      type="monotone"
                      dataKey="val"
                      stroke="#00d2ff"
                      fillOpacity={1}
                      fill="url(#colorVal)"
                      strokeWidth={3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-background/30 rounded-2xl border border-outline-variant">
                  <span className="text-[10px] text-on-surface/40 block mb-1 uppercase font-bold">
                    Precision
                  </span>
                  <span className="text-2xl font-black text-cyan">94.0%</span>
                </div>
                <div className="p-4 bg-background/30 rounded-2xl border border-outline-variant">
                  <span className="text-[10px] text-on-surface/40 block mb-1 uppercase font-bold">
                    Codigos TARIC
                  </span>
                  <span className="text-2xl font-black text-orange">16,457</span>
                </div>
              </div>
            </div>
          </div>
          <div className="absolute -inset-4 bg-cyan/5 blur-3xl rounded-full -z-10" />
        </motion.div>
      </div>
    </section>
  );
}

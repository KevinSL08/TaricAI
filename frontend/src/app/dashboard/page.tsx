"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "motion/react";
import {
  PackageSearch,
  History,
  Search,
  Activity,
  Calculator,
  ArrowRight,
  Ship,
} from "lucide-react";
import { getHistory, type HistoryEntry } from "@/lib/store";
import { checkHealth } from "@/lib/api";

export default function DashboardPage() {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [health, setHealth] = useState<{
    status: string;
    anthropic_configured: boolean;
    pinecone_configured: boolean;
  } | null>(null);

  useEffect(() => {
    setHistory(getHistory());
    checkHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  const recentHistory = history.slice(0, 5);
  const avgConfidence =
    history.length > 0
      ? history.reduce((sum, h) => sum + h.result.top_confidence, 0) /
        history.length
      : 0;

  const stats = [
    {
      icon: PackageSearch,
      value: history.length.toString(),
      label: "Clasificaciones",
      color: "cyan",
    },
    {
      icon: Activity,
      value: avgConfidence > 0 ? `${Math.round(avgConfidence * 100)}%` : "-",
      label: "Confianza media",
      color: "green-400",
    },
    {
      icon: Search,
      value: "16,457",
      label: "Codigos TARIC",
      color: "orange",
    },
    {
      icon: Ship,
      value: health?.status === "ok" ? "Online" : "Offline",
      label: "Estado del API",
      color: health?.status === "ok" ? "green-400" : "red-400",
      pulse: true,
    },
  ];

  const quickActions = [
    {
      href: "/dashboard/classify",
      icon: PackageSearch,
      title: "Clasificar",
      description: "Codigo TARIC 10 digitos",
    },
    {
      href: "/dashboard/aranceles",
      icon: Calculator,
      title: "Aranceles",
      description: "Calcular derechos e IVA",
    },
    {
      href: "/dashboard/history",
      icon: History,
      title: "Historial",
      description: "Consultas anteriores",
    },
    {
      href: "/dashboard/search",
      icon: Search,
      title: "Buscar TARIC",
      description: "Nomenclatura combinada",
    },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="space-y-1">
        <h2 className="text-[0.75rem] uppercase tracking-[0.4em] font-black text-cyan">
          CENTRO DE CONTROL
        </h2>
        <p className="text-3xl font-black tracking-tighter">Dashboard</p>
      </div>

      {/* Stats */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="bento-item !p-5"
          >
            <div className="flex items-center gap-4">
              <div className={`w-10 h-10 bg-${stat.color}/10 rounded-xl flex items-center justify-center border border-${stat.color}/20`}>
                {stat.pulse ? (
                  <div
                    className={`w-3 h-3 rounded-full bg-${stat.color} ${
                      health?.status === "ok" ? "pulse-glow" : ""
                    }`}
                  />
                ) : (
                  <stat.icon size={18} className={`text-${stat.color}`} />
                )}
              </div>
              <div>
                <p className={`text-2xl font-black text-${stat.color}`}>
                  {stat.value}
                </p>
                <p className="text-[10px] font-bold text-on-surface/40 uppercase tracking-widest">
                  {stat.label}
                </p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {quickActions.map((action, i) => (
          <Link key={action.href} href={action.href}>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.05 }}
              whileHover={{ y: -4, borderColor: "rgba(0, 210, 255, 0.3)" }}
              className="bg-surface/40 backdrop-blur-xl rounded-2xl border border-outline-variant p-6 cursor-pointer transition-all group"
            >
              <div className="w-12 h-12 bg-cyan/10 rounded-2xl flex items-center justify-center border border-cyan/20 mb-4 group-hover:scale-110 transition-transform">
                <action.icon size={22} className="text-cyan" />
              </div>
              <h3 className="text-lg font-black tracking-tight mb-1">
                {action.title}
              </h3>
              <p className="text-xs text-on-surface/40 font-medium">
                {action.description}
              </p>
              <ArrowRight
                size={16}
                className="text-on-surface/20 mt-4 group-hover:text-cyan group-hover:translate-x-1 transition-all"
              />
            </motion.div>
          </Link>
        ))}
      </div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-surface/30 backdrop-blur-md p-6 sm:p-8 rounded-[2rem] border border-outline-variant"
      >
        <div className="flex items-center justify-between mb-6">
          <div className="space-y-1">
            <span className="text-[10px] font-black text-cyan uppercase tracking-[0.3em]">
              ACTIVIDAD RECIENTE
            </span>
            <h3 className="text-xl font-black tracking-tight">
              Ultimas Clasificaciones
            </h3>
          </div>
          {history.length > 5 && (
            <Link
              href="/dashboard/history"
              className="text-[10px] font-bold text-cyan cursor-pointer hover:underline uppercase tracking-widest"
            >
              VER TODO
            </Link>
          )}
        </div>

        {recentHistory.length === 0 ? (
          <div className="py-16 text-center space-y-4 opacity-30">
            <PackageSearch className="w-16 h-16 mx-auto" />
            <p className="font-black uppercase tracking-[0.2em]">
              No hay clasificaciones aun
            </p>
            <Link href="/dashboard/classify">
              <motion.button
                whileHover={{ scale: 1.05 }}
                className="mt-4 kinetic-gradient text-[#0a0f14] font-black py-3 px-8 rounded-xl text-xs uppercase tracking-widest"
              >
                Clasificar primer producto
              </motion.button>
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {recentHistory.map((entry, i) => (
              <motion.div
                key={entry.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="flex items-center justify-between p-4 bg-surface-bright/20 rounded-2xl border border-outline-variant hover:border-cyan/30 transition-colors"
              >
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  <div className="w-2 h-2 rounded-full bg-cyan pulse-glow" />
                  <div className="min-w-0">
                    <div className="text-sm font-bold truncate">
                      {entry.description}
                    </div>
                    <div className="text-[10px] text-on-surface/40 font-bold uppercase">
                      {new Date(entry.timestamp).toLocaleString("es-ES")}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3 ml-4 shrink-0">
                  <code className="text-sm font-mono bg-cyan/10 text-cyan px-3 py-1 rounded-lg border border-cyan/20">
                    {entry.result.top_code}
                  </code>
                  <span className="text-[10px] font-black px-2 py-1 rounded-lg bg-green-400/10 text-green-400">
                    {Math.round(entry.result.top_confidence * 100)}%
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
}

"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "motion/react";
import { Ship, LogIn, Menu, X } from "lucide-react";

const navLinks = [
  { label: "Producto", href: "#features" },
  { label: "Demo", href: "#demo" },
  { label: "Precios", href: "#pricing" },
  { label: "Equipo", href: "#team" },
];

export function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-panel border-b border-outline-variant">
      <div className="px-6 h-16 flex items-center justify-between max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-3"
        >
          <div className="w-8 h-8 bg-cyan/20 rounded-lg flex items-center justify-center border border-cyan/30">
            <Ship className="w-5 h-5 text-cyan" />
          </div>
          <Link href="/" className="font-bold text-xl tracking-tighter text-glow">
            Taric<span className="text-cyan">AI</span>
          </Link>
        </motion.div>

        {/* Desktop */}
        <div className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="text-[11px] font-bold text-on-surface/60 hover:text-cyan transition-colors uppercase tracking-[0.2em]"
            >
              {link.label}
            </a>
          ))}
          <Link href="/login">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center gap-2 bg-cyan/10 px-5 py-2 rounded-full border border-cyan/20 text-xs font-bold text-cyan hover:bg-cyan/20 transition-all"
            >
              <LogIn className="w-4 h-4" />
              ACCESO
            </motion.button>
          </Link>
        </div>

        {/* Mobile toggle */}
        <button
          className="md:hidden text-on-surface/70"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          {mobileOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden glass-panel border-b border-outline-variant px-6 py-4 space-y-4"
        >
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              onClick={() => setMobileOpen(false)}
              className="block text-sm font-bold text-on-surface/60 hover:text-cyan uppercase tracking-widest"
            >
              {link.label}
            </a>
          ))}
          <Link
            href="/login"
            onClick={() => setMobileOpen(false)}
            className="flex items-center gap-2 text-cyan text-sm font-bold"
          >
            <LogIn className="w-4 h-4" />
            ACCESO
          </Link>
        </motion.div>
      )}
    </nav>
  );
}

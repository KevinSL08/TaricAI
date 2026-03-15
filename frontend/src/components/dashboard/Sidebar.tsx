"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Search,
  History,
  PackageSearch,
  Calculator,
  LogOut,
  Menu,
  X,
  Ship,
} from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/components/auth/AuthProvider";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/classify", label: "Clasificar", icon: PackageSearch },
  { href: "/dashboard/aranceles", label: "Aranceles", icon: Calculator },
  { href: "/dashboard/history", label: "Historial", icon: History },
  { href: "/dashboard/search", label: "Buscar TARIC", icon: Search },
];

export function Sidebar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user, signOut } = useAuth();

  return (
    <>
      {/* Mobile toggle */}
      <button
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-surface border border-outline-variant rounded-xl shadow-lg"
        onClick={() => setMobileOpen(!mobileOpen)}
      >
        {mobileOpen ? (
          <X size={20} className="text-on-surface" />
        ) : (
          <Menu size={20} className="text-on-surface" />
        )}
      </button>

      {/* Overlay */}
      {mobileOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed top-0 left-0 z-40 h-screen w-64 glass-panel border-r border-outline-variant flex flex-col transition-transform duration-200 lg:translate-x-0",
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo */}
        <div className="h-16 flex items-center px-6 border-b border-outline-variant">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-8 h-8 bg-cyan/20 rounded-lg flex items-center justify-center border border-cyan/30">
              <Ship className="w-5 h-5 text-cyan" />
            </div>
            <span className="font-bold text-lg tracking-tighter text-glow">
              Taric<span className="text-cyan">AI</span>
            </span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map((item) => {
            const isActive =
              item.href === "/dashboard"
                ? pathname === "/dashboard"
                : pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-bold transition-all",
                  isActive
                    ? "bg-cyan/10 text-cyan border border-cyan/20"
                    : "text-on-surface/50 hover:bg-surface-bright hover:text-on-surface border border-transparent"
                )}
              >
                <item.icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Bottom: user + logout */}
        <div className="px-3 py-4 border-t border-outline-variant space-y-2">
          {user && (
            <div className="px-3 py-2 bg-surface-bright/50 rounded-xl border border-outline-variant">
              <p className="text-[10px] font-black text-cyan uppercase tracking-widest mb-0.5">
                USUARIO
              </p>
              <p className="text-xs text-on-surface/60 truncate font-medium">
                {user.email}
              </p>
            </div>
          )}
          <button
            onClick={() => signOut()}
            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-bold text-on-surface/40 hover:bg-red-500/10 hover:text-red-400 transition-all w-full border border-transparent"
          >
            <LogOut size={18} />
            Cerrar sesion
          </button>
        </div>
      </aside>
    </>
  );
}

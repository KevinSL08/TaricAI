"use client";

import { motion } from "motion/react";
import { Linkedin, Shield } from "lucide-react";

const team = [
  {
    name: "Kevin Daniel Suarez Largo",
    role: "CEO & Co-Founder",
    description: "Comercio Exterior y Negocios Internacionales. Visión estratégica y desarrollo de negocio.",
    linkedin: "https://linkedin.com/in/kevindanielsl",
  },
  {
    name: "Anderson de Jesus Escorcia",
    role: "CTO & Co-Founder",
    description: "Ingeniero de Sistemas. Especialista en LLMs, IA y arquitectura de software.",
    linkedin: "#",
  },
  {
    name: "Pelayo Serrano Garcia",
    role: "Asesor Estratégico",
    description: "38+ años de experiencia en aduanas. Representante Aduanero Autorizado (RAA).",
    badge: "RAA",
    linkedin: "#",
  },
];

export function Team() {
  return (
    <section id="team" className="px-6 py-24 max-w-7xl mx-auto space-y-16">
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        className="text-center space-y-4"
      >
        <h2 className="text-[0.75rem] uppercase tracking-[0.4em] font-black text-cyan">
          EQUIPO
        </h2>
        <p className="text-3xl sm:text-4xl font-black tracking-tight">
          Expertos en Aduanas + IA
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {team.map((member, i) => (
          <motion.div
            key={member.name}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            whileHover={{ y: -5 }}
            className="bg-surface/40 backdrop-blur-xl p-8 rounded-3xl border border-outline-variant group hover:border-cyan/30 transition-all"
          >
            <div className="space-y-6">
              {/* Avatar placeholder */}
              <div className="w-20 h-20 rounded-3xl bg-cyan/10 flex items-center justify-center border border-cyan/20 group-hover:scale-105 transition-transform">
                <span className="text-2xl font-black text-cyan">
                  {member.name
                    .split(" ")
                    .map((n) => n[0])
                    .slice(0, 2)
                    .join("")}
                </span>
              </div>

              <div className="space-y-2">
                <h3 className="text-xl font-black tracking-tight">{member.name}</h3>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-black text-cyan uppercase tracking-widest">
                    {member.role}
                  </span>
                  {member.badge && (
                    <span className="inline-flex items-center gap-1 bg-orange/10 text-orange px-2 py-0.5 rounded-full text-[9px] font-black border border-orange/20">
                      <Shield className="w-3 h-3" />
                      {member.badge}
                    </span>
                  )}
                </div>
                <p className="text-sm text-on-surface/50 leading-relaxed">
                  {member.description}
                </p>
              </div>

              <a
                href={member.linkedin}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-[11px] font-bold text-on-surface/40 hover:text-cyan transition-colors uppercase tracking-widest"
              >
                <Linkedin className="w-4 h-4" />
                LinkedIn
              </a>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

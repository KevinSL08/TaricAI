import { Linkedin } from "lucide-react";

const team = [
  {
    name: "Kevin Daniel Suarez Largo",
    role: "CEO & Co-Founder",
    description:
      "Comercio Exterior y Negocios Internacionales. Experiencia en operaciones de importacion y normativa aduanera.",
  },
  {
    name: "Anderson de Jesus Escorcia Hernandez",
    role: "CTO & Co-Founder",
    description:
      "Ingeniero de Sistemas. Especialista en LLMs, arquitectura de IA y desarrollo full-stack.",
  },
  {
    name: "Pelayo Serrano Garcia",
    role: "Advisor",
    description:
      "38+ anos de experiencia en aduanas. Representante Aduanero Autorizado (RAA). Experto en clasificacion TARIC.",
  },
];

export function Team() {
  return (
    <section id="team" className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/50">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            Nuestro equipo
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Combinamos tecnologia de vanguardia con decadas de experiencia en
            comercio exterior y aduanas.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {team.map((member) => (
            <div key={member.name} className="text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                <span className="text-white text-2xl font-bold">
                  {member.name
                    .split(" ")
                    .map((n) => n[0])
                    .slice(0, 2)
                    .join("")}
                </span>
              </div>
              <h3 className="text-lg font-semibold text-foreground">
                {member.name}
              </h3>
              <p className="text-sm text-blue-600 font-medium">{member.role}</p>
              <p className="mt-2 text-sm text-muted-foreground">
                {member.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

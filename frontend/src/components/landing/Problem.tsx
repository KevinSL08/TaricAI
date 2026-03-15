import { AlertTriangle, Clock, DollarSign } from "lucide-react";

const problems = [
  {
    icon: AlertTriangle,
    title: "Errores costosos",
    description:
      "Un codigo TARIC incorrecto puede generar multas de hasta 300% del valor de la mercancia, retrasos en aduana y perdida de clientes.",
  },
  {
    icon: Clock,
    title: "Proceso lento y manual",
    description:
      "Clasificar un producto requiere buscar entre mas de 16,000 codigos, interpretar notas legales y aplicar 6 reglas generales de interpretacion.",
  },
  {
    icon: DollarSign,
    title: "Expertos escasos y caros",
    description:
      "Los clasificadores expertos con experiencia en TARIC son dificiles de encontrar y su formacion requiere anos de practica.",
  },
];

export function Problem() {
  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/50">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            La clasificacion arancelaria es compleja
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Las agencias de aduanas e importadores enfrentan retos diarios que
            impactan directamente en su rentabilidad.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {problems.map((problem) => (
            <div
              key={problem.title}
              className="bg-card rounded-xl p-8 border border-border shadow-sm"
            >
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center mb-4">
                <problem.icon size={24} className="text-red-600 dark:text-red-400" />
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-2">
                {problem.title}
              </h3>
              <p className="text-muted-foreground">{problem.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

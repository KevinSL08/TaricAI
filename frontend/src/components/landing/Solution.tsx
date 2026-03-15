import { CheckCircle, Brain, Database, Shield } from "lucide-react";

const steps = [
  {
    icon: Brain,
    title: "IA Experta en TARIC",
    description:
      "Nuestro agente aplica las 6 Reglas Generales de Interpretacion (RGI) como un clasificador con 30+ anos de experiencia.",
  },
  {
    icon: Database,
    title: "Base de datos oficial",
    description:
      "16,457 codigos TARIC importados directamente de fuentes oficiales de la UE, siempre actualizados.",
  },
  {
    icon: Shield,
    title: "Validacion automatica",
    description:
      "Cada codigo es verificado contra la base de datos oficial. Si no existe, se corrige automaticamente al codigo valido mas cercano.",
  },
];

export function Solution() {
  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            TaricAI lo resuelve en segundos
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Describe tu producto en lenguaje natural y recibe el codigo TARIC
            correcto con explicacion detallada.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, i) => (
            <div key={step.title} className="text-center">
              <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <step.icon size={32} className="text-blue-600 dark:text-blue-400" />
              </div>
              <div className="text-sm font-medium text-blue-600 mb-2">
                Paso {i + 1}
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-2">
                {step.title}
              </h3>
              <p className="text-muted-foreground">{step.description}</p>
              <div className="mt-4 space-y-2">
                {i === 0 && (
                  <>
                    <Feature text="RAG con busqueda semantica" />
                    <Feature text="Prompt experto con 25+ ejemplos reales" />
                  </>
                )}
                {i === 1 && (
                  <>
                    <Feature text="Datos oficiales TARIC de la UE" />
                    <Feature text="21 secciones, 98 capitulos" />
                  </>
                )}
                {i === 2 && (
                  <>
                    <Feature text="Longest Prefix Match" />
                    <Feature text="90%+ precision en codigo exacto" />
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Feature({ text }: { text: string }) {
  return (
    <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
      <CheckCircle size={14} className="text-green-500 dark:text-green-400 shrink-0" />
      <span>{text}</span>
    </div>
  );
}

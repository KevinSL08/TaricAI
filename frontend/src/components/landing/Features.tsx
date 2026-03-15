import {
  Brain,
  Calculator,
  Leaf,
  Ship,
  FileText,
  MessageSquare,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

const features = [
  {
    icon: Brain,
    title: "Clasificacion IA",
    description:
      "Motor de IA que clasifica productos en codigo TARIC de 10 digitos con precision superior al 90%.",
    available: true,
  },
  {
    icon: Calculator,
    title: "Calculador de aranceles",
    description:
      "Calcula derechos arancelarios, IVA, impuestos especiales y medidas anti-dumping automaticamente.",
    available: false,
  },
  {
    icon: Leaf,
    title: "Control fitosanitario",
    description:
      "Verifica requisitos MAPA, TRACES, SOIVRE, RAPEX y CITES para tu mercancia.",
    available: false,
  },
  {
    icon: Ship,
    title: "Landed cost",
    description:
      "Calcula el coste total de importacion incluyendo tasas portuarias espanolas.",
    available: false,
  },
  {
    icon: FileText,
    title: "Checklist documental",
    description:
      "Genera automaticamente la lista de documentos necesarios: DUA, EUR.1, certificados, T2L.",
    available: false,
  },
  {
    icon: MessageSquare,
    title: "Agente conversacional",
    description:
      "Consulta en espanol cualquier duda sobre clasificacion, normativa y procedimientos.",
    available: false,
  },
];

export function Features() {
  return (
    <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/50">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            Todo lo que necesitas para importar
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Una plataforma completa que cubre todo el proceso de clasificacion
            arancelaria y gestion de importaciones.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => (
            <Card
              key={feature.title}
              className={`relative ${!feature.available ? "opacity-75" : ""}`}
            >
              {!feature.available && (
                <div className="absolute top-4 right-4 text-xs font-medium text-muted-foreground bg-muted px-2 py-1 rounded-full">
                  Proximamente
                </div>
              )}
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mb-2">
                  <feature.icon size={24} className="text-blue-600 dark:text-blue-400" />
                </div>
                <CardTitle className="text-lg">{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

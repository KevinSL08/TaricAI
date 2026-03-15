import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check } from "lucide-react";

const plans = [
  {
    name: "Starter",
    price: "249",
    description: "Para agencias pequenas o importadores independientes.",
    features: [
      "5 usuarios",
      "200 clasificaciones/mes",
      "API basica",
      "Soporte por email",
      "Historial 30 dias",
    ],
    cta: "Empezar",
    popular: false,
  },
  {
    name: "Professional",
    price: "599",
    description: "Para agencias de aduanas con volumen medio-alto.",
    features: [
      "15 usuarios",
      "Clasificaciones ilimitadas",
      "API completa",
      "Soporte prioritario",
      "Historial ilimitado",
      "Calculador de aranceles",
      "Control fitosanitario",
    ],
    cta: "Empezar",
    popular: true,
  },
  {
    name: "Enterprise",
    price: "1.499",
    description: "Para grandes operadores con necesidades a medida.",
    features: [
      "Usuarios ilimitados",
      "Clasificaciones ilimitadas",
      "API con integraciones custom",
      "Soporte dedicado 24/7",
      "SLA garantizado",
      "Todas las funcionalidades",
      "Formacion personalizada",
      "Integracion con ERP/SAP",
    ],
    cta: "Contactar",
    popular: false,
  },
];

export function Pricing() {
  return (
    <section id="pricing" className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-foreground">
            Planes adaptados a tu volumen
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Sin permanencia. Facturacion mensual o anual con descuento.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map((plan) => (
            <Card
              key={plan.name}
              className={`relative p-8 flex flex-col ${
                plan.popular ? "border-blue-600 dark:border-blue-400 border-2 shadow-lg" : ""
              }`}
            >
              {plan.popular && (
                <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 dark:bg-blue-500">
                  Mas popular
                </Badge>
              )}
              <div>
                <h3 className="text-xl font-bold text-foreground">
                  {plan.name}
                </h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {plan.description}
                </p>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-foreground">
                    {plan.price}
                  </span>
                  <span className="text-muted-foreground">/mes</span>
                </div>
              </div>

              <ul className="mt-8 space-y-3 flex-1">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <Check size={18} className="text-green-500 dark:text-green-400 shrink-0 mt-0.5" />
                    <span className="text-sm text-foreground">{feature}</span>
                  </li>
                ))}
              </ul>

              <Button
                className="mt-8 w-full"
                variant={plan.popular ? "default" : "outline"}
                size="lg"
              >
                {plan.cta}
              </Button>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

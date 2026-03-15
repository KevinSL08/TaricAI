import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, Zap } from "lucide-react";

export function Hero() {
  return (
    <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto text-center">
        <Badge variant="secondary" className="mb-6 px-4 py-1.5 text-sm">
          <Zap size={14} className="mr-1" />
          Motor de IA con +90% de precision
        </Badge>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-foreground max-w-4xl mx-auto">
          Clasificacion arancelaria{" "}
          <span className="text-blue-600">TARIC</span> con{" "}
          <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            Inteligencia Artificial
          </span>
        </h1>

        <p className="mt-6 text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto">
          Clasifica productos en segundos con IA experta en nomenclatura
          combinada TARIC. Validacion contra 16,457 codigos oficiales.
        </p>

        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Button size="lg" className="px-8 text-base" render={<a href="#demo" />}>
            Probar Demo Gratis
            <ArrowRight size={18} className="ml-2" />
          </Button>
          <Button size="lg" variant="outline" className="px-8 text-base" render={<a href="#pricing" />}>
            Ver Precios
          </Button>
        </div>

        <div className="mt-16 grid grid-cols-3 gap-8 max-w-lg mx-auto">
          <div>
            <p className="text-3xl font-bold text-foreground">90%+</p>
            <p className="text-sm text-muted-foreground mt-1">Precision exacta</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-foreground">16,457</p>
            <p className="text-sm text-muted-foreground mt-1">Codigos TARIC</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-foreground">&lt;5s</p>
            <p className="text-sm text-muted-foreground mt-1">Por clasificacion</p>
          </div>
        </div>
      </div>
    </section>
  );
}

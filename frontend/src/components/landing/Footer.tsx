import { Separator } from "@/components/ui/separator";

export function Footer() {
  return (
    <footer className="py-12 px-4 sm:px-6 lg:px-8 border-t border-border">
      <div className="max-w-7xl mx-auto">
        <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-sm">T</span>
              </div>
              <span className="font-bold text-lg">
                Taric<span className="text-blue-600">AI</span>
              </span>
            </div>
            <p className="text-sm text-muted-foreground">
              Clasificacion arancelaria TARIC con Inteligencia Artificial para
              agencias de aduanas e importadores.
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-foreground mb-4">Producto</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#features" className="hover:text-foreground transition-colors">Funcionalidades</a></li>
              <li><a href="#pricing" className="hover:text-foreground transition-colors">Precios</a></li>
              <li><a href="#demo" className="hover:text-foreground transition-colors">Demo</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">API</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-foreground mb-4">Empresa</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#team" className="hover:text-foreground transition-colors">Equipo</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">Blog</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">Contacto</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-foreground mb-4">Legal</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-foreground transition-colors">Politica de privacidad</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">Terminos de servicio</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">Aviso legal</a></li>
            </ul>
          </div>
        </div>

        <Separator className="my-8" />

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground">
            2026 TaricAI. Todos los derechos reservados.
          </p>
          <p className="text-sm text-muted-foreground">
            Madrid, Espana
          </p>
        </div>
      </div>
    </footer>
  );
}

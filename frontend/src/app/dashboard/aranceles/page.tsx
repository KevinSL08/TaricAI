"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Calculator,
  Loader2,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Info,
  Euro,
} from "lucide-react";
import {
  calculateDuties,
  type DutyCalculationResponse,
} from "@/lib/api";

const IVA_OPTIONS = [
  { value: "general", label: "General (21%)", rate: 21 },
  { value: "reducido", label: "Reducido (10%)", rate: 10 },
  { value: "superreducido", label: "Superreducido (4%)", rate: 4 },
];

export default function ArancelesPage() {
  return (
    <Suspense>
      <ArancelesContent />
    </Suspense>
  );
}

function ArancelesContent() {
  const searchParams = useSearchParams();

  const [commodityCode, setCommodityCode] = useState("");
  const [originCountry, setOriginCountry] = useState("");
  const [customsValue, setCustomsValue] = useState("");
  const [weightKg, setWeightKg] = useState("");
  const [ivaType, setIvaType] = useState("general");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DutyCalculationResponse | null>(null);
  const [showAllMeasures, setShowAllMeasures] = useState(false);

  // Pre-rellenar desde query params (viene del clasificador)
  useEffect(() => {
    const code = searchParams.get("code");
    const origin = searchParams.get("origin");
    if (code) setCommodityCode(code);
    if (origin) setOriginCountry(origin);
  }, [searchParams]);

  const handleCalculate = async () => {
    if (!commodityCode || !customsValue) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await calculateDuties({
        commodity_code: commodityCode.replace(/\s/g, ""),
        origin_country: originCountry || undefined,
        customs_value_eur: parseFloat(customsValue),
        weight_kg: weightKg ? parseFloat(weightKg) : undefined,
        iva_type: ivaType,
      });
      setResult(response);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error al calcular aranceles"
      );
    } finally {
      setLoading(false);
    }
  };

  const formatEur = (amount: number) =>
    new Intl.NumberFormat("es-ES", {
      style: "currency",
      currency: "EUR",
    }).format(amount);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
          <Calculator size={28} className="text-blue-600" />
          Calculador de Aranceles
        </h1>
        <p className="text-muted-foreground mt-1">
          Calcula aranceles, IVA y coste total de importacion con datos oficiales
        </p>
      </div>

      {/* Form */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Datos de la importacion</CardTitle>
          <CardDescription>
            Introduce el codigo TARIC, pais de origen y valor para calcular los
            aranceles
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-1.5 block">
                Codigo TARIC <span className="text-red-500">*</span>
              </label>
              <Input
                placeholder="Ej: 0805100020"
                value={commodityCode}
                onChange={(e) => setCommodityCode(e.target.value)}
                maxLength={10}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Codigo de 6-10 digitos
              </p>
            </div>

            <div>
              <label className="text-sm font-medium mb-1.5 block">
                Pais de origen
              </label>
              <Input
                placeholder="Ej: CN, MA, US"
                value={originCountry}
                onChange={(e) =>
                  setOriginCountry(e.target.value.toUpperCase().slice(0, 2))
                }
                maxLength={2}
              />
              <p className="text-xs text-muted-foreground mt-1">
                ISO 2 letras (vacio = arancel general)
              </p>
            </div>
          </div>

          <div className="grid sm:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium mb-1.5 block">
                Valor en aduana (EUR) <span className="text-red-500">*</span>
              </label>
              <Input
                type="number"
                placeholder="10000"
                value={customsValue}
                onChange={(e) => setCustomsValue(e.target.value)}
                min={0}
                step={0.01}
              />
              <p className="text-xs text-muted-foreground mt-1">Valor CIF</p>
            </div>

            <div>
              <label className="text-sm font-medium mb-1.5 block">
                Peso (kg)
              </label>
              <Input
                type="number"
                placeholder="500"
                value={weightKg}
                onChange={(e) => setWeightKg(e.target.value)}
                min={0}
                step={0.01}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Para aranceles especificos
              </p>
            </div>

            <div>
              <label className="text-sm font-medium mb-1.5 block">
                Tipo de IVA
              </label>
              <select
                className="w-full h-10 px-3 rounded-md border border-input bg-background text-sm"
                value={ivaType}
                onChange={(e) => setIvaType(e.target.value)}
              >
                {IVA_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <Button
            onClick={handleCalculate}
            disabled={loading || !commodityCode || !customsValue}
            className="w-full sm:w-auto"
          >
            {loading ? (
              <>
                <Loader2 size={16} className="mr-2 animate-spin" />
                Calculando...
              </>
            ) : (
              <>
                <Calculator size={16} className="mr-2" />
                Calcular aranceles
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Error */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertCircle size={20} className="text-red-600 mt-0.5" />
              <div>
                <p className="font-medium text-red-800">
                  Error al calcular aranceles
                </p>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Total highlight */}
          <Card className="border-green-200 bg-green-50">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-700 font-medium">
                    Coste total de importacion
                  </p>
                  <p className="text-3xl font-bold text-green-800 mt-1">
                    {formatEur(result.total_import_cost_eur)}
                  </p>
                </div>
                <Euro size={40} className="text-green-300" />
              </div>
            </CardContent>
          </Card>

          {/* Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Desglose del calculo</CardTitle>
              <CardDescription>
                {result.commodity_description}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {/* Valor en aduana */}
                <div className="flex justify-between items-center py-2">
                  <span className="text-sm text-muted-foreground">
                    Valor en aduana (CIF)
                  </span>
                  <span className="font-medium">
                    {formatEur(result.customs_value_eur)}
                  </span>
                </div>

                <div className="border-t border-border" />

                {/* Arancel */}
                <div className="flex justify-between items-center py-2">
                  <div>
                    <span className="text-sm text-muted-foreground">
                      Arancel
                    </span>
                    <Badge variant="secondary" className="ml-2 text-xs">
                      {result.duty_rate}
                    </Badge>
                  </div>
                  <span className="font-medium text-amber-700">
                    + {formatEur(result.duty_amount_eur)}
                  </span>
                </div>

                <div className="border-t border-border" />

                {/* Base IVA */}
                <div className="flex justify-between items-center py-2">
                  <span className="text-sm text-muted-foreground">
                    Base imponible IVA
                  </span>
                  <span className="text-sm">
                    {formatEur(result.iva_base_eur)}
                  </span>
                </div>

                {/* IVA */}
                <div className="flex justify-between items-center py-2">
                  <div>
                    <span className="text-sm text-muted-foreground">IVA</span>
                    <Badge variant="secondary" className="ml-2 text-xs">
                      {result.iva_rate_pct}%{" "}
                      {result.iva_type === "general"
                        ? ""
                        : `(${result.iva_type})`}
                    </Badge>
                  </div>
                  <span className="font-medium text-amber-700">
                    + {formatEur(result.iva_amount_eur)}
                  </span>
                </div>

                <div className="border-t-2 border-foreground" />

                {/* Total */}
                <div className="flex justify-between items-center py-2">
                  <span className="font-bold text-lg">TOTAL</span>
                  <span className="font-bold text-lg text-green-700">
                    {formatEur(result.total_import_cost_eur)}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Applicable measure */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Medida arancelaria aplicada</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="grid sm:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Tipo</p>
                  <p className="font-medium">
                    {result.applicable_measure.measure_type}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Arancel</p>
                  <p className="font-medium">
                    {result.applicable_measure.duty_expression}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Area geografica</p>
                  <p className="font-medium">
                    {result.applicable_measure.geographical_area}
                  </p>
                </div>
              </div>

              {/* All measures toggle */}
              {result.all_measures.length > 1 && (
                <div className="pt-4">
                  <button
                    onClick={() => setShowAllMeasures(!showAllMeasures)}
                    className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
                  >
                    {showAllMeasures ? (
                      <ChevronUp size={16} />
                    ) : (
                      <ChevronDown size={16} />
                    )}
                    Ver todas las medidas ({result.all_measures.length})
                  </button>

                  {showAllMeasures && (
                    <div className="mt-3 space-y-2">
                      {result.all_measures.map((m, i) => (
                        <div
                          key={i}
                          className="flex items-center justify-between p-2 bg-muted rounded-md text-sm"
                        >
                          <span className="truncate flex-1">
                            {m.measure_type}
                          </span>
                          <Badge variant="outline" className="mx-2">
                            {m.duty_expression}
                          </Badge>
                          <span className="text-muted-foreground text-xs">
                            {m.geographical_area}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Notes */}
          {result.notes && (
            <Card className="border-amber-200 bg-amber-50">
              <CardContent className="pt-6">
                <div className="flex items-start gap-3">
                  <Info size={20} className="text-amber-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-amber-800">Nota</p>
                    <p className="text-sm text-amber-700 mt-1">
                      {result.notes}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Source */}
          <p className="text-xs text-muted-foreground text-center">
            Datos obtenidos de {result.source} | Solo orientativo, consulte con
            su agente de aduanas
          </p>
        </div>
      )}
    </div>
  );
}

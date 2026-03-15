"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PackageSearch, History, Search, Activity } from "lucide-react";
import { getHistory, type HistoryEntry } from "@/lib/store";
import { checkHealth } from "@/lib/api";

export default function DashboardPage() {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [health, setHealth] = useState<{
    status: string;
    anthropic_configured: boolean;
    pinecone_configured: boolean;
  } | null>(null);

  useEffect(() => {
    setHistory(getHistory());
    checkHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  const recentHistory = history.slice(0, 5);
  const avgConfidence =
    history.length > 0
      ? history.reduce((sum, h) => sum + h.result.top_confidence, 0) /
        history.length
      : 0;

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Panel de control de clasificacion arancelaria TaricAI
        </p>
      </div>

      {/* Stats */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <PackageSearch size={20} className="text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{history.length}</p>
                <p className="text-sm text-muted-foreground">Clasificaciones</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <Activity size={20} className="text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {avgConfidence > 0 ? `${Math.round(avgConfidence * 100)}%` : "-"}
                </p>
                <p className="text-sm text-muted-foreground">Confianza media</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <Search size={20} className="text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">16,457</p>
                <p className="text-sm text-muted-foreground">Codigos TARIC</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${health?.status === "ok" ? "bg-green-100" : "bg-red-100"}`}>
                <div className={`w-3 h-3 rounded-full ${health?.status === "ok" ? "bg-green-500" : "bg-red-500"}`} />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {health?.status === "ok" ? "Online" : "Offline"}
                </p>
                <p className="text-sm text-muted-foreground">Estado del API</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick actions */}
      <div className="grid sm:grid-cols-3 gap-4">
        <Card className="hover:border-blue-300 transition-colors">
          <Link href="/dashboard/classify">
            <CardHeader>
              <PackageSearch size={24} className="text-blue-600 mb-2" />
              <CardTitle className="text-lg">Clasificar producto</CardTitle>
              <CardDescription>
                Obtener codigo TARIC de 10 digitos para un producto
              </CardDescription>
            </CardHeader>
          </Link>
        </Card>

        <Card className="hover:border-blue-300 transition-colors">
          <Link href="/dashboard/history">
            <CardHeader>
              <History size={24} className="text-blue-600 mb-2" />
              <CardTitle className="text-lg">Ver historial</CardTitle>
              <CardDescription>
                Consultar clasificaciones anteriores
              </CardDescription>
            </CardHeader>
          </Link>
        </Card>

        <Card className="hover:border-blue-300 transition-colors">
          <Link href="/dashboard/search">
            <CardHeader>
              <Search size={24} className="text-blue-600 mb-2" />
              <CardTitle className="text-lg">Buscar TARIC</CardTitle>
              <CardDescription>
                Buscar codigos en la nomenclatura combinada
              </CardDescription>
            </CardHeader>
          </Link>
        </Card>
      </div>

      {/* Recent activity */}
      <Card>
        <CardHeader>
          <CardTitle>Actividad reciente</CardTitle>
          <CardDescription>Ultimas clasificaciones realizadas</CardDescription>
        </CardHeader>
        <CardContent>
          {recentHistory.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <PackageSearch size={40} className="mx-auto mb-3 opacity-50" />
              <p>No hay clasificaciones aun.</p>
              <Button className="mt-4" variant="outline" render={<Link href="/dashboard/classify" />}>
                Clasificar primer producto
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {recentHistory.map((entry) => (
                <div
                  key={entry.id}
                  className="flex items-center justify-between p-3 border border-border rounded-lg"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      {entry.description}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(entry.timestamp).toLocaleString("es-ES")}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <code className="text-sm font-mono bg-muted px-2 py-1 rounded">
                      {entry.result.top_code}
                    </code>
                    <Badge variant="secondary" className="text-xs">
                      {Math.round(entry.result.top_confidence * 100)}%
                    </Badge>
                  </div>
                </div>
              ))}
              {history.length > 5 && (
                <Button variant="ghost" className="w-full" render={<Link href="/dashboard/history" />}>
                  Ver todas ({history.length})
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

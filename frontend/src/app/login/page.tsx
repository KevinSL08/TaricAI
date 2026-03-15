"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Loader2, LogIn } from "lucide-react";
import { useAuth } from "@/components/auth/AuthProvider";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { signIn, user, loading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && user) {
      router.replace("/dashboard");
    }
  }, [user, authLoading, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim() || !password) return;

    setLoading(true);
    setError(null);

    const { error } = await signIn(email.trim(), password);
    if (error) {
      setError(error);
      setLoading(false);
    } else {
      router.push("/dashboard");
    }
  }

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 size={32} className="animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (user) return null;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background to-muted/30 px-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <Link href="/" className="inline-block">
            <h1 className="text-2xl font-bold">
              Taric<span className="text-blue-600">AI</span>
            </h1>
          </Link>
          <p className="text-muted-foreground mt-1">
            Clasificacion arancelaria con IA
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Iniciar sesion</CardTitle>
            <CardDescription>
              Accede a tu cuenta para clasificar productos
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-1.5 block">
                  Email
                </label>
                <Input
                  type="email"
                  placeholder="tu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">
                  Contrasena
                </label>
                <Input
                  type="password"
                  placeholder="Tu contrasena"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  minLength={6}
                />
              </div>

              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              )}

              <Button
                type="submit"
                className="w-full"
                disabled={loading || !email.trim() || !password}
              >
                {loading ? (
                  <>
                    <Loader2 size={18} className="mr-2 animate-spin" />
                    Iniciando sesion...
                  </>
                ) : (
                  <>
                    <LogIn size={18} className="mr-2" />
                    Iniciar sesion
                  </>
                )}
              </Button>
            </form>

            <p className="text-sm text-muted-foreground text-center mt-4">
              No tienes cuenta?{" "}
              <Link
                href="/signup"
                className="text-blue-600 hover:underline font-medium"
              >
                Registrate
              </Link>
            </p>
          </CardContent>
        </Card>

        <p className="text-xs text-muted-foreground text-center">
          <Link href="/" className="hover:underline">
            Volver al inicio
          </Link>
        </p>
      </div>
    </div>
  );
}

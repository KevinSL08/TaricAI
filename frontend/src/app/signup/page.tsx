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
import { Loader2, UserPlus, CheckCircle } from "lucide-react";
import { useAuth } from "@/components/auth/AuthProvider";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const { signUp, user, loading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && user) {
      router.replace("/dashboard");
    }
  }, [user, authLoading, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim() || !password || !confirmPassword) return;

    if (password !== confirmPassword) {
      setError("Las contrasenas no coinciden");
      return;
    }

    if (password.length < 6) {
      setError("La contrasena debe tener al menos 6 caracteres");
      return;
    }

    setLoading(true);
    setError(null);

    const { error, needsConfirmation } = await signUp(email.trim(), password);
    if (error) {
      setError(error);
      setLoading(false);
    } else if (needsConfirmation) {
      setSuccess(true);
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
            Crea tu cuenta gratuita
          </p>
        </div>

        {success ? (
          <Card className="border-green-200 bg-green-50">
            <CardContent className="pt-6">
              <div className="text-center space-y-3">
                <CheckCircle
                  size={48}
                  className="mx-auto text-green-600"
                />
                <h2 className="text-lg font-semibold text-green-900">
                  Revisa tu email
                </h2>
                <p className="text-sm text-green-700">
                  Hemos enviado un enlace de confirmacion a{" "}
                  <strong>{email}</strong>. Haz clic en el enlace para activar
                  tu cuenta.
                </p>
                <Link
                  href="/login"
                  className="inline-block text-sm text-blue-600 hover:underline mt-2"
                >
                  Ir a iniciar sesion
                </Link>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Crear cuenta</CardTitle>
              <CardDescription>
                Registrate para empezar a clasificar productos
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
                    placeholder="Minimo 6 caracteres"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    autoComplete="new-password"
                    minLength={6}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium mb-1.5 block">
                    Confirmar contrasena
                  </label>
                  <Input
                    type="password"
                    placeholder="Repite la contrasena"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    autoComplete="new-password"
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
                  disabled={
                    loading ||
                    !email.trim() ||
                    !password ||
                    !confirmPassword
                  }
                >
                  {loading ? (
                    <>
                      <Loader2 size={18} className="mr-2 animate-spin" />
                      Creando cuenta...
                    </>
                  ) : (
                    <>
                      <UserPlus size={18} className="mr-2" />
                      Crear cuenta
                    </>
                  )}
                </Button>
              </form>

              <p className="text-sm text-muted-foreground text-center mt-4">
                Ya tienes cuenta?{" "}
                <Link
                  href="/login"
                  className="text-blue-600 hover:underline font-medium"
                >
                  Inicia sesion
                </Link>
              </p>
            </CardContent>
          </Card>
        )}

        <p className="text-xs text-muted-foreground text-center">
          <Link href="/" className="hover:underline">
            Volver al inicio
          </Link>
        </p>
      </div>
    </div>
  );
}

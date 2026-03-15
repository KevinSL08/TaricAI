import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { AuthProvider } from "@/components/auth/AuthProvider";
import { ThemeProvider } from "@/components/providers/ThemeProvider";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "TaricAI - Clasificacion Arancelaria con Inteligencia Artificial",
  description:
    "Agente de IA especializado en clasificacion TARIC para agencias de aduanas e importadores. Precision superior al 90% con validacion oficial.",
  keywords: [
    "TARIC",
    "clasificacion arancelaria",
    "aduanas",
    "importacion",
    "IA",
    "inteligencia artificial",
    "comercio exterior",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" suppressHydrationWarning>
      <head>
        {/* Always dark theme */}
        <script
          dangerouslySetInnerHTML={{
            __html: `document.documentElement.classList.add('dark')`,
          }}
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ThemeProvider>
          <AuthProvider>{children}</AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}

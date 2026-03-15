"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from "react";

type Theme = "light" | "dark" | "system";

interface ThemeContextType {
  theme: Theme;
  resolvedTheme: "light" | "dark";
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  theme: "system",
  resolvedTheme: "light",
  setTheme: () => {},
  toggleTheme: () => {},
});

export function useTheme() {
  return useContext(ThemeContext);
}

function getSystemTheme(): "light" | "dark" {
  if (typeof window === "undefined") return "light";
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>("system");
  const [resolvedTheme, setResolvedTheme] = useState<"light" | "dark">("light");
  const [mounted, setMounted] = useState(false);

  // Resolve the actual theme (system → light/dark)
  const resolveTheme = useCallback(
    (t: Theme): "light" | "dark" => {
      return t === "system" ? getSystemTheme() : t;
    },
    []
  );

  // Apply theme to DOM
  const applyTheme = useCallback((resolved: "light" | "dark") => {
    const root = document.documentElement;
    root.classList.remove("light", "dark");
    root.classList.add(resolved);
    setResolvedTheme(resolved);
  }, []);

  // Initialize from localStorage
  useEffect(() => {
    const stored = localStorage.getItem("taricai-theme") as Theme | null;
    const initial = stored || "system";
    setThemeState(initial);
    applyTheme(resolveTheme(initial));
    setMounted(true);
  }, [applyTheme, resolveTheme]);

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => {
      if (theme === "system") {
        applyTheme(getSystemTheme());
      }
    };
    mediaQuery.addEventListener("change", handler);
    return () => mediaQuery.removeEventListener("change", handler);
  }, [theme, applyTheme]);

  const setTheme = useCallback(
    (newTheme: Theme) => {
      setThemeState(newTheme);
      localStorage.setItem("taricai-theme", newTheme);
      applyTheme(resolveTheme(newTheme));
    },
    [applyTheme, resolveTheme]
  );

  const toggleTheme = useCallback(() => {
    const next = resolvedTheme === "light" ? "dark" : "light";
    setTheme(next);
  }, [resolvedTheme, setTheme]);

  // Prevent flash of wrong theme
  if (!mounted) {
    return <>{children}</>;
  }

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

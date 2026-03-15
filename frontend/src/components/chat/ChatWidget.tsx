"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import { MessageSquare, X, Send, Sparkles, Loader2 } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ChatMessage {
  role: "user" | "ai";
  text: string;
}

const WELCOME_SUGGESTIONS = [
  "¿Qué código TARIC tiene el aceite de oliva?",
  "¿Cuál es el arancel para camisetas de algodón?",
  "Clasifica: tornillos de acero inoxidable M8",
];

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (text?: string) => {
    const userMessage = (text || input).trim();
    if (!userMessage) return;

    setMessages((prev) => [...prev, { role: "user", text: userMessage }]);
    setInput("");
    setIsTyping(true);

    try {
      // Use the classify endpoint to get a real classification
      const res = await fetch(`${API_URL}/api/v1/classify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          description: userMessage,
          origin_country: "CN",
        }),
      });

      if (!res.ok) throw new Error("API error");

      const data = await res.json();
      const suggestion = data.suggestions?.[0];

      let aiText = "";
      if (suggestion) {
        aiText = `He clasificado tu producto:\n\n`;
        aiText += `📦 **Código TARIC:** ${data.top_code}\n`;
        aiText += `📝 **Descripción:** ${suggestion.description}\n`;
        aiText += `🎯 **Confianza:** ${Math.round(data.top_confidence * 100)}%\n`;
        if (suggestion.duty_rate) {
          aiText += `💰 **Arancel:** ${suggestion.duty_rate}\n`;
        }
        aiText += `📋 **Capítulo:** ${suggestion.chapter} | **Sección:** ${suggestion.section}\n`;
        aiText += `\n${suggestion.reasoning}`;
      } else {
        aiText = "No pude clasificar ese producto. Intenta con una descripción más detallada.";
      }

      setMessages((prev) => [...prev, { role: "ai", text: aiText }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          text: "Error de conexión. Verifica que el backend esté activo en localhost:8000.",
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-[60]">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            style={{ transformOrigin: "bottom right" }}
            className="absolute bottom-20 right-0 w-[350px] sm:w-[400px] h-[500px] bg-surface/90 backdrop-blur-2xl rounded-[2.5rem] border border-outline-variant shadow-2xl flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="p-6 border-b border-outline-variant flex items-center justify-between bg-cyan/5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-cyan/20 rounded-2xl flex items-center justify-center border border-cyan/30">
                  <Sparkles className="w-5 h-5 text-cyan" />
                </div>
                <div>
                  <div className="text-sm font-black tracking-tight">
                    TaricAI
                  </div>
                  <div className="text-[9px] font-bold text-cyan uppercase tracking-widest flex items-center gap-1">
                    <span className="w-1 h-1 bg-cyan rounded-full animate-pulse" />
                    Online
                  </div>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-surface-bright rounded-xl transition-colors"
              >
                <X className="w-5 h-5 text-on-surface/40" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center text-center space-y-6">
                  <div className="space-y-3 opacity-40">
                    <div className="w-16 h-16 bg-cyan/10 rounded-full flex items-center justify-center mx-auto">
                      <MessageSquare className="w-8 h-8 text-cyan" />
                    </div>
                    <p className="text-xs font-bold uppercase tracking-widest max-w-[200px]">
                      Pregúntame sobre clasificación TARIC
                    </p>
                  </div>
                  <div className="space-y-2 w-full">
                    {WELCOME_SUGGESTIONS.map((s) => (
                      <button
                        key={s}
                        onClick={() => handleSend(s)}
                        className="w-full text-left text-[11px] font-bold text-cyan/60 bg-cyan/5 px-4 py-2.5 rounded-xl border border-cyan/10 hover:bg-cyan/10 hover:text-cyan transition-all"
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {messages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  className={`flex ${
                    msg.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-line ${
                      msg.role === "user"
                        ? "bg-cyan text-[#0a0f14] font-bold rounded-tr-none"
                        : "bg-surface-bright border border-outline-variant text-on-surface rounded-tl-none"
                    }`}
                  >
                    {msg.text}
                  </div>
                </motion.div>
              ))}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-surface-bright border border-outline-variant p-4 rounded-2xl rounded-tl-none flex gap-1">
                    <span className="w-1.5 h-1.5 bg-cyan rounded-full animate-bounce" />
                    <span
                      className="w-1.5 h-1.5 bg-cyan rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    />
                    <span
                      className="w-1.5 h-1.5 bg-cyan rounded-full animate-bounce"
                      style={{ animationDelay: "0.4s" }}
                    />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input */}
            <div className="p-6 bg-surface-bright/50 border-t border-outline-variant">
              <div className="relative">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                  placeholder="Describe un producto..."
                  className="w-full bg-background/50 border border-outline-variant rounded-2xl py-4 pl-6 pr-14 text-sm focus:outline-none focus:border-cyan/50 transition-all"
                />
                <button
                  onClick={() => handleSend()}
                  disabled={!input.trim() || isTyping}
                  className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-cyan text-[#0a0f14] rounded-xl flex items-center justify-center hover:scale-105 active:scale-95 disabled:opacity-50 transition-all"
                >
                  {isTyping ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Toggle button */}
      <motion.button
        whileHover={{ scale: 1.1, rotate: 5 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(!isOpen)}
        className={`w-16 h-16 rounded-2xl flex items-center justify-center shadow-2xl transition-all relative group ${
          isOpen
            ? "bg-surface-bright border border-outline-variant"
            : "kinetic-gradient"
        }`}
      >
        {isOpen ? (
          <X className="w-6 h-6 text-on-surface" />
        ) : (
          <>
            <MessageSquare className="w-6 h-6 text-[#0a0f14] relative z-10" />
            <div className="absolute inset-0 bg-white/20 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-orange rounded-full border-2 border-background flex items-center justify-center">
              <Sparkles className="w-2 h-2 text-white" />
            </div>
          </>
        )}
      </motion.button>
    </div>
  );
}

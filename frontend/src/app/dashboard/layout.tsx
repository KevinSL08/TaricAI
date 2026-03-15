import { Sidebar } from "@/components/dashboard/Sidebar";
import { ChatWidget } from "@/components/chat/ChatWidget";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background mesh-bg">
      <Sidebar />
      <main className="lg:ml-64 min-h-screen relative z-10">
        <div className="p-6 lg:p-8">{children}</div>
      </main>
      <ChatWidget />
    </div>
  );
}

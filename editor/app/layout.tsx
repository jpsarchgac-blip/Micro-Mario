import type { Metadata } from "next";
import "./globals.css";
import { ProjectProvider } from "@/lib/project-context";
import { Header } from "@/components/shared/Header";

export const metadata: Metadata = {
  title: "Micro-Mario Editor",
  description: "Custom map / block / BGM authoring tool for Micro-Mario",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-bg text-gray-100">
        <ProjectProvider>
          <Header />
          <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
        </ProjectProvider>
      </body>
    </html>
  );
}

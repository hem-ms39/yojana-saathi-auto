import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "../contexts/auth-context";
import { NavBar } from "../components/nav-bar";

export const metadata: Metadata = {
  title: "Yojana Saathi — Find every government scheme you deserve",
  description:
    "AI-powered multi-agent system that discovers government schemes you qualify for, in your language.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-slate-50" suppressHydrationWarning>
        <AuthProvider>
          <NavBar />
          <main>{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}

import "./globals.css";
import type { Metadata } from "next";
import { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Zoho Support Copilot",
  description: "Mock support copilot for answer and similar ticket retrieval.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main className="mx-auto min-h-screen max-w-[1440px] p-6 lg:p-8">{children}</main>
      </body>
    </html>
  );
}

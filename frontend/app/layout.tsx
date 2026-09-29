import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Balladesh — Bangla book reading assistant",
  description:
    "Ask grounded questions about the Bangla book Balladesh. Answers come with source pages.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="bn">
      <body className="antialiased">{children}</body>
    </html>
  );
}

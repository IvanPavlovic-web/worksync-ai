import type { Metadata } from "next";
import { ThemeProvider } from "@/components/ThemeProvider";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000",
  ),
  title: {
    default: "WorkSync â€” Posao u BiH, regionu i remote",
    template: "%s | WorkSync",
  },
  description:
    "NajveÄ‡a platforma za posao u Bosni i Hercegovini, regionu i remote. " +
    "Pametni AI matching, automatska prijava, poslovi u NjemaÄkoj, Austriji i EU.",
  keywords: [
    "posao",
    "posao BiH",
    "posao Sarajevo",
    "posao Banja Luka",
    "remote posao",
    "IT posao",
    "programer posao",
    "posao NjemaÄka",
    "posao Austrija",
    "rad u inostranstvu",
    "zaposlenje",
    "karijera",
    "rad od kuÄ‡e",
  ],
  openGraph: {
    type: "website",
    locale: "bs_BA",
    siteName: "WorkSync",
    title: "WorkSync â€” Posao u BiH i regionu + remote",
    description: "Pametna pretraga poslova za BiH, region i inostranstvo.",
  },
  twitter: { card: "summary_large_image" },
  robots: { index: true, follow: true },
};

const orgSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "WorkSync",
  url: process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000",
  areaServed: [
    { "@type": "Country", name: "Bosna i Hercegovina" },
    { "@type": "Country", name: "Hrvatska" },
    { "@type": "Country", name: "Srbija" },
    { "@type": "Country", name: "NjemaÄka" },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="bs" suppressHydrationWarning>
      <body>
        <ThemeProvider>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(orgSchema) }}
        />
        <header className="sticky top-0 z-20 border-b bg-[color:var(--background)]/85 backdrop-blur text-[color:var(--foreground)]">
          <nav className="max-w-6xl mx-auto flex items-center justify-between px-4 h-14">
            <Link href="/" className="text-xl font-bold">
              WorkSync
            </Link>
            <div className="flex items-center gap-6 text-sm">
              <Link href="/poslovi">Poslovi</Link>
              <Link href="/poslovi?work_mode=remote">Remote</Link>
              <Link href="/blog">Blog</Link>
              <Link href="/dashboard">Dashboard</Link>
              <Link href="/kanban">Prijave</Link>
              <Link
                href="/login"
                className="ui-button text-xs px-3 py-1.5"
              >
                Prijava
              </Link>
            </div>
          </nav>
        </header>
        <main className="min-h-screen">{children}</main>
        <footer className="border-t border-slate-800 bg-slate-950 text-slate-400 py-8 text-sm">
          <div className="max-w-6xl mx-auto px-4">
            Â© {new Date().getFullYear()} WorkSync â€” Posao u BiH, regionu i
            remote.
          </div>
        </footer>
        </ThemeProvider>
      </body>
    </html>
  );
}


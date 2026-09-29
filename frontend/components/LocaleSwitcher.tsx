"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";

const LOCALES = [
  { code: "bs", label: "🇧🇦 Bosanski" },
  { code: "hr", label: "🇭🇷 Hrvatski" },
  { code: "sr", label: "🇷🇸 Srpski" },
  { code: "en", label: "🇬🇧 English" },
  { code: "de", label: "🇩🇪 Deutsch" },
];

export function LocaleSwitcher() {
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();
  const current = params.get("lang") || "bs";

  function setLocale(code: string) {
    const sp = new URLSearchParams(params.toString());
    sp.set("lang", code);
    router.push(`${pathname}?${sp.toString()}`);
  }

  return (
    <select
      value={current}
      onChange={(e) => setLocale(e.target.value)}
      className="bg-slate-800 text-white text-sm rounded px-2 py-1 border border-slate-700"
    >
      {LOCALES.map((l) => (
        <option key={l.code} value={l.code}>
          {l.label}
        </option>
      ))}
    </select>
  );
}


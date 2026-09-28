"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Search, X } from "lucide-react";
import { Button, Input } from "@/components/ui";

const fields = [["work_mode", "Način rada"], ["category", "Kategorija"], ["country", "Država"], ["city", "Grad"], ["seniority", "Nivo"]] as const;
export function JobFilters() {
  const router = useRouter(); const pathname = usePathname(); const params = useSearchParams();
  const [query, setQuery] = useState(params.get("query") ?? params.get("q") ?? "");
  useEffect(() => { const timer = setTimeout(() => { if (query === (params.get("query") ?? params.get("q") ?? "")) return; const next = new URLSearchParams(params.toString()); query ? next.set("query", query) : next.delete("query"); next.delete("q"); router.replace(`${pathname}?${next}`); }, 250); return () => clearTimeout(timer); }, [query, params, pathname, router]);
  function clear() { setQuery(""); router.replace(pathname); }
  return <aside className="w-full md:w-64 space-y-4" aria-label="Filteri">
    <div className="relative"><Search size={16} className="absolute left-3 top-3 text-[color:var(--muted)]" /><Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Pretraži poslove" className="pl-9" /></div>
    {fields.map(([key, label]) => <label key={key} className="block text-sm"><span className="mb-1 block">{label}</span><select className="ui-input" value={params.get(key) ?? ""} onChange={(e) => { const next = new URLSearchParams(params.toString()); e.target.value ? next.set(key, e.target.value) : next.delete(key); router.replace(`${pathname}?${next}`); }}><option value="">Sve</option><option value="remote">Remote</option><option value="hybrid">Hybrid</option><option value={key === "seniority" ? "senior" : key === "category" ? "it" : "BA"}>{key === "seniority" ? "Senior" : key === "category" ? "IT" : "Bosna i Hercegovina"}</option></select></label>)}
    <Button type="button" onClick={clear} className="bg-transparent text-[color:var(--foreground)] border"><X size={15} /> Očisti filtere</Button>
  </aside>;
}

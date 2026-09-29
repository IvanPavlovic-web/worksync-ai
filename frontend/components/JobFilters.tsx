"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { Search, SlidersHorizontal, X } from "lucide-react";
import { Button, Input } from "@/components/ui";

type Facet = { value: string; count: number; country?: string };
type Props = { facets: Record<string, Facet[]> };
type FilterState = Record<string, string | boolean>;

const staticOptions: Record<string, [string, string][]> = {
  work_mode: [["remote", "Remote"], ["hybrid", "Hibridno"], ["onsite", "U kancelariji"]],
  category: [["it", "IT"], ["marketing", "Marketing"], ["sales", "Prodaja"], ["customer-support", "Podrška"], ["construction", "Građevina"], ["design", "Dizajn"]],
  seniority: [["junior", "Junior"], ["mid", "Medior"], ["senior", "Senior"], ["lead", "Lead"]],
  employment_type: [["full-time", "Puno radno vrijeme"], ["part-time", "Nepuno radno vrijeme"], ["contract", "Ugovor"], ["internship", "Praksa"]],
};

export function JobFilters({ facets }: Props) {
  const router = useRouter(); const pathname = usePathname(); const params = useSearchParams();
  const [draft, setDraft] = useState<FilterState>({});
  const country = String(draft.country || "");

  useEffect(() => {
    const next: FilterState = {};
    ["query", "work_mode", "category", "country", "city", "seniority", "employment_type", "source", "posted_within", "sort"].forEach((key) => { const value = params.get(key); if (value) next[key] = value; });
    ["visa_only", "housing_only", "relocation_only"].forEach((key) => { if (params.get(key) === "true") next[key] = true; });
    setDraft(next);
  }, [params]);

  const cities = useMemo(() => {
    const source = (facets.city_by_country || facets.city || []).filter((item) => !country || item.country === country);
    const seen = new Set<string>();
    return source.filter((item) => {
      if (seen.has(item.value)) return false;
      seen.add(item.value);
      return true;
    });
  }, [facets, country]);
  const set = (key: string, value: string | boolean) => setDraft((current) => ({ ...current, [key]: value }));
  const options = (key: string) => facets[key]?.length ? facets[key].map((item) => [item.value, `${item.value} (${item.count})`] as [string, string]) : staticOptions[key] || [];

  function apply(event: FormEvent) {
    event.preventDefault();
    const next = new URLSearchParams();
    Object.entries(draft).forEach(([key, value]) => { if (value !== "" && value !== false) next.set(key, String(value)); });
    next.set("page", "1");
    router.push(`${pathname}?${next}`);
  }

  function clear() { setDraft({}); router.push(pathname); }

  return <form className="w-full md:w-72 shrink-0 ui-card p-5 space-y-4 sticky top-24" onSubmit={apply}>
    <div className="flex items-center justify-between"><div className="flex items-center gap-2 font-semibold"><SlidersHorizontal size={18} /> Filteri</div><button type="button" onClick={clear} className="text-slate-400 hover:text-[color:var(--foreground)]" aria-label="Očisti filtere"><X size={18} /></button></div>
    <div className="relative"><Search size={16} className="absolute left-3 top-3.5 text-slate-400" /><Input value={String(draft.query || "")} onChange={(e) => set("query", e.target.value)} placeholder="Pretraži naziv ili firmu" className="pl-9" /></div>
    <FilterSelect label="Način rada" value={String(draft.work_mode || "")} onChange={(value) => set("work_mode", value)} options={options("work_mode")} />
    <FilterSelect label="Kategorija" value={String(draft.category || "")} onChange={(value) => set("category", value)} options={options("category")} />
    <FilterSelect label="Država" value={country} onChange={(value) => { set("country", value); set("city", ""); }} options={options("country")} />
    <FilterSelect label="Grad" value={String(draft.city || "")} onChange={(value) => set("city", value)} options={cities.map((item) => [item.value, `${item.value} (${item.count})`])} disabled={!country} />
    <FilterSelect label="Nivo iskustva" value={String(draft.seniority || "")} onChange={(value) => set("seniority", value)} options={options("seniority")} />
    <FilterSelect label="Tip zaposlenja" value={String(draft.employment_type || "")} onChange={(value) => set("employment_type", value)} options={options("employment_type")} />
    <FilterSelect label="Izvor oglasa" value={String(draft.source || "")} onChange={(value) => set("source", value)} options={options("source")} />
    <FilterSelect label="Objavljeno" value={String(draft.posted_within || "")} onChange={(value) => set("posted_within", value)} options={[["1", "Danas"], ["7", "Ove sedmice"], ["30", "Ovaj mjesec"], ["365", "Ove godine"]]} />
    <div className="filter-checks space-y-2 border-t border-[color:var(--separator)] pt-4"><Check label="Viza / sponzorstvo" value={Boolean(draft.visa_only)} onChange={(value) => set("visa_only", value)} /><Check label="Obezbijeđen smještaj" value={Boolean(draft.housing_only)} onChange={(value) => set("housing_only", value)} /><Check label="Podrška za relokaciju" value={Boolean(draft.relocation_only)} onChange={(value) => set("relocation_only", value)} /></div>
    <Button type="submit" className="w-full">Primijeni filtere</Button>
    <button type="button" onClick={clear} className="w-full text-sm text-slate-400 hover:text-[color:var(--foreground)]">Očisti sve</button>
  </form>;
}

function FilterSelect({ label, value, onChange, options, disabled = false }: { label: string; value: string; onChange: (value: string) => void; options: [string, string][]; disabled?: boolean }) {
  return <label className="block text-sm"><span className="mb-1.5 block text-slate-400">{label}</span><select className="ui-input" value={value} disabled={disabled} onChange={(event) => onChange(event.target.value)}><option value="">Sve opcije</option>{options.map(([option, text], index) => <option key={`${option}-${index}`} value={option}>{text}</option>)}</select></label>;
}

function Check({ label, value, onChange }: { label: string; value: boolean; onChange: (value: boolean) => void }) {
  return <label className="flex items-center gap-2 text-sm cursor-pointer"><input type="checkbox" checked={value} onChange={(event) => onChange(event.target.checked)} /> <span>{label}</span></label>;
}

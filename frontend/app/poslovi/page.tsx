import Link from "next/link";
import { serverFetch } from "@/lib/api";
import { JobFilters } from "@/components/JobFilters";

export const dynamic = "force-dynamic";

type Facet = { value: string; count: number };
type Job = {
  id: string; slug: string; title: string; company: string; city?: string;
  location: string; work_mode: string; category?: string; country_code?: string;
  seniority?: string; visa_sponsorship?: boolean; housing_provided?: boolean;
  relocation_support?: boolean; salary_min?: number; salary_max?: number; currency?: string;
};

export const metadata = {
  title: "Poslovi — BiH, region i remote",
  description: "Pretraži poslove po državi, gradu, načinu rada, iskustvu, plati i podršci za relokaciju.",
};

export default async function JobsPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const params = await searchParams;
  const get = (key: string) => typeof params[key] === "string" ? params[key] as string : "";
  const page = Math.max(1, Number(get("page") || "1"));
  const pageSize = 30;
  const qs = new URLSearchParams();
  const keys = ["query", "q", "work_mode", "category", "country", "city", "seniority", "employment_type", "source", "visa_only", "housing_only", "relocation_only", "posted_within", "sort"];
  keys.forEach((key) => { const value = get(key); if (value) qs.set(key, value); });
  qs.set("limit", String(pageSize));
  qs.set("offset", String((page - 1) * pageSize));
  const data = await serverFetch<{ total: number; items: Job[]; facets: Record<string, Facet[]> }>(`/public/jobs/search?${qs}`, 0);
  const total = data?.total ?? 0;
  const pages = Math.max(1, Math.ceil(total / pageSize));
  const current = Math.min(page, pages);
  const pageHref = (next: number) => {
    const nextParams = new URLSearchParams(params as Record<string, string>);
    nextParams.set("page", String(next));
    return `/poslovi?${nextParams}`;
  };

  return <main className="jobs-shell max-w-6xl mx-auto px-4 py-10">
    <header className="jobs-heading mb-8">
      <p className="eyebrow text-slate-400 mb-3">WORKSYNC / PRETRAGA</p>
      <h1 className="text-3xl font-bold mb-2">Pronađi posao koji ti odgovara</h1>
      <p className="text-slate-400">{total.toLocaleString("bs-BA")} aktivnih oglasa iz provjerenih izvora.</p>
    </header>

    <div className="flex flex-col md:flex-row gap-8 items-start">
      <JobFilters facets={data?.facets ?? {}} />
      <section className="flex-1 min-w-0">
        <div className="jobs-toolbar flex items-center justify-between mb-4">
          <p className="text-sm text-slate-400">{total ? `${(current - 1) * pageSize + 1}–${Math.min(current * pageSize, total)} od ${total.toLocaleString("bs-BA")}` : "Nema rezultata"}</p>
          <span className="text-sm text-slate-400">Stranica {current} / {pages}</span>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {data?.items?.map((job) => <Link key={job.id} href={`/poslovi/${job.slug}`} className="job-result ui-card block">
            <div className="flex items-start justify-between gap-3"><div><h2 className="text-lg font-semibold mb-1">{job.title}</h2><p className="text-slate-400 text-sm">{job.company} · {job.city || job.location}</p></div><span className="ui-badge">{job.work_mode || "posao"}</span></div>
            <div className="flex flex-wrap gap-2 mt-4 text-xs text-slate-400">{job.category && <span>{job.category}</span>}{job.seniority && <span>· {job.seniority}</span>}{job.visa_sponsorship && <span className="text-emerald-500">· Viza</span>}{job.housing_provided && <span className="text-emerald-500">· Smještaj</span>}{job.relocation_support && <span className="text-emerald-500">· Relokacija</span>}</div>
          </Link>)}
        </div>
        {!data?.items?.length && <div className="ui-card text-center py-16"><h2>Nema pronađenih oglasa</h2><p className="text-slate-400 mb-5">Pokušaj širi pojam ili ukloni neki filter.</p><Link href="/poslovi" className="ui-button inline-flex">Prikaži sve poslove</Link></div>}
        {pages > 1 && <nav className="jobs-pagination flex items-center justify-center gap-2 mt-8" aria-label="Paginacija">
          {current > 1 && <Link className="ui-button" href={pageHref(current - 1)}>← Prethodna</Link>}
          <span className="ui-badge">{current} / {pages}</span>
          {current < pages && <Link className="ui-button" href={pageHref(current + 1)}>Sljedeća →</Link>}
        </nav>}
      </section>
    </div>
  </main>;
}

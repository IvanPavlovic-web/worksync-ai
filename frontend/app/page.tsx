import Link from "next/link";
import { serverFetch } from "@/lib/api";

export const dynamic = "force-dynamic";

interface Job {
  id: string; slug: string; title: string; company: string; location: string; city: string;
  work_mode: string; source?: string; salary_min?: number; salary_max?: number; currency?: string;
}

function JobCard({ job }: { job: Job }) {
  return (
    <Link href={`/poslovi/${job.slug}`} className="home-job-card ui-card block">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0"><h3 className="font-semibold leading-snug">{job.title}</h3><p className="text-slate-400 text-sm mt-2">{job.company} · {job.city || job.location}</p></div>
        <span className="ui-badge shrink-0">{job.work_mode || "Posao"}</span>
      </div>
      <div className="flex items-center justify-between gap-3 mt-8 text-sm text-slate-400"><span>{job.source || "WorkSync"}</span>{job.salary_max && <span className="text-emerald-500">{job.salary_min}–{job.salary_max} {job.currency}</span>}</div>
    </Link>
  );
}

function JobGrid({ jobs }: { jobs?: Job[] }) {
  return <div className="grid grid-cols-1 md:grid-cols-3 gap-4">{jobs?.map((job) => <JobCard key={job.id} job={job} />)}</div>;
}

export default async function Home() {
  const [latest, remote, germany] = await Promise.all([
    serverFetch<{ items: Job[] }>("/public/jobs/latest?limit=9", 0),
    serverFetch<{ items: Job[] }>("/public/jobs/by-filter?work_mode=remote&limit=6", 0),
    serverFetch<{ items: Job[] }>("/public/jobs/by-country?country=DE&limit=6", 0),
  ]);
  return <main className="home-shell max-w-6xl mx-auto px-4">
    <section className="home-hero">
      <div><p className="eyebrow text-slate-400 mb-5">WORKSYNC / KARIJERA</p><h1>Pronađi posao koji odgovara tvom životu.</h1></div>
      <div className="home-hero-copy"><p>Pretraži provjerene oglase iz BiH, regiona, Evrope i remote tržišta. Filtriraj uslove koji su ti zaista važni.</p><Link href="/poslovi" className="ui-button inline-flex mt-7">Pretraži oglase</Link></div>
    </section>
    <section className="home-section"><div className="home-section-heading"><h2>Najnoviji oglasi</h2><Link href="/poslovi">Svi oglasi</Link></div><JobGrid jobs={latest?.items} /></section>
    <section className="home-section"><div className="home-section-heading"><h2>Remote prilike</h2><Link href="/poslovi?work_mode=remote">Prikaži remote</Link></div><JobGrid jobs={remote?.items} /></section>
    <section className="home-section"><div className="home-section-heading"><h2>Poslovi u Njemačkoj</h2><Link href="/poslovi?country=DE">Prikaži Njemačku</Link></div><JobGrid jobs={germany?.items} /></section>
    <section className="home-section max-w-3xl"><p className="eyebrow text-slate-400 mb-4">JEDNO MJESTO ZA PRETRAGU</p><h2>Više izvora, jasniji uslovi.</h2><p className="text-slate-400 mt-4">WorkSync objedinjuje oglase sa regionalnih portala, međunarodnih job boardova i direktnih career stranica kompanija. Svaki oglas možeš filtrirati po lokaciji, načinu rada, vizi, smještaju i relokaciji.</p></section>
  </main>;
}

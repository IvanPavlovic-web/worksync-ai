import Link from "next/link";
import { serverFetch } from "@/lib/api";

export const revalidate = 300;

interface Job {
  id: string;
  slug: string;
  title: string;
  company: string;
  location: string;
  city: string;
  work_mode: string;
  salary_min?: number;
  salary_max?: number;
  currency?: string;
}

function JobCard({ job }: { job: Job }) {
  return (
    <Link
      href={`/poslovi/${job.slug}`}
      className="block bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl p-4 transition"
    >
      <h3 className="font-semibold">{job.title}</h3>
      <p className="text-slate-400 text-sm mt-1">
        {job.company} Â· {job.city || job.location}
      </p>
      {job.work_mode && (
        <span className="inline-block mt-2 text-xs bg-slate-800 px-2 py-0.5 rounded">
          {job.work_mode}
        </span>
      )}
      {job.salary_max && (
        <p className="text-emerald-400 text-sm mt-2">
          {job.salary_min}â€“{job.salary_max} {job.currency}
        </p>
      )}
    </Link>
  );
}

export default async function Home() {
  const [latest, remote, germany] = await Promise.all([
    serverFetch<{ items: Job[] }>("/public/jobs/latest?limit=9"),
    serverFetch<{ items: Job[] }>(
      "/public/jobs/by-filter?work_mode=remote&limit=6",
    ),
    serverFetch<{ items: Job[] }>("/public/jobs/by-country?country=DE&limit=6"),
  ]);

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <section className="text-center py-16">
        <h1 className="text-4xl md:text-5xl font-bold">
          NaÄ‘i posao u BiH, regionu ili{" "}
          <span className="text-indigo-500">remote</span>
        </h1>
        <p className="mt-4 text-lg text-slate-400 max-w-2xl mx-auto">
          AI matching za BiH i Balkan â€” poslovi iz 30+ izvora, automatska
          prijava, podrÅ¡ka za vizu i relokaciju.
        </p>
        <Link
          href="/poslovi"
          className="inline-block mt-6 bg-indigo-600 hover:bg-indigo-500 px-6 py-3 rounded-lg font-medium"
        >
          PretraÅ¾i poslove
        </Link>
      </section>

      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-4">Najnoviji poslovi</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {latest?.items?.map((j) => (
            <JobCard key={j.id} job={j} />
          ))}
        </div>
      </section>

      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-4">ðŸŒ Remote poslovi</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {remote?.items?.map((j) => (
            <JobCard key={j.id} job={j} />
          ))}
        </div>
      </section>

      <section className="mb-12">
        <h2 className="text-2xl font-bold mb-4">ðŸ‡©ðŸ‡ª Posao u NjemaÄkoj</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {germany?.items?.map((j) => (
            <JobCard key={j.id} job={j} />
          ))}
        </div>
      </section>

      <section className="mt-16 prose prose-invert max-w-none">
        <h2>ZaÅ¡to WorkSync?</h2>
        <p>
          WorkSync je prva platforma za BiH i Balkan koja kombinuje AI matching
          sa automatskom prijavom. Pokrivamo 30+ izvora â€” Posao.ba, MojPosao.ba,
          EURES, Make it in Germany, Greenhouse, Lever i druge.
        </p>
        <h3>Za kandidate iz BiH i regiona</h3>
        <ul>
          <li>PronaÄ‘i remote posao koji prima radnike iz BiH</li>
          <li>Saznaj koji poslovi nude vizu i smjeÅ¡taj u NjemaÄkoj</li>
          <li>Automatski popuni prijavu jednim klikom</li>
          <li>AI generiÅ¡e propratno pismo na njemaÄkom ili engleskom</li>
        </ul>
      </section>
    </div>
  );
}


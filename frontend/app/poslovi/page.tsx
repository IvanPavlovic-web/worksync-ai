import Link from "next/link";
import { serverFetch } from "@/lib/api";
import { JobFilters } from "@/components/JobFilters";
import { Suspense } from "react";

export const revalidate = 300;

export const metadata = {
  title: "Svi poslovi â€” BiH, region i remote",
  description:
    "PretraÅ¾i sve aktivne poslove u Bosni i Hercegovini, regionu i remote. " +
    "Filter po gradu, kategoriji i tipu rada.",
};

interface Job {
  id: string;
  slug: string;
  title: string;
  company: string;
  city?: string;
  location: string;
  work_mode: string;
}

export default async function JobsPage({
  searchParams,
}: {
  searchParams: {
    q?: string;
    query?: string;
    work_mode?: string;
    category?: string;
    city?: string;
  };
}) {
  const qs = new URLSearchParams();
  if (searchParams.query || searchParams.q) qs.set("query", searchParams.query || searchParams.q || "");
  if (searchParams.work_mode) qs.set("work_mode", searchParams.work_mode);
  if (searchParams.category) qs.set("category", searchParams.category);
  if (searchParams.city) qs.set("city", searchParams.city);
  qs.set("limit", "30");

  const data = await serverFetch<{ total: number; items: Job[] }>(
    `/public/jobs/search?${qs.toString()}`,
    300,
  );

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Svi poslovi</h1>
      <p className="text-slate-400 mb-6">
        Ukupno {data?.total ?? 0} aktivnih oglasa
      </p>

      <div className="flex flex-wrap gap-2 mb-6">
        <Link
          href="/poslovi"
          className="bg-slate-800 px-3 py-1 rounded text-sm"
        >
          Svi
        </Link>
        <Link
          href="/poslovi?work_mode=remote"
          className="bg-slate-800 px-3 py-1 rounded text-sm"
        >
          Remote
        </Link>
        <Link
          href="/poslovi?work_mode=hybrid"
          className="bg-slate-800 px-3 py-1 rounded text-sm"
        >
          Hybrid
        </Link>
        <Link
          href="/poslovi?category=it"
          className="bg-slate-800 px-3 py-1 rounded text-sm"
        >
          IT
        </Link>
        <Link
          href="/poslovi?category=marketing"
          className="bg-slate-800 px-3 py-1 rounded text-sm"
        >
          Marketing
        </Link>
        <Link
          href="/poslovi?category=construction"
          className="bg-slate-800 px-3 py-1 rounded text-sm"
        >
          GraÄ‘evina
        </Link>
      </div>

      <div className="flex flex-col md:flex-row gap-8">
      <Suspense fallback={<div className="w-64 h-40" />}><JobFilters /></Suspense>
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4">
        {data?.items?.map((j) => (
          <Link
            key={j.id}
            href={`/poslovi/${j.slug}`}
            className="block bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl p-4"
          >
            <h3 className="font-semibold">{j.title}</h3>
            <p className="text-slate-400 text-sm mt-1">
              {j.company} Â· {j.city || j.location}
            </p>
            <span className="inline-block mt-2 text-xs bg-slate-800 px-2 py-0.5 rounded">
              {j.work_mode}
            </span>
          </Link>
        ))}
      </div>
      </div>
    </div>
  );
}


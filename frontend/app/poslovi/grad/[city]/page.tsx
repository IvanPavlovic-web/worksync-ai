import Link from "next/link";
import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { serverFetch } from "@/lib/api";

export const revalidate = 1800;

const CITY_NAMES: Record<string, string> = {
  sarajevo: "Sarajevu",
  "banja-luka": "Banjoj Luci",
  tuzla: "Tuzli",
  mostar: "Mostaru",
  zenica: "Zenici",
  bihac: "BihaÄ‡u",
  brcko: "BrÄkom",
  gorazde: "GoraÅ¾du",
};

export async function generateMetadata({
  params,
}: {
  params: { city: string };
}): Promise<Metadata> {
  const name = CITY_NAMES[params.city] || params.city;
  return {
    title: `Posao u ${name} â€” najnoviji oglasi`,
    description: `Aktuelni poslovi u ${name}. IT, marketing, prodaja, ugostiteljstvo i drugo. AÅ¾urirano dnevno.`,
    alternates: { canonical: `/poslovi/grad/${params.city}` },
  };
}

export default async function CityPage({
  params,
}: {
  params: { city: string };
}) {
  const name = CITY_NAMES[params.city];
  if (!name) notFound();

  const data = await serverFetch<{ total: number; items: any[] }>(
    `/public/jobs/by-filter?city=${encodeURIComponent(params.city)}&limit=30`,
    1800,
  );

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-2">Posao u {name}</h1>
      <p className="text-slate-400 mb-6">
        Ukupno {data?.total ?? 0} aktivnih oglasa
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data?.items?.map((j: any) => (
          <Link
            key={j.id}
            href={`/poslovi/${j.slug}`}
            className="block bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl p-4"
          >
            <h3 className="font-semibold">{j.title}</h3>
            <p className="text-slate-400 text-sm mt-1">{j.company}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}


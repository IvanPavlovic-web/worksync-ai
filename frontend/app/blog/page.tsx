import Link from "next/link";
import type { Metadata } from "next";
import { serverFetch } from "@/lib/api";

export const revalidate = 3600;

export const metadata: Metadata = {
  title: "Blog â€” vodiÄi za posao u BiH i inostranstvu",
  description:
    "PraktiÄni vodiÄi: radna dozvola NjemaÄka, CV, intervjui, plate, " +
    "remote poslovi i relokacija. Sve Å¡to trebaÅ¡ znati kao kandidat iz BiH.",
  alternates: { canonical: "/blog" },
};

interface Post {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  category: string;
  published_at: string;
  cover_image?: string;
}

export default async function BlogIndex() {
  const data = await serverFetch<{ total: number; items: Post[] }>(
    "/blog?locale=bs&limit=30",
    3600,
  );

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-4xl font-bold mb-3">VodiÄi za karijeru</h1>
      <p className="text-slate-400 mb-10">
        Sve o poslu u BiH, regionu i inostranstvu â€” od CV-a do radne dozvole.
      </p>

      <div className="space-y-8">
        {data?.items?.map((p) => (
          <article
            key={p.id}
            className="border-b border-slate-800 pb-6 last:border-0"
          >
            <Link href={`/blog/${p.slug}`} className="group">
              <h2 className="text-2xl font-bold group-hover:text-indigo-400">
                {p.title}
              </h2>
            </Link>
            <p className="text-slate-400 mt-2">{p.excerpt}</p>
            <p className="text-xs text-slate-500 mt-2">
              {new Date(p.published_at).toLocaleDateString("bs-BA", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}{" "}
              Â· {p.category}
            </p>
          </article>
        ))}
      </div>

      {(!data || data.items.length === 0) && (
        <p className="text-slate-400">
          Blog postovi se generiÅ¡u. Provjeri za par sati.
        </p>
      )}
    </div>
  );
}


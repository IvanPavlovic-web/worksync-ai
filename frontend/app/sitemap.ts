import type { MetadataRoute } from "next";

const BASE = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const staticPages: MetadataRoute.Sitemap = [
    { url: `${BASE}/`, changeFrequency: "daily", priority: 1.0 },
    { url: `${BASE}/poslovi`, changeFrequency: "hourly", priority: 0.95 },
    {
      url: `${BASE}/poslovi?work_mode=remote`,
      changeFrequency: "hourly",
      priority: 0.9,
    },
    { url: `${BASE}/blog`, changeFrequency: "daily", priority: 0.8 },
  ];

  const cities = [
    "sarajevo",
    "banja-luka",
    "tuzla",
    "mostar",
    "zenica",
    "bihac",
    "brcko",
    "gorazde",
  ];
  const cityPages = cities.map((c) => ({
    url: `${BASE}/poslovi/grad/${c}`,
    changeFrequency: "daily" as const,
    priority: 0.85,
  }));

  const categories = [
    "it",
    "marketing",
    "dizajn",
    "prodaja",
    "finansije",
    "podrska",
    "gradjevinarstvo",
    "ugostiteljstvo",
  ];
  const categoryPages = categories.map((c) => ({
    url: `${BASE}/poslovi?category=${c}`,
    changeFrequency: "daily" as const,
    priority: 0.8,
  }));

  let jobPages: MetadataRoute.Sitemap = [];
  try {
    const r = await fetch(
      `${process.env.API_URL}/public/jobs/sitemap?limit=5000`,
      {
        next: { revalidate: 3600 },
      },
    );
    if (r.ok) {
      const jobs = (await r.json()) as { slug: string; updated_at?: string }[];
      jobPages = jobs.map((j) => ({
        url: `${BASE}/poslovi/${j.slug}`,
        lastModified: j.updated_at ? new Date(j.updated_at) : undefined,
        changeFrequency: "weekly" as const,
        priority: 0.7,
      }));
    }
  } catch {}

  return [...staticPages, ...cityPages, ...categoryPages, ...jobPages];
}


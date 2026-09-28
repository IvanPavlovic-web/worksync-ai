import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { serverFetch } from "@/lib/api";

interface Job {
  id: string;
  slug: string;
  title: string;
  company: string;
  location: string;
  city: string;
  work_mode: string;
  category: string;
  seniority: string;
  description: string;
  salary_min?: number;
  salary_max?: number;
  currency?: string;
  url: string;
  posted_at?: string;
  expires_at?: string;
  seo_title?: string;
  seo_description?: string;
  allowed_countries?: string[];
  visa_sponsorship?: boolean;
  housing_provided?: boolean;
}

async function getJob(slug: string) {
  return serverFetch<Job>(`/public/jobs/${slug}`, 3600);
}

export async function generateMetadata({
  params,
}: {
  params: { slug: string };
}): Promise<Metadata> {
  const job = await getJob(params.slug);
  if (!job) return { title: "Posao nije naÄ‘en" };
  const title =
    job.seo_title ||
    `${job.title} â€” ${job.company} (${job.city || job.location})`;
  const description =
    job.seo_description ||
    `${job.company} traÅ¾i ${job.title} u ${job.city || job.location}. ` +
      `${job.work_mode === "remote" ? "Remote posao. " : ""}Prijavi se brzo preko WorkSync.`;
  return {
    title,
    description,
    alternates: { canonical: `/poslovi/${job.slug}` },
    openGraph: { title, description, type: "article" },
  };
}

export default async function JobPage({
  params,
}: {
  params: { slug: string };
}) {
  const job = await getJob(params.slug);
  if (!job) notFound();

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "JobPosting",
    title: job.title,
    description: job.description,
    datePosted: job.posted_at,
    validThrough: job.expires_at,
    employmentType: "FULL_TIME",
    hiringOrganization: { "@type": "Organization", name: job.company },
    jobLocation: {
      "@type": "Place",
      address: {
        "@type": "PostalAddress",
        addressLocality: job.city || job.location,
      },
    },
    jobLocationType: job.work_mode === "remote" ? "TELECOMMUTE" : undefined,
    baseSalary:
      job.salary_max && job.currency
        ? {
            "@type": "MonetaryAmount",
            currency: job.currency,
            value: {
              "@type": "QuantitativeValue",
              minValue: job.salary_min,
              maxValue: job.salary_max,
              unitText: "YEAR",
            },
          }
        : undefined,
  };

  const breadcrumbs = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "PoÄetna", item: "/" },
      { "@type": "ListItem", position: 2, name: "Poslovi", item: "/poslovi" },
      {
        "@type": "ListItem",
        position: 3,
        name: job.title,
        item: `/poslovi/${job.slug}`,
      },
    ],
  };

  return (
    <article className="max-w-4xl mx-auto px-4 py-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbs) }}
      />

      <header className="border-b border-slate-800 pb-6 mb-6">
        <h1 className="text-3xl font-bold">{job.title}</h1>
        <p className="text-slate-400 mt-2">
          {job.company} Â· {job.city || job.location} Â· {job.work_mode}
        </p>
        {job.salary_max && (
          <p className="text-emerald-400 mt-2 font-semibold">
            {job.salary_min}â€“{job.salary_max} {job.currency}
          </p>
        )}
        <div className="flex flex-wrap gap-2 mt-3 text-xs">
          {job.visa_sponsorship && (
            <span className="bg-emerald-700 px-2 py-1 rounded">âœ… Viza</span>
          )}
          {job.housing_provided && (
            <span className="bg-indigo-700 px-2 py-1 rounded">ðŸ  SmjeÅ¡taj</span>
          )}
          {job.category && (
            <span className="bg-slate-800 px-2 py-1 rounded">
              {job.category}
            </span>
          )}
        </div>
      </header>

      <section
        className="prose prose-invert max-w-none"
        dangerouslySetInnerHTML={{ __html: job.description }}
      />

      <a
        href={job.url}
        target="_blank"
        rel="noopener noreferrer nofollow"
        className="inline-block mt-8 bg-indigo-600 hover:bg-indigo-500 px-6 py-3 rounded-lg font-medium"
      >
        Prijavi se direktno â†-
      </a>
    </article>
  );
}


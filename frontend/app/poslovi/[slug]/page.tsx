import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { serverFetch } from "@/lib/api";

interface Job {
  id: string; slug: string; title: string; company: string; location: string; city: string;
  work_mode: string; category: string; seniority: string; description: string;
  salary_min?: number; salary_max?: number; currency?: string; url: string;
  posted_at?: string; expires_at?: string; seo_title?: string; seo_description?: string;
  visa_sponsorship?: boolean; housing_provided?: boolean;
}

async function getJob(slug: string) { return serverFetch<Job>(`/public/jobs/${slug}`, 3600); }

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const job = await getJob(slug);
  if (!job) return { title: "Posao nije pronađen" };
  const title = job.seo_title || `${job.title} — ${job.company} (${job.city || job.location})`;
  const description = job.seo_description || `${job.company} traži ${job.title} u ${job.city || job.location}. ${job.work_mode === "remote" ? "Remote posao. " : ""}Prijavi se brzo preko WorkSync.`;
  return { title, description, alternates: { canonical: `/poslovi/${job.slug}` }, openGraph: { title, description, type: "article" } };
}

export default async function JobPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const job = await getJob(slug);
  if (!job) notFound();
  const jsonLd = {
    "@context": "https://schema.org", "@type": "JobPosting", title: job.title,
    description: job.description, datePosted: job.posted_at, validThrough: job.expires_at,
    employmentType: "FULL_TIME", hiringOrganization: { "@type": "Organization", name: job.company },
    jobLocation: { "@type": "Place", address: { "@type": "PostalAddress", addressLocality: job.city || job.location } },
    jobLocationType: job.work_mode === "remote" ? "TELECOMMUTE" : undefined,
  };
  return (
    <article className="job-detail max-w-4xl mx-auto px-4 py-10">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <header className="job-detail-header border-b border-slate-800 pb-8 mb-8">
        <p className="eyebrow text-slate-400 mb-4">WORKSYNC / OGLAS</p>
        <h1 className="text-3xl font-bold mb-4">{job.title}</h1>
        <div className="job-detail-meta text-slate-400"><span>{job.company}</span><span>{job.city || job.location}</span><span>{job.work_mode}</span></div>
        {job.salary_max && <p className="job-detail-salary text-emerald-400 mt-4 font-semibold">{job.salary_min}–{job.salary_max} {job.currency}</p>}
        <div className="flex flex-wrap gap-2 mt-5 text-xs">
          {job.visa_sponsorship && <span className="bg-emerald-700 px-3 py-1.5 rounded-lg">Viza dostupna</span>}
          {job.housing_provided && <span className="bg-indigo-700 px-3 py-1.5 rounded-lg">Smještaj obezbijeđen</span>}
          {job.category && <span className="bg-slate-800 px-3 py-1.5 rounded-lg">{job.category}</span>}
        </div>
      </header>
      <section className="job-detail-description prose prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: job.description }} />
      <a href={job.url} target="_blank" rel="noopener noreferrer nofollow" className="job-apply-button inline-flex mt-10 px-6 py-3 rounded-xl font-semibold">Prijavi se direktno</a>
    </article>
  );
}

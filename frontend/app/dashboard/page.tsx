"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { RequireAuth } from "@/components/RequireAuth";
import { clearAuth, getUser } from "@/lib/auth";
import { useRouter } from "next/navigation";

interface FeedJob {
  id: string;
  slug: string;
  title: string;
  company: string;
  location: string;
  work_mode: string;
  score_pct: number;
  url: string;
  eligibility: { eligible: boolean; reason: string; notes: string[] };
  allowed_countries?: string[];
  salary_min?: number;
  salary_max?: number;
  currency?: string;
}

function ScoreBadge({ score }: { score: number }) {
  const color =
    score >= 90
      ? "bg-emerald-600"
      : score >= 75
        ? "bg-yellow-600"
        : score >= 50
          ? "bg-slate-600"
          : "bg-slate-800";
  return (
    <span className={`${color} px-2 py-1 rounded text-xs font-bold`}>
      {score.toFixed(0)}% Match
    </span>
  );
}

export default function DashboardPage() {
  return (
    <RequireAuth>
      <DashboardInner />
    </RequireAuth>
  );
}

function DashboardInner() {
  const router = useRouter();
  const [jobs, setJobs] = useState<FeedJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [reason, setReason] = useState<string | null>(null);
  const [error, setError] = useState("");
  const user = getUser();

  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get("/jobs/feed?limit=30");
        setJobs(data.items || []);
        if (data.reason) setReason(data.reason);
      } catch (err: any) {
        if (err?.response?.status === 401) {
          clearAuth();
          router.push("/login");
        } else {
          setError("GreÅ¡ka pri dohvatu preporuka.");
        }
      } finally {
        setLoading(false);
      }
    })();
  }, [router]);

  async function save(job: FeedJob) {
    await api.post("/applications", {
      job_id: job.id,
      status: "saved",
      match_score: job.score_pct,
    });
    alert("SaÄuvano!");
  }

  async function autoApply(job: FeedJob) {
    const res = await api.post(`/applications/auto-apply/${job.id}`);
    if (res.data.queued) alert("Prijava ide u red. Otvori /kanban za status.");
    else alert("Rate limit â€” probaj kasnije.");
  }

  async function generateCoverLetter(job: FeedJob) {
    const { data } = await api.post(`/ai/cover-letter/${job.id}?language=bs`);
    await navigator.clipboard.writeText(data.cover_letter);
    alert("Propratno pismo kopirano u clipboard!");
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">
            Zdravo, {user?.full_name || user?.email || "kandidate"} ðŸ‘‹
          </h1>
          <p className="text-slate-400 mt-1">
            Tvoje AI preporuke â€” sortirano po match-u.
          </p>
        </div>
        <Link
          href="/profil"
          className="bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg text-sm"
        >
          Uredi profil
        </Link>
      </div>

      {reason === "profile_not_ready" && (
        <div className="bg-yellow-950/40 border border-yellow-900 text-yellow-200 p-4 rounded-lg mb-6">
          âš ï¸ Tvoj profil joÅ¡ nije kompletan.{" "}
          <Link href="/profil" className="underline">
            Upload-uj CV
          </Link>{" "}
          da bi AI mogao da radi matching.
        </div>
      )}

      {error && (
        <div className="bg-red-950/40 border border-red-900 text-red-200 p-4 rounded-lg mb-6">
          {error}
        </div>
      )}

      {loading ? (
        <p className="text-slate-400">UÄitavanje preporuka...</p>
      ) : jobs.length === 0 ? (
        <p className="text-slate-400">
          Nema preporuka. Upload-uj CV u profilu.
        </p>
      ) : (
        <div className="space-y-3">
          {jobs.map((j) => (
            <div
              key={j.id}
              className="bg-slate-900 border border-slate-800 rounded-xl p-5"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 flex-wrap">
                    <Link
                      href={`/poslovi/${j.slug}`}
                      className="text-lg font-semibold hover:text-indigo-400"
                    >
                      {j.title}
                    </Link>
                    <ScoreBadge score={j.score_pct} />
                    <span className="bg-slate-800 px-2 py-0.5 rounded text-xs">
                      {j.work_mode}
                    </span>
                  </div>
                  <p className="text-slate-400 text-sm mt-1">
                    {j.company} Â· {j.location}
                  </p>
                  {j.salary_max && (
                    <p className="text-emerald-400 text-sm mt-1">
                      {j.salary_min}â€“{j.salary_max} {j.currency}
                    </p>
                  )}
                  {j.eligibility?.notes?.length > 0 && (
                    <p className="text-yellow-400 text-xs mt-1">
                      âš ï¸ {j.eligibility.notes.join(" Â· ")}
                    </p>
                  )}
                </div>
                <div className="flex flex-col gap-2 items-end">
                  <a
                    href={j.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-indigo-400 text-sm hover:underline"
                  >
                    Otvori â†-
                  </a>
                  <button
                    onClick={() => save(j)}
                    className="bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded text-xs"
                  >
                    SaÄuvaj
                  </button>
                  <button
                    onClick={() => generateCoverLetter(j)}
                    className="bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded text-xs"
                  >
                    GeneriÅ¡i pismo
                  </button>
                  <button
                    onClick={() => autoApply(j)}
                    className="bg-indigo-600 hover:bg-indigo-500 px-3 py-1.5 rounded text-xs"
                  >
                    Auto-Apply
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}


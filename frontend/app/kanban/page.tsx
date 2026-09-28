"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { RequireAuth } from "@/components/RequireAuth";

type Status =
  | "saved"
  | "applied"
  | "interview"
  | "offer"
  | "rejected"
  | "prefill";

const COLUMNS: { key: Status; label: string; color: string }[] = [
  { key: "saved", label: "ðŸ“Œ SaÄuvano", color: "border-slate-700" },
  { key: "applied", label: "ðŸ“¤ Prijavljeno", color: "border-blue-700" },
  { key: "prefill", label: "âš ï¸ Prefill", color: "border-yellow-700" },
  { key: "interview", label: "ðŸ’¬ Intervju", color: "border-purple-700" },
  { key: "offer", label: "ðŸŽ‰ Ponuda", color: "border-emerald-700" },
  { key: "rejected", label: "âŒ Odbijeno", color: "border-red-900" },
];

interface App {
  id: string;
  job_id: string;
  status: Status;
  match_score?: number;
  updated_at: string;
  job: { title: string; company: string; url: string; slug: string };
}

export default function KanbanPage() {
  return (
    <RequireAuth>
      <KanbanInner />
    </RequireAuth>
  );
}

function KanbanInner() {
  const [apps, setApps] = useState<App[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    const { data } = await api.get("/applications");
    setApps(data);
    setLoading(false);
  }

  useEffect(() => {
    load();
  }, []);

  async function moveTo(appId: string, status: Status) {
    setApps((prev) => prev.map((a) => (a.id === appId ? { ...a, status } : a)));
    try {
      await api.patch(`/applications/${appId}`, { status });
    } catch {
      load();
    }
  }

  async function remove(appId: string) {
    if (!confirm("Obrisati ovu prijavu?")) return;
    await api.delete(`/applications/${appId}`);
    setApps((prev) => prev.filter((a) => a.id !== appId));
  }

  if (loading) {
    return <div className="p-8 text-slate-400">UÄitavanje...</div>;
  }

  return (
    <div className="max-w-full px-4 py-8">
      <div className="flex items-center justify-between mb-6 max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold">PraÄ‡enje prijava</h1>
        <p className="text-slate-400 text-sm">Ukupno: {apps.length}</p>
      </div>

      <div className="overflow-x-auto pb-4">
        <div className="grid grid-cols-6 gap-3 min-w-[1200px] max-w-[1600px] mx-auto">
          {COLUMNS.map((col) => {
            const items = apps.filter((a) => a.status === col.key);
            return (
              <div
                key={col.key}
                className={`bg-slate-900 border-2 ${col.color} rounded-xl p-3 min-h-[400px]`}
              >
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-sm font-semibold">{col.label}</h2>
                  <span className="text-xs text-slate-500">{items.length}</span>
                </div>
                <div className="space-y-2">
                  {items.map((a) => (
                    <div
                      key={a.id}
                      className="bg-slate-800 hover:bg-slate-750 rounded-lg p-3 text-xs"
                    >
                      <Link
                        href={`/poslovi/${a.job.slug}`}
                        className="font-semibold line-clamp-2 hover:text-indigo-400"
                      >
                        {a.job.title}
                      </Link>
                      <p className="text-slate-400 mt-1">{a.job.company}</p>
                      {a.match_score != null && (
                        <p className="text-emerald-400 mt-1">
                          {a.match_score.toFixed(0)}% match
                        </p>
                      )}
                      <select
                        value={a.status}
                        onChange={(e) => moveTo(a.id, e.target.value as Status)}
                        className="mt-2 w-full bg-slate-700 rounded px-1 py-1 text-xs"
                      >
                        {COLUMNS.map((c) => (
                          <option key={c.key} value={c.key}>
                            {c.label}
                          </option>
                        ))}
                      </select>
                      <button
                        onClick={() => remove(a.id)}
                        className="mt-1 text-red-400 hover:text-red-300 text-xs w-full text-left"
                      >
                        ObriÅ¡i
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}


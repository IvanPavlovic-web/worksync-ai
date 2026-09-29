"use client";

import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { RequireAuth } from "@/components/RequireAuth";

interface ProfileData {
  profile: {
    title?: string;
    summary?: string;
    location?: string;
    location_country?: string;
    seniority?: string;
    work_mode_pref?: string;
    remote_pref?: string;
    skills: { name: string; category?: string; level?: string }[];
    experiences: any[];
  };
  vault: {
    first_name?: string;
    last_name?: string;
    email?: string;
    phone?: string;
    linkedin_url?: string;
    github_url?: string;
    portfolio_url?: string;
    city?: string;
    country?: string;
    country_code?: string;
    requires_sponsorship?: boolean;
    willing_to_relocate?: boolean;
  };
}

export default function ProfilePage() {
  return (
    <RequireAuth>
      <ProfileInner />
    </RequireAuth>
  );
}

function ProfileInner() {
  const [data, setData] = useState<ProfileData | null>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    (async () => {
      try {
        const r = await api.get("/profile");
        setData(r.data);
      } catch {
        setMsg("Greška pri učitavanju profila");
      }
    })();
  }, []);

  async function uploadCv(file: File) {
    setBusy(true);
    setMsg("");
    const fd = new FormData();
    fd.append("file", file);
    try {
      const { data: res } = await api.post("/ai/import-cv", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMsg(
        `CV parsiran! Jezik: ${res.detected_language}, pozicija: ${res.primary_role}, vještina: ${res.skills_count}`,
      );
      const r = await api.get("/profile");
      setData(r.data);
    } catch (err: any) {
      setMsg((err?.response?.data?.detail || "Greška pri upload-u"));
    } finally {
      setBusy(false);
    }
  }

  async function saveVault(e: React.FormEvent) {
    e.preventDefault();
    if (!data) return;
    setBusy(true);
    try {
      await api.put("/profile/vault", data.vault);
      setMsg("Vault sačuvan");
    } catch {
      setMsg("Greška pri čuvanju");
    } finally {
      setBusy(false);
    }
  }

  if (!data) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-slate-400">
        Učitavanje...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      <h1 className="text-3xl font-bold">Moj profil</h1>

      {msg && (
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 text-sm">
          {msg}
        </div>
      )}

      <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <h2 className="text-xl font-semibold mb-3">📄 CV Import</h2>
        <p className="text-slate-400 text-sm mb-4">
          Upload-uj CV (PDF / DOCX / TXT) — AI će ga parsirati i popuniti
          profil.
        </p>
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          onChange={(e) => e.target.files && uploadCv(e.target.files[0])}
          className="hidden"
        />
        <button
          disabled={busy}
          onClick={() => fileRef.current?.click()}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 px-4 py-2 rounded-lg"
        >
          {busy ? "AI radi..." : "Odaberi CV"}
        </button>
      </section>

      <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <h2 className="text-xl font-semibold mb-4">👤 Osnovni podaci</h2>
        <form
          onSubmit={saveVault}
          className="grid grid-cols-1 md:grid-cols-2 gap-4"
        >
          <Field
            label="Ime"
            value={data.vault.first_name}
            onChange={(v) =>
              setData({ ...data, vault: { ...data.vault, first_name: v } })
            }
          />
          <Field
            label="Prezime"
            value={data.vault.last_name}
            onChange={(v) =>
              setData({ ...data, vault: { ...data.vault, last_name: v } })
            }
          />
          <Field
            label="Email"
            value={data.vault.email}
            onChange={(v) =>
              setData({ ...data, vault: { ...data.vault, email: v } })
            }
          />
          <Field
            label="Telefon"
            value={data.vault.phone}
            onChange={(v) =>
              setData({ ...data, vault: { ...data.vault, phone: v } })
            }
          />
          <Field
            label="Grad"
            value={data.vault.city}
            onChange={(v) =>
              setData({ ...data, vault: { ...data.vault, city: v } })
            }
          />
          <Field
            label="Država (kod npr. BA)"
            value={data.vault.country_code}
            onChange={(v) =>
              setData({
                ...data,
                vault: { ...data.vault, country_code: v.toUpperCase() },
              })
            }
          />
          <Field
            label="LinkedIn URL"
            value={data.vault.linkedin_url}
            onChange={(v) =>
              setData({ ...data, vault: { ...data.vault, linkedin_url: v } })
            }
          />
          <Field
            label="GitHub URL"
            value={data.vault.github_url}
            onChange={(v) =>
              setData({ ...data, vault: { ...data.vault, github_url: v } })
            }
          />
          <Field
            label="Portfolio URL"
            value={data.vault.portfolio_url}
            onChange={(v) =>
              setData({ ...data, vault: { ...data.vault, portfolio_url: v } })
            }
          />

          <div className="md:col-span-2 flex gap-6 mt-2">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={!!data.vault.requires_sponsorship}
                onChange={(e) =>
                  setData({
                    ...data,
                    vault: {
                      ...data.vault,
                      requires_sponsorship: e.target.checked,
                    },
                  })
                }
              />
              Potrebna mi je viza / radna dozvola
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={!!data.vault.willing_to_relocate}
                onChange={(e) =>
                  setData({
                    ...data,
                    vault: {
                      ...data.vault,
                      willing_to_relocate: e.target.checked,
                    },
                  })
                }
              />
              Spreman/na sam za selidbu
            </label>
          </div>

          <div className="md:col-span-2">
            <button
              type="submit"
              disabled={busy}
              className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 px-4 py-2 rounded-lg"
            >
              Sačuvaj vault
            </button>
          </div>
        </form>
      </section>

      <section className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <h2 className="text-xl font-semibold mb-4">
          💼 Iskustvo i vještine (iz CV-a)
        </h2>

        {data.profile.title && (
          <p className="text-slate-300">
            <strong>Titula:</strong> {data.profile.title}
          </p>
        )}
        {data.profile.summary && (
          <p className="text-slate-400 text-sm mt-2">{data.profile.summary}</p>
        )}

        {data.profile.skills?.length > 0 && (
          <div className="mt-4">
            <h3 className="text-sm uppercase text-slate-500 mb-2">Vještine</h3>
            <div className="flex flex-wrap gap-2">
              {data.profile.skills.map((s, i) => (
                <span
                  key={i}
                  className="bg-slate-800 px-2 py-1 rounded text-xs"
                >
                  {s.name} {s.level && `· ${s.level}`}
                </span>
              ))}
            </div>
          </div>
        )}

        {data.profile.experiences?.length > 0 && (
          <div className="mt-4 space-y-3">
            <h3 className="text-sm uppercase text-slate-500 mb-2">Iskustvo</h3>
            {data.profile.experiences.map((e, i) => (
              <div key={i} className="border-l-2 border-slate-700 pl-3">
                <p className="font-semibold">{e.role}</p>
                <p className="text-sm text-slate-400">{e.company}</p>
                {e.description && (
                  <p className="text-xs text-slate-500 mt-1">
                    {e.description.slice(0, 200)}...
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
}: {
  label: string;
  value?: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <label className="block text-sm text-slate-300 mb-1">{label}</label>
      <input
        type="text"
        value={value || ""}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
      />
    </div>
  );
}


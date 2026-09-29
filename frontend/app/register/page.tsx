"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import { setToken, setUser } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (password.length < 8) {
      setError("Lozinka mora imati barem 8 karaktera.");
      return;
    }
    setBusy(true);
    try {
      const { data } = await api.post("/auth/register", {
        email,
        password,
        full_name: fullName,
      });
      setToken(data.token);
      setUser({ email, full_name: fullName });
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Registracija nije uspjela.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-slate-950">
      <form
        onSubmit={submit}
        className="bg-slate-900 border border-slate-800 rounded-2xl p-8 w-full max-w-md space-y-4"
      >
        <h1 className="text-2xl font-bold text-white">Registracija</h1>
        <p className="text-slate-400 text-sm">
          Napravi nalog i pusti AI da nađe posao za tebe.
        </p>

        <div>
          <label className="block text-sm text-slate-300 mb-1">
            Ime i prezime
          </label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
            placeholder="Amina Hodžić"
          />
        </div>

        <div>
          <label className="block text-sm text-slate-300 mb-1">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div>
          <label className="block text-sm text-slate-300 mb-1">
            Lozinka (min 8 znakova)
          </label>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
          />
        </div>

        {error && (
          <p className="text-red-400 text-sm bg-red-950/40 border border-red-900 rounded p-2">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={busy}
          className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium py-2 rounded-lg"
        >
          {busy ? "Kreiram nalog..." : "Registruj se"}
        </button>

        <p className="text-slate-400 text-sm text-center">
          Već imaš nalog?{" "}
          <Link href="/login" className="text-indigo-400 hover:underline">
            Prijavi se
          </Link>
        </p>
      </form>
    </div>
  );
}


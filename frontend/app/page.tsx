import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-12">
      <div className="rounded-3xl bg-white p-10 shadow-sm ring-1 ring-slate-200">
        <p className="text-sm font-medium uppercase tracking-[0.3em] text-sky-600">
          Nano Lab Academy
        </p>
        <h1 className="mt-4 text-4xl font-bold tracking-tight text-slate-900">
          Learner frontend
        </h1>
        <p className="mt-4 max-w-2xl text-slate-600">
          Dashboard, course outline, lessons, and quizzes are available in the
          learner area.
        </p>
        <div className="mt-8 flex gap-3">
          <Link
            className="rounded-full bg-sky-600 px-5 py-3 text-sm font-semibold text-white"
            href="/dashboard"
          >
            Open dashboard
          </Link>
          <Link
            className="rounded-full border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-700"
            href="/courses"
          >
            Browse courses
          </Link>
        </div>
      </div>
    </main>
  );
}

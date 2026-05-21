"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { getJson, postJson } from "@/lib/api";
import { useSessionStore } from "@/lib/store";

type EnrollmentResponse = {
  id?: string;
  courseId?: string;
  stage?: string;
  stage1Completed?: boolean;
  stage2Completed?: boolean;
  stage1Locked?: boolean;
  enrolled?: boolean;
  plans?: Array<{ id: string; name: string; description?: string; monthlyPrice?: number }>;
};

type GamificationResponse = {
  xp?: number;
  streak?: number;
  badges?: Array<{ id: string; name: string; description?: string }>;
  stage?: string;
  stageProgress?: number;
};

const fallbackPlans = [
  { id: "basics", name: "Basics", description: "Operator track", monthlyPrice: 0 },
  { id: "pro", name: "Pro", description: "Supervisor track", monthlyPrice: 120000 },
  { id: "ultra", name: "Ultra", description: "Calibration leader track", monthlyPrice: 240000 },
];

export default function DashboardPage() {
  const { enrollment, gamification, setEnrollment, setGamification } = useSessionStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [enrollingId, setEnrollingId] = useState<string | null>(null);
  const [plans, setPlans] = useState(fallbackPlans);

  useEffect(() => {
    let active = true;
    Promise.all([
      getJson<EnrollmentResponse>("/enrollments/my"),
      getJson<GamificationResponse>("/gamification/status"),
      getJson<{ plans?: EnrollmentResponse["plans"] }>("/courses/available").catch(() => ({})),
    ])
      .then(([enrollmentData, gamificationData, availableData]) => {
        if (!active) return;
        setEnrollment(enrollmentData as never);
        setGamification(gamificationData);
        if (availableData.plans?.length) {
          setPlans(
            availableData.plans.map((plan) => ({
              id: plan.id,
              name: plan.name,
              description: plan.description,
              monthlyPrice: plan.monthlyPrice,
            })),
          );
        }
      })
      .catch((err: unknown) => {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Failed to load dashboard");
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [setEnrollment, setGamification]);

  const stageProgress = useMemo(
    () => gamification?.stageProgress ?? (enrollment?.stage1Completed ? 100 : 0),
    [enrollment?.stage1Completed, gamification?.stageProgress],
  );

  async function handleEnroll(planId: string) {
    setEnrollingId(planId);
    try {
      await postJson("/enrollments", { planId });
      const updated = await getJson<EnrollmentResponse>("/enrollments/my");
      setEnrollment(updated as never);
    } finally {
      setEnrollingId(null);
    }
  }

  if (loading) {
    return <main className="p-8 text-slate-600">Loading dashboard...</main>;
  }

  if (error) {
    return <main className="p-8 text-red-600">{error}</main>;
  }

  const isEnrolled = Boolean(enrollment?.id ?? enrollment?.enrolled);

  return (
    <main className="mx-auto max-w-6xl px-6 py-8">
      <div className="mb-8 flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-sky-600">
            Learner dashboard
          </p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">Your progress</h1>
        </div>
        <Link className="text-sm font-semibold text-sky-700" href="/courses">
          View courses →
        </Link>
      </div>

      {isEnrolled ? (
        <div className="grid gap-4 md:grid-cols-4">
          <StatCard label="Stage progress" value={`${stageProgress}%`} />
          <StatCard label="XP" value={`${gamification?.xp ?? 0}`} />
          <StatCard label="Streak" value={`${gamification?.streak ?? 0} days`} />
          <StatCard label="Badges" value={`${gamification?.badges?.length ?? 0}`} />
        </div>
      ) : null}

      {isEnrolled ? (
        <section className="mt-8 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h2 className="text-xl font-semibold text-slate-900">Badges earned</h2>
          <div className="mt-4 flex flex-wrap gap-3">
            {(gamification?.badges ?? []).length ? (
              gamification?.badges?.map((badge) => (
                <span
                  key={badge.id}
                  className="rounded-full bg-sky-50 px-4 py-2 text-sm font-medium text-sky-700"
                >
                  {badge.name}
                </span>
              ))
            ) : (
              <p className="text-sm text-slate-500">No badges yet.</p>
            )}
          </div>
        </section>
      ) : (
        <section className="mt-8 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h2 className="text-xl font-semibold text-slate-900">Choose a plan</h2>
          <div className="mt-5 grid gap-4 md:grid-cols-3">
            {plans.map((plan) => (
              <article key={plan.id} className="rounded-2xl border border-slate-200 p-5">
                <h3 className="text-lg font-semibold text-slate-900">{plan.name}</h3>
                <p className="mt-2 text-sm text-slate-600">{plan.description}</p>
                <p className="mt-4 text-2xl font-bold text-slate-900">
                  {plan.monthlyPrice ? `${plan.monthlyPrice}` : "Free"}
                </p>
                <button
                  className="mt-5 rounded-full bg-sky-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
                  disabled={enrollingId === plan.id}
                  onClick={() => handleEnroll(plan.id)}
                  type="button"
                >
                  {enrollingId === plan.id ? "Enrolling..." : "Enroll"}
                </button>
              </article>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-3 text-3xl font-bold text-slate-900">{value}</p>
    </div>
  );
}

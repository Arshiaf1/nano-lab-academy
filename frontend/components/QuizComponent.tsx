"use client";

import { useEffect, useMemo, useState } from "react";
import { getJson, postJson } from "@/lib/api";

type Question = {
  id: string;
  questionText: string;
  questionType?: "single_choice" | "multiple_choice" | "text";
  options?: string[];
  points?: number;
};

type QuizResponse = {
  id: string;
  title: string;
  passThreshold?: number;
  maxAttempts?: number;
  questions?: Question[];
};

type Props = {
  quizId: string;
};

export function QuizComponent({ quizId }: Props) {
  const [quiz, setQuiz] = useState<QuizResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    getJson<QuizResponse>(`/quizzes/${quizId}`)
      .then((data) => {
        if (!active) return;
        setQuiz(data);
      })
      .catch((err: unknown) => {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Failed to load quiz");
      })
      .finally(() => {
        if (!active) return;
        setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [quizId]);

  const questions = useMemo(() => quiz?.questions ?? [], [quiz]);

  async function handleSubmit() {
    setSubmitting(true);
    setResult(null);
    try {
      const payload = {
        answers: Object.entries(answers).map(([questionId, answer]) => ({
          questionId,
          answer,
        })),
      };
      const response = await postJson<{ score?: number; passed?: boolean }>(
        `/quizzes/${quizId}/attempt`,
        payload,
      );
      setResult(
        response.passed
          ? `Passed${typeof response.score === "number" ? ` with ${response.score}%` : ""}`
          : `Submitted${typeof response.score === "number" ? ` (${response.score}%)` : ""}`,
      );
    } catch (err: unknown) {
      setResult(err instanceof Error ? err.message : "Failed to submit quiz");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return <p className="text-sm text-slate-500">Loading quiz...</p>;
  }

  if (error) {
    return <p className="text-sm text-red-600">{error}</p>;
  }

  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <div className="mb-4">
        <h3 className="text-xl font-semibold text-slate-900">{quiz?.title ?? "Quiz"}</h3>
        {typeof quiz?.passThreshold === "number" ? (
          <p className="text-sm text-slate-500">Pass threshold: {quiz.passThreshold}%</p>
        ) : null}
      </div>

      <div className="space-y-4">
        {questions.map((question, index) => (
          <label key={question.id} className="block rounded-2xl bg-slate-50 p-4">
            <p className="font-medium text-slate-900">
              {index + 1}. {question.questionText}
            </p>
            {question.options?.length ? (
              <select
                className="mt-3 w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm"
                value={answers[question.id] ?? ""}
                onChange={(event) =>
                  setAnswers((current) => ({ ...current, [question.id]: event.target.value }))
                }
              >
                <option value="">Choose an answer</option>
                {question.options.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            ) : (
              <input
                className="mt-3 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
                value={answers[question.id] ?? ""}
                onChange={(event) =>
                  setAnswers((current) => ({ ...current, [question.id]: event.target.value }))
                }
              />
            )}
          </label>
        ))}
      </div>

      <div className="mt-5 flex items-center gap-3">
        <button
          className="rounded-full bg-sky-600 px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
          disabled={submitting}
          onClick={handleSubmit}
          type="button"
        >
          {submitting ? "Submitting..." : "Submit answers"}
        </button>
        {result ? <p className="text-sm text-slate-600">{result}</p> : null}
      </div>
    </div>
  );
}

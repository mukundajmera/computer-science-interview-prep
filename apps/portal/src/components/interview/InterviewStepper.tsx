"use client";

import { useState, useEffect, useCallback } from "react";
import type { InterviewTemplate } from "./interview-data";

interface Props {
  template: InterviewTemplate;
  problemTitle: string;
}

function timerDisplay(
  overTime: boolean,
  elapsedSec: number,
  stepDurationSec: number,
  remaining: number,
  formatTime: (sec: number) => string
): string {
  if (overTime) return `+${formatTime(elapsedSec - stepDurationSec)}`;
  return formatTime(remaining);
}

export function InterviewStepper({ template, problemTitle }: Props) {
  const [currentStep, setCurrentStep] = useState(0);
  const [elapsedSec, setElapsedSec] = useState(0);
  const [running, setRunning] = useState(false);
  const [stepNotes, setStepNotes] = useState<Record<number, string>>({});

  const step = template.steps[currentStep];
  const stepDurationSec = step.durationMin * 60;

  // Timer tick
  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => setElapsedSec((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, [running]);

  const formatTime = useCallback((sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${String(s).padStart(2, "0")}`;
  }, []);

  const overTime = elapsedSec > stepDurationSec;
  const remaining = Math.max(0, stepDurationSec - elapsedSec);

  function goToStep(idx: number) {
    setCurrentStep(idx);
    setElapsedSec(0);
    setRunning(false);
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-2xl font-bold">{problemTitle}</h1>
        <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-800">
          {template.label} · {template.totalMin} min
        </span>
      </div>

      {/* Step progress bar */}
      <div className="flex gap-1">
        {template.steps.map((s, i) => (
          <button
            key={i}
            onClick={() => goToStep(i)}
            title={s.title}
            aria-label={s.title}
            aria-current={i === currentStep ? "step" : undefined}
            className={`h-2 flex-1 rounded-full transition-colors ${
              i < currentStep
                ? "bg-green-500"
                : i === currentStep
                ? "bg-blue-600"
                : "bg-gray-200"
            }`}
          />
        ))}
      </div>

      {/* Current step card */}
      <div className="rounded-xl border p-6">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <span className="text-sm text-gray-500">
              Step {currentStep + 1} of {template.steps.length}
            </span>
            <h2 className="text-xl font-semibold">{step.title}</h2>
          </div>
          <div className="text-right">
            <div
              className={`text-2xl font-mono font-bold ${
                overTime ? "text-red-600" : "text-gray-900"
              }`}
            >
              {timerDisplay(overTime, elapsedSec, stepDurationSec, remaining, formatTime)}
            </div>
            <span className="text-xs text-gray-500">
              {step.durationMin} min allotted
            </span>
          </div>
        </div>

        {/* Timer controls */}
        <div className="mt-4 flex gap-2">
          <button
            onClick={() => setRunning(!running)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              running
                ? "bg-yellow-100 text-yellow-800 hover:bg-yellow-200"
                : "bg-green-100 text-green-800 hover:bg-green-200"
            }`}
          >
            {running ? "⏸ Pause" : "▶ Start Timer"}
          </button>
          <button
            onClick={() => {
              setElapsedSec(0);
              setRunning(false);
            }}
            className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-200"
          >
            ↻ Reset
          </button>
        </div>

        {/* Prompt */}
        <div className="mt-5 rounded-lg bg-blue-50 p-4">
          <p className="font-medium text-blue-900">{step.prompt}</p>
        </div>

        {/* Tips */}
        <div className="mt-4">
          <h3 className="text-sm font-semibold text-gray-600">💡 Tips</h3>
          <ul className="mt-1 space-y-1">
            {step.tips.map((tip, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                <span className="mt-0.5 text-gray-400">•</span>
                {tip}
              </li>
            ))}
          </ul>
        </div>

        {/* Notes area */}
        <div className="mt-4">
          <label htmlFor="step-notes" className="text-sm font-semibold text-gray-600">
            📝 Your Notes
          </label>
          <textarea
            id="step-notes"
            value={stepNotes[currentStep] ?? ""}
            onChange={(e) =>
              setStepNotes((prev) => ({
                ...prev,
                [currentStep]: e.target.value,
              }))
            }
            placeholder="Jot down your thoughts for this step..."
            rows={4}
            className="mt-1 w-full rounded-lg border p-3 text-sm focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-400"
          />
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between">
        <button
          disabled={currentStep === 0}
          onClick={() => goToStep(currentStep - 1)}
          className="rounded-lg bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-200 disabled:opacity-40"
        >
          ← Previous
        </button>
        {currentStep < template.steps.length - 1 ? (
          <button
            onClick={() => goToStep(currentStep + 1)}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
          >
            Next →
          </button>
        ) : (
          <span className="rounded-lg bg-green-100 px-4 py-2 text-sm font-semibold text-green-800">
            ✅ Interview Complete
          </span>
        )}
      </div>
    </div>
  );
}

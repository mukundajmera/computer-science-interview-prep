"use client";

import { useId, useState } from "react";
import { MarkdownRenderer } from "@/components/content/MarkdownRenderer";

type RevealTone = "amber" | "green";

interface RevealPanelProps {
  title: string;
  description: string;
  revealHref: string;
  revealLabel: string;
  hideLabel: string;
  tone: RevealTone;
}

const toneClasses: Record<RevealTone, {
  panel: string;
  title: string;
  text: string;
  button: string;
}> = {
  amber: {
    panel: "border-amber-300 bg-amber-50",
    title: "text-amber-900",
    text: "text-amber-700",
    button: "bg-amber-200 text-amber-900 hover:bg-amber-300",
  },
  green: {
    panel: "border-green-300 bg-green-50",
    title: "text-green-900",
    text: "text-green-700",
    button: "bg-green-200 text-green-900 hover:bg-green-300",
  },
};

export function RevealPanel({
  title,
  description,
  revealHref,
  revealLabel,
  hideLabel,
  tone,
}: RevealPanelProps) {
  const [revealed, setRevealed] = useState(false);
  const [html, setHtml] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const contentId = useId();
  const classes = toneClasses[tone];
  const toggleReveal = async () => {
    if (loading) return;

    if (revealed) {
      setRevealed(false);
      return;
    }

    if (!html) {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(revealHref);
        if (!response.ok) throw new Error(`Reveal fetch failed: ${response.status}`);

        const page = await response.text();
        const document = new DOMParser().parseFromString(page, "text/html");
        const revealContent = document.querySelector("[data-reveal-content]");
        if (!revealContent) throw new Error("Reveal content was not found");

        setHtml(revealContent.innerHTML);
      } catch {
        setError("Unable to load the reveal content.");
        return;
      } finally {
        setLoading(false);
      }
    }

    setRevealed(true);
  };

  return (
    <div className={`mt-8 rounded-xl border border-dashed p-6 ${classes.panel}`}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className={`text-lg font-semibold ${classes.title}`}>{title}</h2>
        <button
          type="button"
          onClick={toggleReveal}
          aria-expanded={revealed}
          aria-controls={contentId}
          disabled={loading}
          className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${classes.button}`}
        >
          {loading ? "Loading..." : revealed ? hideLabel : revealLabel}
        </button>
      </div>
      {!revealed && !error ? (
        <p className={`mt-2 text-sm ${classes.text}`}>{description}</p>
      ) : null}
      {error ? <p className="mt-2 text-sm text-red-700">{error}</p> : null}
      <div
        id={contentId}
        role="region"
        aria-label={title}
        hidden={!revealed}
        className={revealed ? "mt-4" : undefined}
      >
        {revealed && html ? <MarkdownRenderer html={html} /> : null}
      </div>
    </div>
  );
}

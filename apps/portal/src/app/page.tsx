import { SectionCard } from "@/components/content/SectionCard";
import { buildSectionSummaries } from "@/content/section-summaries";
import Link from "next/link";

export default function HomePage() {
  const sections = buildSectionSummaries();

  return (
    <div>
      <h1 className="text-3xl font-bold">
        🎯 System Design Interview Prep
      </h1>
      <p className="mt-2 text-lg text-gray-600">
        Master LLD, HLD, Design Patterns, and GenAI system design — all in one
        place.
      </p>

      <div className="mt-6 flex flex-wrap gap-4">
        <Link
          href="/start"
          className="rounded-lg bg-blue-600 px-6 py-2 font-semibold text-white hover:bg-blue-700"
        >
          Start Here
        </Link>
        <Link
          href="/progress"
          className="rounded-lg border bg-white px-6 py-2 font-semibold text-gray-700 hover:bg-gray-50"
        >
          Continue Learning
        </Link>
      </div>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {sections.map((section) => (
          <SectionCard
            key={section.href}
            href={section.href}
            emoji={section.emoji}
            label={section.label}
            description={section.description}
            summary={section.summary}
          />
        ))}
      </div>
    </div>
  );
}

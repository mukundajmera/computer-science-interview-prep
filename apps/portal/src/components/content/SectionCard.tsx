import Link from "next/link";
import { SectionProgressBadge } from "@/components/progress/SectionProgressBadge";

interface SectionCardProps {
  href: string;
  emoji: string;
  label: string;
  description: string;
  summary?: string;
  progressItemIds?: string[];
}

export function SectionCard({
  href,
  emoji,
  label,
  description,
  summary,
  progressItemIds,
}: SectionCardProps) {
  return (
    <Link
      href={href}
      className="group rounded-lg border p-5 transition-shadow hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="text-2xl">{emoji}</div>
        <div className="flex items-center gap-2">
          {progressItemIds && progressItemIds.length > 0 ? (
            <SectionProgressBadge itemIds={progressItemIds} />
          ) : null}
          {summary ? (
            <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
              {summary}
            </span>
          ) : null}
        </div>
      </div>
      <h2 className="mt-2 font-semibold group-hover:text-blue-600">{label}</h2>
      <p className="mt-1 text-sm text-gray-500">{description}</p>
    </Link>
  );
}

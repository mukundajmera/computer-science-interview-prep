import Link from "next/link";

interface SectionCardProps {
  href: string;
  emoji: string;
  label: string;
  description: string;
  summary?: string;
}

export function SectionCard({
  href,
  emoji,
  label,
  description,
  summary,
}: SectionCardProps) {
  return (
    <Link
      href={href}
      className="group rounded-lg border p-5 transition-shadow hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="text-2xl">{emoji}</div>
        {summary ? (
          <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
            {summary}
          </span>
        ) : null}
      </div>
      <h2 className="mt-2 font-semibold group-hover:text-blue-600">{label}</h2>
      <p className="mt-1 text-sm text-gray-500">{description}</p>
    </Link>
  );
}

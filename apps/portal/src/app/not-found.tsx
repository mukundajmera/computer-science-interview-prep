import Link from "next/link";
import { PORTAL_SECTIONS } from "@/lib/sections";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-3xl py-12 text-center">
      <h1 className="text-3xl font-bold">404 - Page not found</h1>
      <p className="mt-2 text-lg text-gray-600">
        This URL does not match any page, but every study section is one click
        away.
      </p>

      <div className="mt-6">
        <Link
          href="/"
          className="rounded-lg bg-blue-600 px-6 py-2 font-semibold text-white hover:bg-blue-700"
        >
          Back to home
        </Link>
      </div>

      <div className="mt-8 grid gap-4 text-left sm:grid-cols-2 lg:grid-cols-3">
        {PORTAL_SECTIONS.map((section) => (
          <Link
            key={section.href}
            href={section.href}
            className="rounded-lg border bg-white px-4 py-3 hover:bg-gray-50"
          >
            <span className="font-semibold text-gray-700">
              {section.emoji} {section.label}
            </span>
            <span className="mt-1 block text-sm text-gray-600">
              {section.description}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}

"use client";

import Link from "next/link";
import { useId, useMemo, useState } from "react";
import type { SearchEntry } from "@/content/search-index";

interface SearchBoxProps {
  entries: SearchEntry[];
}

export function SearchBox({ entries }: SearchBoxProps) {
  const [query, setQuery] = useState("");
  const listId = useId();
  const statusId = useId();
  const normalizedQuery = query.trim().toLowerCase();
  const hasSearchQuery = normalizedQuery.length >= 2;

  const results = useMemo(() => {
    if (!hasSearchQuery) return [];
    return entries
      .filter((entry) => entry.searchText.includes(normalizedQuery))
      .slice(0, 8);
  }, [entries, hasSearchQuery, normalizedQuery]);

  const resultStatus = hasSearchQuery
    ? results.length > 0
      ? `${results.length} results available.`
      : "No results found."
    : "Enter at least two characters to search.";

  return (
    <div className="relative w-full max-w-xl" role="search">
      <label htmlFor="portal-search" className="sr-only">
        Search portal
      </label>
      <input
        id="portal-search"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Escape") setQuery("");
        }}
        type="search"
        placeholder="Search topics, quizzes, projects..."
        aria-controls={hasSearchQuery ? listId : undefined}
        aria-describedby={statusId}
        className="h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
      />
      <p id={statusId} className="sr-only" aria-live="polite">
        {resultStatus}
      </p>
      {hasSearchQuery && (
        <ul
          id={listId}
          className="absolute left-0 right-0 top-12 z-50 overflow-hidden rounded-lg border bg-white shadow-lg"
        >
          {results.map((result) => (
            <li key={result.href} className="border-b last:border-b-0">
              <Link
                href={result.href}
                onClick={() => setQuery("")}
                className="block px-4 py-3 text-sm hover:bg-gray-50"
              >
                <span className="font-medium text-gray-900">{result.title}</span>
                <span className="ml-2 text-xs text-gray-500">{result.section}</span>
                {result.description ? (
                  <span className="mt-1 block text-xs text-gray-500">
                    {result.description}
                  </span>
                ) : null}
              </Link>
            </li>
          ))}
          {results.length === 0 ? (
            <li className="px-4 py-3 text-sm text-gray-500">No results found.</li>
          ) : null}
        </ul>
      )}
    </div>
  );
}

"use client";

import { useState, useMemo } from "react";
import { ContentList } from "@/components/content/ContentList";
import { InterviewType } from "./interview-data";

export interface InterviewItem {
  id: string;
  href: string;
  title: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  icon: string;
  meta: string;
  type: InterviewType;
}

interface InterviewSetupProps {
  items: InterviewItem[];
}

export function InterviewSetup({ items }: InterviewSetupProps) {
  const [activeTab, setActiveTab] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      const matchesSearch = item.title
        .toLowerCase()
        .includes(searchQuery.toLowerCase());
      if (!matchesSearch) return false;

      switch (activeTab) {
        case "High-Level Design":
          return item.type === "hld" || item.type === "genai-hld";
        case "Low-Level Design":
          return item.type === "lld";
        case "Coding Patterns":
          return item.type === "coding";
        case "Behavioral":
          return item.type === "behavioral";
        default:
          return true; // "All"
      }
    });
  }, [items, activeTab, searchQuery]);

  const tabs = [
    "All",
    "High-Level Design",
    "Low-Level Design",
    "Coding Patterns",
    "Behavioral",
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="flex flex-wrap gap-2">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                activeTab === tab
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
        <div className="relative">
          <input
            type="text"
            placeholder="Search problems..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full sm:w-64 px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <ContentList items={filteredItems} columns="one" variant="comfortable" />
    </div>
  );
}

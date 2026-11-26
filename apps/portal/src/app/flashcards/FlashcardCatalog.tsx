"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { FlashcardDeck } from "@/content/flashcards";
import { DifficultyBadge } from "@/components/content/DifficultyBadge";

export function FlashcardCatalog({ decks }: { decks: FlashcardDeck[] }) {
  const [search, setSearch] = useState("");
  const [categoryTab, setCategoryTab] = useState<string>("All");
  const [progressMap, setProgressMap] = useState<Record<string, number>>({});

  useEffect(() => {
    const newProgressMap: Record<string, number> = {};
    for (const deck of decks) {
      try {
        const data = localStorage.getItem(`flashcard-progress-${deck.id}`);
        if (data) {
          const parsed = JSON.parse(data);
          const completed = Object.keys(parsed).length;
          newProgressMap[deck.id] = Math.round((completed / deck.cardCount) * 100);
        }
      } catch { }
    }
    setProgressMap(newProgressMap);
  }, [decks]);

  const categories = ["All", "HLD", "LLD", "Coding", "GenAI", "Behavioral"];

  const filteredDecks = decks.filter(deck => {
    const matchesSearch = deck.title.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = categoryTab === "All" || deck.category === categoryTab;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <input 
          type="text" 
          placeholder="Search flashcards..." 
          className="border rounded-md px-4 py-2 w-full sm:w-64"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="flex flex-wrap gap-2">
          {categories.map(cat => (
            <button 
              key={cat} 
              onClick={() => setCategoryTab(cat)}
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                categoryTab === cat ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDecks.map(deck => {
          const progress = progressMap[deck.id] || 0;

          return (
            <Link key={deck.id} href={`/flashcards/${deck.id}`}>
              <div className="border rounded-lg p-5 hover:shadow-lg transition-shadow bg-white h-full flex flex-col cursor-pointer">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-bold text-gray-900">{deck.title}</h3>
                  <span className="text-xs bg-gray-100 px-2 py-1 rounded-md text-gray-600 font-semibold">{deck.category}</span>
                </div>
                <div className="mt-auto pt-4 space-y-3">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-500">{deck.cardCount} cards</span>
                    <DifficultyBadge difficulty={deck.difficulty} />
                  </div>
                  {progress > 0 && (
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${progress}%` }}></div>
                    </div>
                  )}
                </div>
              </div>
            </Link>
          );
        })}
        {filteredDecks.length === 0 && (
          <div className="col-span-full py-12 text-center text-gray-500">
            No flashcard decks found matching your criteria.
          </div>
        )}
      </div>
    </div>
  );
}

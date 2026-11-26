import { getCachedDecks } from "@/content/flashcards";
import { FlashcardCatalog } from "./FlashcardCatalog";

export const metadata = {
  title: "Flashcards - System Design Prep",
  description: "Test your knowledge with spaced repetition flashcards for HLD, LLD, and GenAI.",
};

export default function FlashcardsPage() {
  const decks = getCachedDecks();

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight mb-2">
          🧠 Interview Flashcards
        </h1>
        <p className="text-lg text-gray-600">
          Review core concepts across High-Level Design, Low-Level Design, and GenAI.
        </p>
      </div>
      
      <FlashcardCatalog decks={decks} />
    </div>
  );
}

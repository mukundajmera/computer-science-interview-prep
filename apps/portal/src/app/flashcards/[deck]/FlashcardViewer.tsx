"use client";

import { useState, useEffect, useCallback } from "react";
import { Flashcard } from "@/content/flashcards";
import { MarkdownRenderer } from "@/components/content/MarkdownRenderer";
import Link from "next/link";

interface RenderedFlashcard extends Flashcard {
  frontHtml: string;
  backHtml: string;
}

interface FlashcardViewerProps {
  deckId: string;
  cards: RenderedFlashcard[];
}

export function FlashcardViewer({ deckId, cards: initialCards }: FlashcardViewerProps) {
  const [cards, setCards] = useState<RenderedFlashcard[]>(initialCards);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [isShuffled, setIsShuffled] = useState(false);
  const [progress, setProgress] = useState<Record<string, string>>({});

  useEffect(() => {
    try {
      const data = localStorage.getItem(`flashcard-progress-${deckId}`);
      if (data) {
        setProgress(JSON.parse(data));
      }
    } catch {}
  }, [deckId]);

  const saveProgress = (cardId: string, grade: string) => {
    const newProgress = { ...progress, [cardId]: grade };
    setProgress(newProgress);
    try {
      localStorage.setItem(`flashcard-progress-${deckId}`, JSON.stringify(newProgress));
    } catch {}
  };

  const handleFlip = useCallback(() => {
    setIsFlipped(prev => !prev);
  }, []);

  const handleNext = useCallback(() => {
    setIsFlipped(false);
    setCurrentIndex(prev => (prev < cards.length - 1 ? prev + 1 : prev));
  }, [cards.length]);

  const handlePrev = useCallback(() => {
    setIsFlipped(false);
    setCurrentIndex(prev => (prev > 0 ? prev - 1 : prev));
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === "Space") {
        e.preventDefault();
        handleFlip();
      } else if (e.code === "ArrowRight") {
        handleNext();
      } else if (e.code === "ArrowLeft") {
        handlePrev();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleFlip, handleNext, handlePrev]);

  const toggleShuffle = () => {
    if (isShuffled) {
      setCards(initialCards);
      setCurrentIndex(0);
      setIsShuffled(false);
    } else {
      const shuffled = [...cards].sort(() => Math.random() - 0.5);
      setCards(shuffled);
      setCurrentIndex(0);
      setIsShuffled(true);
    }
    setIsFlipped(false);
  };

  const exportToAnki = () => {
    // TSV format: front \t back
    const tsvRows = initialCards.map(c => {
      // Escape tabs and newlines
      const front = c.front.replace(/\t/g, " ").replace(/\n/g, "<br>");
      const back = c.back.replace(/\t/g, " ").replace(/\n/g, "<br>");
      return `${front}\t${back}`;
    });
    const tsvContent = tsvRows.join("\n");
    const blob = new Blob([tsvContent], { type: "text/tab-separated-values" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${deckId}-anki.tsv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (cards.length === 0) return <div>No cards in this deck.</div>;

  const currentCard = cards[currentIndex];
  const currentGrade = progress[currentCard.id];

  return (
    <div className="flex flex-col h-full items-center relative" style={{ perspective: "1000px" }}>
      
      {/* Top Bar */}
      <div className="w-full flex justify-between items-center mb-6">
        <Link href="/flashcards" className="text-blue-600 hover:underline">
          &larr; Back to Decks
        </Link>
        <div className="flex gap-2">
          <button 
            onClick={toggleShuffle} 
            className={`px-3 py-1 text-sm rounded ${isShuffled ? "bg-blue-100 text-blue-800" : "bg-gray-100 text-gray-700"}`}
          >
            {isShuffled ? "🔀 Shuffled" : "Shuffle"}
          </button>
          <button 
            onClick={exportToAnki}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            Export Anki TSV
          </button>
        </div>
      </div>

      {/* Card Area */}
      <div 
        className="relative w-full max-w-2xl aspect-[4/3] sm:aspect-video cursor-pointer"
        onClick={handleFlip}
      >
        <div 
          className="w-full h-full transition-transform duration-500"
          style={{ transformStyle: "preserve-3d", transform: isFlipped ? "rotateY(180deg)" : "rotateY(0deg)" }}
        >
          {/* Front */}
          <div 
            className="absolute inset-0 bg-white border-2 border-gray-200 rounded-xl shadow-lg p-8 flex flex-col justify-center items-center text-center"
            style={{ backfaceVisibility: "hidden" }}
          >
            <div className="text-sm text-gray-400 absolute top-4 left-4">Question</div>
            {currentGrade && (
              <div className="absolute top-4 right-4 text-xs font-bold uppercase tracking-wider text-gray-500">
                Last: {currentGrade}
              </div>
            )}
            <div className="max-w-full overflow-y-auto">
              <MarkdownRenderer html={currentCard.frontHtml} />
            </div>
          </div>

          {/* Back */}
          <div 
            className="absolute inset-0 bg-gray-50 border-2 border-gray-300 rounded-xl shadow-lg p-8 flex flex-col justify-center items-center text-center"
            style={{ backfaceVisibility: "hidden", transform: "rotateY(180deg)" }}
          >
            <div className="text-sm text-gray-400 absolute top-4 left-4">Answer</div>
            <div className="max-w-full overflow-y-auto text-left w-full h-full pt-6">
              <MarkdownRenderer html={currentCard.backHtml} />
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="w-full max-w-2xl mt-8 flex flex-col gap-4">
        {/* Grading Buttons - Only show when flipped */}
        <div className={`flex justify-center gap-2 sm:gap-4 transition-opacity duration-300 ${isFlipped ? "opacity-100" : "opacity-0 pointer-events-none"}`}>
          <button onClick={(e) => { e.stopPropagation(); saveProgress(currentCard.id, "Again"); handleNext(); }} className="px-4 py-2 bg-red-100 text-red-700 hover:bg-red-200 rounded-md font-medium">Again</button>
          <button onClick={(e) => { e.stopPropagation(); saveProgress(currentCard.id, "Hard"); handleNext(); }} className="px-4 py-2 bg-orange-100 text-orange-700 hover:bg-orange-200 rounded-md font-medium">Hard</button>
          <button onClick={(e) => { e.stopPropagation(); saveProgress(currentCard.id, "Good"); handleNext(); }} className="px-4 py-2 bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-md font-medium">Good</button>
          <button onClick={(e) => { e.stopPropagation(); saveProgress(currentCard.id, "Easy"); handleNext(); }} className="px-4 py-2 bg-green-100 text-green-700 hover:bg-green-200 rounded-md font-medium">Easy</button>
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center w-full px-4 text-gray-500">
          <button 
            onClick={handlePrev}
            disabled={currentIndex === 0}
            className="px-4 py-2 disabled:opacity-50 hover:text-gray-900"
          >
            &larr; Prev
          </button>
          <div className="text-sm">
            {currentIndex + 1} / {cards.length}
          </div>
          <button 
            onClick={handleNext}
            disabled={currentIndex === cards.length - 1}
            className="px-4 py-2 disabled:opacity-50 hover:text-gray-900"
          >
            Next &rarr;
          </button>
        </div>
      </div>

      <div className="mt-4 text-xs text-gray-400 text-center">
        Tip: Use Spacebar to flip, Arrow keys to navigate
      </div>
    </div>
  );
}

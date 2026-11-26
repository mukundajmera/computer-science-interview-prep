import { notFound } from "next/navigation";
import { getCachedDeck, getAllDecks } from "@/content/flashcards";
import { renderMarkdown } from "@/content/loader";
import { FlashcardViewer } from "./FlashcardViewer";

export async function generateStaticParams() {
  const decks = getAllDecks();
  return decks.map(deck => ({ deck: deck.id }));
}

export default async function DeckPage({ params }: { params: { deck: string } }) {
  const deckData = getCachedDeck(params.deck);
  if (!deckData) {
    notFound();
  }

  // Pre-render markdown for all cards in this deck on the server
  const renderedCards = await Promise.all(deckData.cards.map(async card => {
    const frontHtml = (await renderMarkdown(card.front)).html;
    const backHtml = (await renderMarkdown(card.back)).html;
    return {
      ...card,
      frontHtml,
      backHtml
    };
  }));

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8 h-[calc(100vh-64px)] flex flex-col">
      <div className="mb-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{deckData.title}</h1>
          <p className="text-sm text-gray-500">{deckData.cardCount} cards • {deckData.category}</p>
        </div>
      </div>
      
      <div className="flex-1 flex flex-col min-h-0">
        <FlashcardViewer deckId={deckData.id} cards={renderedCards} />
      </div>
    </div>
  );
}

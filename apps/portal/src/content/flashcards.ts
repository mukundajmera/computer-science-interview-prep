import fs from "fs";
import path from "path";
import { REPO_ROOT } from "./safe-content";
import { Difficulty } from "./types";

export interface Flashcard {
  id: string;
  front: string;
  back: string;
  deck: string;
  category: string;
}

export interface FlashcardDeck {
  id: string;
  title: string;
  category: string;
  difficulty: Difficulty;
  cardCount: number;
  cards: Flashcard[];
}

const FLASHCARDS_DIR = path.join(REPO_ROOT, "flashcards");

export function getFlashcardsCategory(id: string): string {
  if (id.includes("hld") || id.includes("distributed") || id.includes("infra") || id.includes("applied-ml")) return "HLD";
  if (id.includes("lld") || id.includes("design-patterns")) return "LLD";
  if (id.includes("ai") || id.includes("genai") || id.includes("ml")) return "GenAI";
  if (id.includes("behavioral") || id.includes("salary")) return "Behavioral";
  return "Coding";
}

export function getAllDecks(): FlashcardDeck[] {
  if (!fs.existsSync(FLASHCARDS_DIR)) {
    return [];
  }

  const files = fs.readdirSync(FLASHCARDS_DIR).filter(file => file.endsWith(".md") && file !== "README.md" && file !== "AGENTS.md");
  const decks: FlashcardDeck[] = [];

  for (const file of files) {
    const id = file.replace(".md", "");
    const filePath = path.join(FLASHCARDS_DIR, file);
    const content = fs.readFileSync(filePath, "utf-8");
    
    const titleMatch = content.match(/^#\s+(.+)$/m);
    const title = titleMatch ? titleMatch[1].trim().replace(" Flashcards", "").replace(" Flashcard", "") : id;
    
    const category = getFlashcardsCategory(id);
    const cards: Flashcard[] = [];
    
    const cardSections = content.split(/###\s+Card\s+\d+/i);
    for (let i = 1; i < cardSections.length; i++) {
      const section = cardSections[i];
      
      const frontMatch = section.match(/(?:\*\*Front:\*\*|Front:)\s*([\s\S]*?)(?=(?:\*\*Back:\*\*|Back:)|$)/i);
      const backMatch = section.match(/(?:\*\*Back:\*\*|Back:)\s*([\s\S]*?)$/i);
      
      let front = frontMatch ? frontMatch[1].trim() : "";
      front = front.replace(/---+$/, "").trim();
      
      let back = backMatch ? backMatch[1].trim() : "";
      back = back.replace(/---+$/, "").trim();
      
      if (!back) {
         back = "*(Question-only flashcard. Answer verbally and check your understanding against the source material.)*";
      }
      
      if (front) {
        cards.push({
          id: `${id}-${i}`,
          front,
          back,
          deck: id,
          category,
        });
      }
    }
    
    if (cards.length > 0) {
      decks.push({
        id,
        title,
        category,
        difficulty: "intermediate", 
        cardCount: cards.length,
        cards,
      });
    }
  }
  
  return decks;
}

let cachedDecks: FlashcardDeck[] | null = null;

export function getCachedDecks(): FlashcardDeck[] {
  if (!cachedDecks) {
    cachedDecks = getAllDecks();
  }
  return cachedDecks;
}

export function getCachedDeck(id: string): FlashcardDeck | undefined {
  const decks = getCachedDecks();
  return decks.find(d => d.id === id);
}

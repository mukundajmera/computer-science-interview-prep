export interface PortalSection {
  label: string;
  href: string;
  emoji: string;
  description: string;
}

export const PORTAL_SECTIONS: PortalSection[] = [
  {
    label: "Start Here",
    href: "/start",
    emoji: "🚀",
    description: "Welcome to System Design",
  },
  {
    label: "Learning Paths",
    href: "/learning-paths",
    emoji: "🛣️",
    description: "Structured paths to mastery",
  },
  {
    label: "Theory",
    href: "/theory",
    emoji: "📚",
    description: "Core CS fundamentals",
  },
  {
    label: "Design Patterns",
    href: "/patterns",
    emoji: "🎨",
    description: "23 GoF patterns",
  },
  {
    label: "Coding Patterns",
    href: "/coding",
    emoji: "🔁",
    description: "Algorithm templates for interviews",
  },
  {
    label: "LLD Projects",
    href: "/lld",
    emoji: "🏗️",
    description: "Low-level design practice",
  },
  {
    label: "HLD Concepts",
    href: "/hld-concepts",
    emoji: "⚙️",
    description: "System design building blocks",
  },
  {
    label: "HLD Projects",
    href: "/hld",
    emoji: "🌐",
    description: "End-to-end system designs",
  },
  {
    label: "GenAI Systems",
    href: "/genai",
    emoji: "🤖",
    description: "GenAI / LLM system design",
  },
  {
    label: "Case Studies",
    href: "/case-studies",
    emoji: "📊",
    description: "Real company architectures",
  },
  {
    label: "Interview Mode",
    href: "/interview",
    emoji: "🎯",
    description: "Guided practice sessions",
  },
  {
    label: "Quizzes",
    href: "/quizzes",
    emoji: "📝",
    description: "Test your knowledge",
  },
  {
    label: "Flashcards",
    href: "/flashcards",
    emoji: "🗂️",
    description: "Spaced repetition practice",
  },
  {
    label: "Resources",
    href: "/resources",
    emoji: "🧭",
    description: "Study plans, cheatsheets, tips, and templates",
  },
  {
    label: "Progress Tracker",
    href: "/progress",
    emoji: "📈",
    description: "Local study progress",
  },
];

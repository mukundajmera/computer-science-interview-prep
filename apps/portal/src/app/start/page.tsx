import { Metadata } from "next";
import Link from "next/link";
import { LevelAssessment } from "@/components/start/level-assessment";
import { StudyTrackSelector } from "@/components/start/study-track-selector";

export const metadata: Metadata = {
  title: "Start Here - Onboarding | System Design Prep",
  description: "Get started with your system design interview preparation.",
};

export default function StartPage() {
  return (
    <div className="mx-auto max-w-5xl py-8">
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-gray-100 sm:text-5xl">
          Welcome to the Portal
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-xl text-gray-600 dark:text-gray-400">
          Your journey to mastering System Design and GenAI architecture starts here. 
          Let&apos;s find the best path for your goals.
        </p>
      </header>

      <section className="mb-16">
        <div className="grid gap-8 lg:grid-cols-2">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              Where should I start?
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400 mb-6">
              System design is a vast topic. Depending on your experience level and the roles you are targeting, 
              your focus areas will differ. Take our quick assessment to get a personalized recommendation.
            </p>
            <div className="prose dark:prose-invert">
              <ul className="space-y-2">
                <li><strong>Junior:</strong> Focus on coding, theory, and basic object-oriented design.</li>
                <li><strong>Mid:</strong> Master Low-Level Design (LLD) and foundational High-Level Design (HLD).</li>
                <li><strong>Senior:</strong> Deep dive into distributed systems, scale, and trade-offs.</li>
                <li><strong>Staff+:</strong> Navigate ambiguous problems, cross-system architecture, and GenAI concepts.</li>
              </ul>
            </div>
          </div>
          <div>
            <LevelAssessment />
          </div>
        </div>
      </section>

      <section className="mb-16">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-6 text-center">
          Curriculum Map
        </h2>
        <p className="text-center text-gray-600 dark:text-gray-400 mb-8 max-w-3xl mx-auto">
          The curriculum is designed sequentially, but you can jump to any section that fits your needs.
        </p>
        
        <div className="relative">
          <div className="absolute left-1/2 hidden h-full w-0.5 -translate-x-1/2 bg-gray-200 dark:bg-gray-800 md:block" />
          
          <div className="space-y-8 relative">
            {[
              { id: "00", title: "Theory & Foundations", desc: "Computer science fundamentals, networking, and databases.", link: "/theory", color: "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300" },
              { id: "01", title: "Design Patterns", desc: "GoF patterns, cloud architecture patterns, and anti-patterns.", link: "/patterns", color: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300" },
              { id: "02", title: "Low-Level Design (LLD)", desc: "Object-oriented design, API design, and schema modeling.", link: "/lld", color: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-300" },
              { id: "03", title: "HLD Concepts", desc: "Building blocks: load balancers, caching, message queues.", link: "/hld-concepts", color: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300" },
              { id: "04", title: "HLD Projects", desc: "Real-world systems: Chat apps, Ride-sharing, URL shorteners.", link: "/hld", color: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300" },
              { id: "06", title: "GenAI Systems", desc: "LLMs, RAG architectures, Vector DBs, and agentic workflows.", link: "/genai", color: "bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-300" },
            ].map((item, idx) => (
              <div key={item.id} className={`relative flex flex-col items-center md:flex-row ${idx % 2 === 0 ? "md:flex-row-reverse" : ""}`}>
                <div className="absolute left-1/2 flex h-8 w-8 -translate-x-1/2 items-center justify-center rounded-full border-4 border-white bg-gray-200 dark:border-gray-950 dark:bg-gray-800 hidden md:flex">
                  <span className="text-xs font-bold text-gray-500">{item.id}</span>
                </div>
                
                <div className={`w-full md:w-1/2 ${idx % 2 === 0 ? "md:pl-12" : "md:pr-12"}`}>
                  <Link href={item.link} className="block rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md dark:border-gray-800 dark:bg-gray-950">
                    <div className={`mb-3 inline-block rounded-full px-3 py-1 text-xs font-semibold ${item.color}`}>
                      Section {item.id}
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                      {item.title}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      {item.desc}
                    </p>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mb-16">
        <StudyTrackSelector />
      </section>

      <section className="mb-16 rounded-2xl bg-gradient-to-br from-indigo-50 to-blue-50 p-8 dark:from-indigo-950/20 dark:to-blue-900/20 border border-indigo-100 dark:border-indigo-900/30">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-indigo-900 dark:text-indigo-100 mb-4">
            How to Practice: Interview Mode
          </h2>
          <p className="text-lg text-indigo-800 dark:text-indigo-200 mb-6">
            Reading about systems is not enough. You must practice speaking and diagramming. 
            Use our built-in <strong>Interview Mode</strong> to simulate a real interview environment.
          </p>
          
          <div className="grid gap-6 sm:grid-cols-3 text-left">
            <div className="bg-white/60 dark:bg-gray-900/60 p-5 rounded-xl backdrop-blur-sm">
              <div className="text-2xl mb-2">🎙️</div>
              <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">1. Speak Aloud</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">Treat the problem statement like a real prompt. Talk through your requirements and estimates.</p>
            </div>
            <div className="bg-white/60 dark:bg-gray-900/60 p-5 rounded-xl backdrop-blur-sm">
              <div className="text-2xl mb-2">⏱️</div>
              <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">2. Time Yourself</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">Aim for 45 minutes. Watch the clock and ensure you leave 15 minutes for deep dives.</p>
            </div>
            <div className="bg-white/60 dark:bg-gray-900/60 p-5 rounded-xl backdrop-blur-sm">
              <div className="text-2xl mb-2">✅</div>
              <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">3. Check Solutions</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">Compare your design against the STRONG-ANSWER guides to find gaps in your knowledge.</p>
            </div>
          </div>
          
          <div className="mt-8">
            <Link href="/interview" className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-6 py-3 text-base font-medium text-white transition-colors hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600">
              Try Interview Mode Now
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

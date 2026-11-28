import Link from "next/link";

const plans = [
  {
    id: "1-week",
    title: "1-Week Crash Course",
    duration: "7 Days",
    desc: "For urgent upcoming interviews. Covers absolute essentials.",
    href: "/resources/study-plans/1-week-plan",
  },
  {
    id: "1-month",
    title: "1-Month Intensive",
    duration: "30 Days",
    desc: "Solid preparation covering HLD concepts and top 5 LLD/HLD projects.",
    href: "/resources/study-plans/1-month-plan",
  },
  {
    id: "60-day",
    title: "60-Day Comprehensive",
    duration: "60 Days",
    desc: "In-depth coverage including deep dives, advanced patterns, and GenAI.",
    href: "/resources/study-plans/60-day-plan",
  },
  {
    id: "90-day",
    title: "90-Day Mastery",
    duration: "90 Days",
    desc: "The ultimate guide for Staff+ roles. Leaves no stone unturned.",
    href: "/resources/study-plans/90-day-plan",
  },
];

export function StudyTrackSelector() {
  return (
    <div className="mt-12">
      <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
        Quick Links to Study Plans
      </h3>
      <p className="mt-2 text-gray-600 dark:text-gray-400">
        Have a specific timeline? Pick a structured study plan to guide your daily learning.
      </p>

      <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {plans.map((plan) => (
          <Link
            key={plan.id}
            href={plan.href}
            className="group flex flex-col rounded-xl border border-gray-200 bg-white p-6 transition-all hover:border-blue-500 hover:shadow-md dark:border-gray-800 dark:bg-gray-950 dark:hover:border-blue-500"
          >
            <div className="mb-4 inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
              {plan.duration}
            </div>
            <h4 className="mb-2 text-lg font-semibold text-gray-900 group-hover:text-blue-600 dark:text-gray-100 dark:group-hover:text-blue-400">
              {plan.title}
            </h4>
            <p className="text-sm text-gray-600 dark:text-gray-400 flex-1">
              {plan.desc}
            </p>
            <div className="mt-4 flex items-center text-sm font-medium text-blue-600 dark:text-blue-400">
              View Plan
              <svg
                className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

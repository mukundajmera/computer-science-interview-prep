import { loadFile } from "./loader";

export interface QuizQuestion {
  id: number;
  section: string;
  text: string;
  options: { letter: string; text: string }[];
}

export interface QuizAnswer {
  answer: string;
  explanation: string;
}

export interface ScoreBand {
  scoreRange: string;
  percentage: string;
  assessment: string;
  recommendation: string;
}

export interface StructuredQuiz {
  slug: string;
  timeStr: string;
  questions: QuizQuestion[];
  answers: Record<number, QuizAnswer>;
  bands: ScoreBand[];
}

export function parseQuizFile(quizContent: string): { questions: QuizQuestion[]; timeStr: string } {
  const lines = quizContent.split('\n');
  const questions: QuizQuestion[] = [];
  let currentSection = 'General';
  let currentQ: QuizQuestion | null = null;
  let qText: string[] = [];
  let timeStr = '60 minutes';

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    const timeMatch = line.match(/^Time:\s*(.*)/i) || line.match(/^⏱️\s*Time:\s*(.*)/i) || line.match(/^⏱️\s*Time:\s*([^\s]+)/i);
    if (timeMatch && !timeMatch[1].includes('|')) {
      timeStr = timeMatch[1].trim();
    } else if (line.includes('⏱️ Time:')) {
      const p = line.split('|')[0];
      const match = p.match(/Time:\s*(.*)/);
      if (match) timeStr = match[1].trim();
    }

    const sectionMatch = line.match(/^##\s+(.*)/);
    if (sectionMatch && !sectionMatch[1].startsWith('Section')) {
       if (!line.includes('Overview') && !line.includes('Quick Links')) {
          currentSection = sectionMatch[1].trim();
       }
    }
    const strictSectionMatch = line.match(/^##\s+Section\s+\d+:\s*(.*)/);
    if (strictSectionMatch) {
       currentSection = strictSectionMatch[1].trim();
    }

    const qMatch = line.match(/^###\s+Question\s+(\d+)/i);
    if (qMatch) {
      if (currentQ) {
        currentQ.text = qText.join('\n').trim();
        questions.push(currentQ);
      }
      currentQ = { id: parseInt(qMatch[1], 10), section: currentSection, options: [], text: '' };
      qText = [];
      continue;
    }

    const optMatch = line.match(/^([A-Z])[\)\.]\s+(.*)/);
    if (optMatch && currentQ) {
      currentQ.options.push({ letter: optMatch[1], text: optMatch[2].trim() });
      continue;
    }

    if (currentQ) {
      if (line.trim() !== '---' && line.trim() !== '') {
        qText.push(line);
      }
    }
  }
  if (currentQ) {
    currentQ.text = qText.join('\n').trim();
    questions.push(currentQ);
  }
  return { questions, timeStr };
}

export function parseAnswerKey(answerContent: string): Record<number, QuizAnswer> {
  const lines = answerContent.split('\n');
  const answers: Record<number, QuizAnswer> = {};
  let currentQ: number | null = null;
  let expText: string[] = [];
  let tableHeaders: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.trim().startsWith('|')) {
      const cells = line.trim().replace(/^\||\|$/g, '').split('|').map((cell) => cell.trim());
      if (/^question$|^#$/i.test(cells[0] ?? '')) {
        tableHeaders = cells;
        continue;
      }
      const letterCell = (cells[1] ?? '').match(/^\*{0,2}([A-Z])\*{0,2}(?:\s*[-:)]\s*(.*))?$/i);
      if (/^\d+$/.test(cells[0] ?? '') && letterCell && cells.length > 2) {
        const questionNumber = parseInt(cells[0], 10);
        answers[questionNumber] = {
          answer: letterCell[1].toUpperCase(),
          explanation: [letterCell[2] ? `**Answer:** ${letterCell[2]}` : '', ...cells
            .slice(2)
            .map((cell, index) => {
              const header = tableHeaders[index + 2];
              return header && cells.length > 3 ? `**${header}:** ${cell}` : cell;
            })]
            .filter(Boolean)
            .join('\n\n'),
        };
        currentQ = null;
        expText = [];
        continue;
      }
    }

    const qMatch1 = line.match(/^###\s+Question\s+(\d+)/i);
    const qMatch2 = line.match(/^(\d+)[.\-)]\s*\*{0,2}([A-Z])\b/i);

    if (qMatch1) {
      if (currentQ) {
        answers[currentQ] = { ...answers[currentQ], explanation: expText.join('\n').trim() };
      }
      currentQ = parseInt(qMatch1[1], 10);
      expText = [];
      answers[currentQ] = { answer: '', explanation: '' };
      continue;
    } else if (qMatch2) {
      if (currentQ && expText.length > 0) {
        answers[currentQ] = { ...answers[currentQ], explanation: expText.join('\n').trim() };
      }
      currentQ = parseInt(qMatch2[1], 10);
      answers[currentQ] = { answer: qMatch2[2].toUpperCase(), explanation: '' };
      expText = [];
      continue;
    }

    const ansMatch = line.match(/^\*\*Answer:\s*([A-Z])\*\*/i) || line.match(/^\*\*Answer:\s*([A-Z])\)\*\*/i);
    if (ansMatch && currentQ) {
      answers[currentQ].answer = ansMatch[1].toUpperCase();
      continue;
    }

    if (currentQ && line.trim() !== '') {
      expText.push(line);
    }
  }
  if (currentQ) {
    answers[currentQ] = { ...answers[currentQ], explanation: expText.join('\n').trim() };
  }
  return answers;
}

export function extractScoreBands(readmeContent: string, titleSlug: string): ScoreBand[] {
  const lines = readmeContent.split('\n');
  const bands: ScoreBand[] = [];
  let targetSectionFound = false;
  let inTable = false;

  const abbreviations: Record<string, string> = { 'hld': 'hld', 'lld': 'lld', 'api': 'api', 'os': 'os', 'db': 'db', 'bfs': 'bfs', 'dfs': 'dfs', 'ml': 'ml', 'ai': 'ai' };
  const formattedTitle = titleSlug.split('-').map(w => {
    if (abbreviations[w]) return abbreviations[w];
    if (w === 'genai') return 'genai';
    return w;
  }).join(' ');
  const normalizedTitleWords = formattedTitle.toLowerCase().split(' ').filter(w => w !== 'quiz');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.startsWith('### ')) {
      const headerText = line.replace('### ', '').trim().toLowerCase();
      const matchesAllWords = normalizedTitleWords.every(word => headerText.includes(word));
      if (matchesAllWords && headerText.includes('quiz') && !headerText.includes('progress') && !headerText.includes('overview')) {
        targetSectionFound = true;
        inTable = false;
      } else {
        targetSectionFound = false;
      }
      continue;
    }

    if (targetSectionFound) {
      if (line.trim().startsWith('| Score | Range | Assessment | Recommendation |') || line.trim().startsWith('| Score |')) {
        inTable = true;
        continue;
      }
      if (inTable && line.trim().startsWith('|---')) {
        continue;
      }
      if (inTable && line.trim().startsWith('|')) {
        const parts = line.split('|').map(p => p.trim()).filter(p => p !== '');
        if (parts.length >= 4) {
          bands.push({
            scoreRange: parts[0],
            percentage: parts[1],
            assessment: parts[2].replace(/\*/g, ''),
            recommendation: parts[3]
          });
        }
      } else if (inTable && line.trim() === '') {
        break;
      }
    }
  }

  if (bands.length === 0) {
    bands.push(
      { scoreRange: '90-100%', percentage: '90-100%', assessment: 'Excellent', recommendation: 'Great job!' },
      { scoreRange: '75-89%', percentage: '75-89%', assessment: 'Good', recommendation: 'Review weak areas' },
      { scoreRange: '60-74%', percentage: '60-74%', assessment: 'Fair', recommendation: 'More practice needed' },
      { scoreRange: '0-59%', percentage: '0-59%', assessment: 'Needs Work', recommendation: 'Study fundamentals first' }
    );
  }
  return bands;
}

export function getStructuredQuiz(slug: string): StructuredQuiz {
  const quizPath = `quizzes/${slug}-quiz.md`;
  const answerPath = `quizzes/answers/${slug}-answers.md`;
  const readmePath = `quizzes/README.md`;

  const quizContent = loadFile(quizPath) || '';
  const answerContent = loadFile(answerPath) || '';
  const readmeContent = loadFile(readmePath) || '';

  const { questions, timeStr } = parseQuizFile(quizContent);
  let answers: Record<number, QuizAnswer> = {};
  
  if (answerContent) {
      answers = parseAnswerKey(answerContent);
      if (questions.length !== Object.keys(answers).length) {
          throw new Error(`Quiz ${slug} has ${questions.length} questions but ${Object.keys(answers).length} answers. Counts must match.`);
      }
  }

  const bands = extractScoreBands(readmeContent, slug);

  return {
    slug,
    timeStr,
    questions,
    answers,
    bands
  };
}

"""
Stack Overflow - V3 Optimized
Full-featured: Users, Questions, Answers, Voting, Badges,
Question status, keyword search, duplicate detection, and tag metadata.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Set
from dataclasses import dataclass, field
import threading


class VoteType(Enum):
    UPVOTE = 1
    DOWNVOTE = -1


class QuestionStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"


class Badge(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


BADGE_THRESHOLDS = {
    Badge.BRONZE: 100,
    Badge.SILVER: 500,
    Badge.GOLD: 1000,
}


@dataclass
class Tag:
    """Metadata wrapper around a tag name, tracking how many questions use it."""
    name: str
    question_count: int = 0


@dataclass
class User:
    user_id: str
    name: str
    email: str
    reputation: int = 1
    questions: List['Question'] = field(default_factory=list)
    answers: List['Answer'] = field(default_factory=list)
    badges: Set[Badge] = field(default_factory=set)

    def update_reputation(self, delta: int) -> None:
        self.reputation = max(1, self.reputation + delta)
        self._check_badges()

    def _check_badges(self) -> None:
        for badge, threshold in BADGE_THRESHOLDS.items():
            if self.reputation >= threshold:
                self.badges.add(badge)

    def add_question(self, question: 'Question') -> None:
        self.questions.append(question)

    def add_answer(self, answer: 'Answer') -> None:
        self.answers.append(answer)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.user_id == other.user_id

    def __hash__(self) -> int:
        return hash(self.user_id)


@dataclass
class Vote:
    user: User
    vote_type: VoteType
    created_at: datetime = field(default_factory=datetime.now)


class Post:
    _counter = 0
    _lock = threading.Lock()

    def __init__(self, author: User, content: str) -> None:
        with Post._lock:
            Post._counter += 1
            self.post_id = f"POST-{Post._counter}"
        self.author = author
        self.content = content
        self.votes: Dict[str, Vote] = {}
        self.created_at = datetime.now()
        self._cached_score = 0
        self._vote_lock = threading.Lock()

    def add_vote(self, vote: Vote) -> bool:
        if vote.user == self.author:
            return False

        voter_id = vote.user.user_id
        with self._vote_lock:
            existing = self.votes.get(voter_id)

            if existing:
                if existing.vote_type == vote.vote_type:
                    return False
                self._cached_score -= existing.vote_type.value
                self.author.update_reputation(-self._get_reputation_delta(existing.vote_type))
                existing.vote_type = vote.vote_type
            else:
                self.votes[voter_id] = vote

            self._cached_score += vote.vote_type.value
            self.author.update_reputation(self._get_reputation_delta(vote.vote_type))
        return True

    def _get_reputation_delta(self, vote_type: VoteType) -> int:
        return 10 if vote_type == VoteType.UPVOTE else -2

    @property
    def score(self) -> int:
        with self._vote_lock:
            return self._cached_score


class Question(Post):
    def __init__(self, author: User, title: str, content: str) -> None:
        super().__init__(author, content)
        self.title = title
        self.answers: List[Answer] = []
        self.accepted_answer: Optional[Answer] = None
        self.tags: Set[str] = set()
        self.status: QuestionStatus = QuestionStatus.OPEN

    def add_answer(self, answer: 'Answer') -> None:
        self.answers.append(answer)

    def accept_answer(self, answer: 'Answer') -> bool:
        if answer not in self.answers:
            return False
        if self.accepted_answer:
            self.accepted_answer.is_accepted = False
        self.accepted_answer = answer
        answer.is_accepted = True
        answer.author.update_reputation(15)
        return True

    def add_tag(self, tag: str) -> bool:
        """Add a tag if the 5-tag limit has not been reached. Returns True if added."""
        if len(self.tags) < 5:
            self.tags.add(tag.lower())
            return True
        return False

    def has_tag(self, tag: str) -> bool:
        return tag.lower() in self.tags

    def close_question(self) -> None:
        self.status = QuestionStatus.CLOSED

    def get_ranked_answers(self) -> List['Answer']:
        """Return answers sorted: accepted first, then by score descending."""
        return sorted(
            self.answers,
            key=lambda a: (a.is_accepted, a.score),
            reverse=True,
        )


class Answer(Post):
    def __init__(self, author: User, question: Question, content: str) -> None:
        super().__init__(author, content)
        self.question = question
        self.is_accepted = False


class StackOverflowService:
    _instance: Optional['StackOverflowService'] = None

    def __new__(cls) -> 'StackOverflowService':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self.users: Dict[str, User] = {}
        self.questions: Dict[str, Question] = {}
        self.tags: Dict[str, Tag] = {}
        self._tag_questions: Dict[str, Set[Question]] = {}
        self._initialized = True

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None
        Post._counter = 0

    def register_user(self, user_id: str, name: str, email: str) -> User:
        if user_id not in self.users:
            self.users[user_id] = User(user_id, name, email)
        return self.users[user_id]

    def post_question(self, author: User, title: str, content: str,
                      tag_names: Optional[List[str]] = None) -> Question:
        question = Question(author, title, content)

        for tag_name in (tag_names or []):
            tag_key = tag_name.lower()
            if not question.add_tag(tag_key):
                continue
            if tag_key not in self.tags:
                self.tags[tag_key] = Tag(tag_key)
                self._tag_questions[tag_key] = set()
            self._tag_questions[tag_key].add(question)
            self.tags[tag_key].question_count = len(self._tag_questions[tag_key])

        author.add_question(question)
        self.questions[question.post_id] = question
        return question

    def post_answer(self, author: User, question: Question, content: str) -> Answer:
        if question.status == QuestionStatus.CLOSED:
            raise ValueError("Cannot answer a closed question")
        answer = Answer(author, question, content)
        question.add_answer(answer)
        author.add_answer(answer)
        return answer

    def vote(self, voter: User, post: Post, vote_type: VoteType) -> bool:
        return post.add_vote(Vote(voter, vote_type))

    def search_by_tag(self, tag_name: str) -> List[Question]:
        return list(self._tag_questions.get(tag_name.lower(), set()))

    def search_by_keyword(self, keyword: str) -> List[Question]:
        """Search questions by keyword in title or content (case-insensitive)."""
        kw = keyword.lower()
        return [
            q for q in self.questions.values()
            if kw in q.title.lower() or kw in q.content.lower()
        ]

    def find_potential_duplicates(self, title: str) -> List[Question]:
        """Find questions whose titles share significant words with the given title."""
        words = set(title.lower().split())
        stop_words = {"a", "an", "the", "in", "is", "to", "how", "what", "of", "and", "or"}
        words -= stop_words
        results: List[Question] = []
        for q in self.questions.values():
            q_words = set(q.title.lower().split()) - stop_words
            if words & q_words:
                results.append(q)
        return results

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def get_question(self, question_id: str) -> Optional[Question]:
        return self.questions.get(question_id)

    def get_tag(self, tag_name: str) -> Optional[Tag]:
        return self.tags.get(tag_name.lower())

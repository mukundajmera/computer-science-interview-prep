"""
Stack Overflow - V1 Basic
Core implementation with users, questions, answers, and voting.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass, field


class VoteType(Enum):
    UPVOTE = 1
    DOWNVOTE = -1


@dataclass
class User:
    user_id: str
    name: str
    email: str
    reputation: int = 1
    questions: List['Question'] = field(default_factory=list)
    answers: List['Answer'] = field(default_factory=list)

    def update_reputation(self, delta: int) -> None:
        self.reputation = max(1, self.reputation + delta)

    def add_question(self, question: 'Question') -> None:
        self.questions.append(question)

    def add_answer(self, answer: 'Answer') -> None:
        self.answers.append(answer)

    def __eq__(self, other) -> bool:
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

    def __init__(self, author: User, content: str):
        Post._counter += 1
        self.post_id = f"POST-{Post._counter}"
        self.author = author
        self.content = content
        self.votes: dict[str, Vote] = {}
        self.created_at = datetime.now()
        self._cached_score = 0

    def add_vote(self, vote: Vote) -> bool:
        if vote.user == self.author:
            return False

        voter_id = vote.user.user_id
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
        return self._cached_score


class Question(Post):
    def __init__(self, author: User, title: str, content: str):
        super().__init__(author, content)
        self.title = title
        self.answers: List[Answer] = []
        self.accepted_answer: Optional[Answer] = None
        self.tags: set[str] = set()

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

    def add_tag(self, tag: str) -> None:
        if len(self.tags) < 5:
            self.tags.add(tag.lower())

    def has_tag(self, tag: str) -> bool:
        return tag.lower() in self.tags


class Answer(Post):
    def __init__(self, author: User, question: Question, content: str):
        super().__init__(author, content)
        self.question = question
        self.is_accepted = False


class StackOverflowService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.users: dict[str, User] = {}
        self.questions: dict[str, Question] = {}
        self.tags: dict[str, set[Question]] = {}
        self._initialized = True

    @classmethod
    def reset_instance(cls):
        cls._instance = None

    def register_user(self, user_id: str, name: str, email: str) -> User:
        if user_id not in self.users:
            self.users[user_id] = User(user_id, name, email)
        return self.users[user_id]

    def post_question(self, author: User, title: str, content: str, 
                     tag_names: List[str] = None) -> Question:
        question = Question(author, title, content)
        
        for tag_name in (tag_names or []):
            tag = tag_name.lower()
            if tag not in self.tags:
                self.tags[tag] = set()
            self.tags[tag].add(question)
            question.add_tag(tag)
        
        author.add_question(question)
        self.questions[question.post_id] = question
        return question

    def post_answer(self, author: User, question: Question, content: str) -> Answer:
        answer = Answer(author, question, content)
        question.add_answer(answer)
        author.add_answer(answer)
        return answer

    def vote(self, voter: User, post: Post, vote_type: VoteType) -> bool:
        return post.add_vote(Vote(voter, vote_type))

    def search_by_tag(self, tag_name: str) -> List[Question]:
        return list(self.tags.get(tag_name.lower(), set()))

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def get_question(self, question_id: str) -> Optional[Question]:
        return self.questions.get(question_id)

"""Stack Overflow Python Module."""
from enum import Enum
from typing import Dict, List
from datetime import datetime

class VoteType(Enum):
    UPVOTE = 1
    DOWNVOTE = -1

class User:
    def __init__(self, id: str, username: str):
        self.id = id
        self.username = username
        self.reputation = 0
    def add_reputation(self, points: int): self.reputation += points
    def __str__(self): return f"User[{self.username}, Rep: {self.reputation}]"

class Answer:
    def __init__(self, id: str, content: str, author: User):
        self.id = id
        self.content = content
        self.author = author
        self.created_at = datetime.now()
        self.votes = 0
        self.is_accepted = False
    def vote(self, value: int): self.votes += value; self.author.add_reputation(value * 10)
    def accept(self): self.is_accepted = True; self.author.add_reputation(15)
    def __str__(self): return f"A[{self.id}]: by {self.author.username} (votes: {self.votes}{'✓' if self.is_accepted else ''})"

class Question:
    def __init__(self, id: str, title: str, content: str, author: User):
        self.id = id
        self.title = title
        self.content = content
        self.author = author
        self.created_at = datetime.now()
        self.answers: List[Answer] = []
        self.tags: set = set()
        self.votes = 0
    def vote(self, value: int): self.votes += value; self.author.add_reputation(value * 5)
    def add_answer(self, a: Answer): self.answers.append(a)
    def __str__(self): return f"Q[{self.id}]: {self.title} (votes: {self.votes}, answers: {len(self.answers)})"

class StackOverflowService:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.users: Dict[str, User] = {}
            cls._instance.questions: Dict[str, Question] = {}
            cls._instance.answers: Dict[str, Answer] = {}
            cls._instance._qc = cls._instance._ac = 0
        return cls._instance
    
    def register_user(self, u: User): self.users[u.id] = u
    
    def post_question(self, user_id: str, title: str, content: str, tags=None) -> Question:
        user = self.users.get(user_id)
        if not user: return None
        self._qc += 1
        q = Question(f"Q-{self._qc}", title, content, user)
        if tags:
            for t in tags: q.tags.add(t)
        self.questions[q.id] = q
        return q
    
    def post_answer(self, user_id: str, question_id: str, content: str) -> Answer:
        user = self.users.get(user_id)
        question = self.questions.get(question_id)
        if not user or not question: return None
        self._ac += 1
        a = Answer(f"A-{self._ac}", content, user)
        self.answers[a.id] = a
        question.add_answer(a)
        return a
    
    def vote(self, post_id: str, vtype: VoteType):
        if post_id.startswith("Q-"):
            q = self.questions.get(post_id)
            if q: q.vote(vtype.value)
        else:
            a = self.answers.get(post_id)
            if a: a.vote(vtype.value)
    
    def accept_answer(self, answer_id: str):
        a = self.answers.get(answer_id)
        if a: a.accept()
    
    def search(self, keyword: str) -> List[Question]:
        kw = keyword.lower()
        return [q for q in self.questions.values() if kw in q.title.lower() or kw in q.content.lower()]

"""
Stack Overflow Test Suite
"""

import unittest
import sys
import os

from concurrent.futures import ThreadPoolExecutor

# Add v3-optimized to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-optimized'))

from stack_overflow import (
    StackOverflowService, VoteType, QuestionStatus, Badge
)


class TestStackOverflow(unittest.TestCase):

    def setUp(self):
        StackOverflowService.reset_instance()
        self.service = StackOverflowService()
        
        self.alice = self.service.register_user("U1", "Alice", "alice@test.com")
        self.bob = self.service.register_user("U2", "Bob", "bob@test.com")
        self.charlie = self.service.register_user("U3", "Charlie", "charlie@test.com")
        
        # Give bob and charlie enough reputation to vote
        for _ in range(20):
            self.bob.update_reputation(10)
            self.charlie.update_reputation(10)

    def test_user_registration(self):
        self.assertIsNotNone(self.alice)
        self.assertEqual("Alice", self.alice.name)
        self.assertEqual(1, self.alice.reputation)

    def test_post_question(self):
        question = self.service.post_question(
            self.alice,
            "What is Python?",
            "Please explain Python basics",
            ["python", "programming"]
        )
        
        self.assertIsNotNone(question)
        self.assertEqual("What is Python?", question.title)
        self.assertEqual(2, len(question.tags))
        self.assertTrue(question.has_tag("python"))

    def test_post_answer(self):
        question = self.service.post_question(
            self.alice, "Test question", "Content", ["test"]
        )
        
        answer = self.service.post_answer(self.bob, question, "This is my answer")
        
        self.assertIsNotNone(answer)
        self.assertEqual(1, len(question.answers))
        self.assertEqual(self.bob, answer.author)

    def test_voting_updates_score_and_reputation(self):
        question = self.service.post_question(
            self.alice, "Test", "Content", ["test"]
        )
        
        initial_rep = self.alice.reputation
        
        voted = self.service.vote(self.bob, question, VoteType.UPVOTE)
        
        self.assertTrue(voted)
        self.assertEqual(1, question.score)
        self.assertEqual(initial_rep + 10, self.alice.reputation)

    def test_cannot_vote_on_own_post(self):
        question = self.service.post_question(
            self.alice, "Test", "Content", ["test"]
        )
        
        # Give alice voting privileges
        for _ in range(20):
            self.alice.update_reputation(10)
        
        voted = self.service.vote(self.alice, question, VoteType.UPVOTE)
        
        self.assertFalse(voted)
        self.assertEqual(0, question.score)

    def test_accept_answer_gives_reputation(self):
        question = self.service.post_question(
            self.alice, "Test", "Content", ["test"]
        )
        answer = self.service.post_answer(self.bob, question, "Answer")
        
        rep_before = self.bob.reputation
        accepted = question.accept_answer(answer)
        
        self.assertTrue(accepted)
        self.assertTrue(answer.is_accepted)
        self.assertEqual(rep_before + 15, self.bob.reputation)

    def test_search_by_tag(self):
        self.service.post_question(self.alice, "Java Q", "Content", ["java"])
        self.service.post_question(self.bob, "Python Q", "Content", ["python"])
        
        results = self.service.search_by_tag("java")
        
        self.assertEqual(1, len(results))
        self.assertEqual("Java Q", results[0].title)

    def test_search_by_keyword(self):
        self.service.post_question(self.alice, "Java Memory", "About heap", ["java"])
        self.service.post_question(self.bob, "Python Lists", "About lists", ["python"])
        
        results = self.service.search_by_keyword("memory")
        
        self.assertEqual(1, len(results))
        self.assertIn("Memory", results[0].title)

    def test_answer_ranking_puts_accepted_first(self):
        question = self.service.post_question(
            self.alice, "Test", "Content", ["test"]
        )
        
        answer1 = self.service.post_answer(self.bob, question, "First answer")
        answer2 = self.service.post_answer(self.charlie, question, "Second answer")
        
        # Upvote first answer
        voter = self.service.register_user("V1", "Voter", "v@test.com")
        for _ in range(20):
            voter.update_reputation(10)
        self.service.vote(voter, answer1, VoteType.UPVOTE)
        
        # Accept second answer
        question.accept_answer(answer2)
        
        ranked = question.get_ranked_answers()
        
        self.assertEqual(answer2, ranked[0])  # Accepted answer first
        self.assertEqual(answer1, ranked[1])

    def test_concurrent_voting_is_thread_safe(self):
        question = self.service.post_question(
            self.alice, "Test", "Content", ["test"]
        )
        
        def voter_task(idx):
            voter = self.service.register_user(f"V{idx}", f"Voter{idx}", f"v{idx}@test.com")
            for _ in range(20):
                voter.update_reputation(10)
            return self.service.vote(voter, question, VoteType.UPVOTE)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(voter_task, range(10)))
        
        self.assertEqual(10, question.score)
        self.assertTrue(all(results))

    def test_duplicate_detection(self):
        self.service.post_question(
            self.alice, "How to sort array in Java", "Content", ["java"]
        )
        
        duplicates = self.service.find_potential_duplicates("sorting array in Java")
        
        self.assertGreater(len(duplicates), 0)

    def test_badges_awarded_correctly(self):
        user = self.service.register_user("TEST", "Test", "test@test.com")
        
        # Initially no badges
        self.assertEqual(0, len(user.badges))
        
        # Get to 100 reputation
        for _ in range(10):
            user.update_reputation(10)
        self.assertIn(Badge.BRONZE, user.badges)
        
        # Get to 500 reputation
        for _ in range(40):
            user.update_reputation(10)
        self.assertIn(Badge.SILVER, user.badges)

    def test_question_status_change(self):
        question = self.service.post_question(
            self.alice, "Test", "Content", ["test"]
        )
        
        self.assertEqual(QuestionStatus.OPEN, question.status)
        
        question.close_question()
        self.assertEqual(QuestionStatus.CLOSED, question.status)
        
        # Cannot add answer to closed question
        with self.assertRaises(ValueError):
            self.service.post_answer(self.bob, question, "Answer")

    def test_tag_counts(self):
        self.service.post_question(self.alice, "Q1", "Content", ["java"])
        self.service.post_question(self.bob, "Q2", "Content", ["java", "spring"])
        
        java_tag = self.service.get_tag("java")
        
        self.assertIsNotNone(java_tag)
        self.assertEqual(2, java_tag.question_count)

    def test_max_five_tags_per_question(self):
        question = self.service.post_question(
            self.alice, "Test", "Content",
            ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"]
        )
        
        self.assertEqual(5, len(question.tags))


if __name__ == "__main__":
    unittest.main()

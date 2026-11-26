"""
Stack Overflow V1 Basic - Demo
"""

from stack_overflow import (
    StackOverflowService, VoteType
)


def main():
    print("=== Stack Overflow V1 (Basic) Demo ===\n")
    
    StackOverflowService.reset_instance()
    service = StackOverflowService()
    
    # Register users
    alice = service.register_user("U1", "Alice", "alice@example.com")
    bob = service.register_user("U2", "Bob", "bob@example.com")
    charlie = service.register_user("U3", "Charlie", "charlie@example.com")
    
    print("Users registered:")
    print(f"  - {alice.name} (reputation: {alice.reputation})")
    print(f"  - {bob.name} (reputation: {bob.reputation})")
    print(f"  - {charlie.name} (reputation: {charlie.reputation})")
    
    # Alice posts a question
    question = service.post_question(
        alice,
        "How does Python garbage collection work?",
        "Can someone explain reference counting and gc module?",
        ["python", "memory", "gc"]
    )
    print(f"\nQuestion posted: {question.title}")
    print(f"Tags: {question.tags}")
    
    # Bob answers
    bob_answer = service.post_answer(
        bob, question,
        "Python uses reference counting primarily..."
    )
    print(f"\nBob answered (ID: {bob_answer.post_id})")
    
    # Charlie answers
    charlie_answer = service.post_answer(
        charlie, question,
        "The gc module handles circular references..."
    )
    print(f"Charlie answered (ID: {charlie_answer.post_id})")
    
    # Voting
    service.vote(bob, question, VoteType.UPVOTE)
    print(f"\nBob upvoted the question")
    print(f"Question score: {question.score}")
    print(f"Alice reputation: {alice.reputation}")
    
    service.vote(charlie, bob_answer, VoteType.UPVOTE)
    print(f"\nCharlie upvoted Bob's answer")
    print(f"Bob's answer score: {bob_answer.score}")
    print(f"Bob reputation: {bob.reputation}")
    
    # Accept answer
    question.accept_answer(bob_answer)
    print(f"\nAlice accepted Bob's answer")
    print(f"Bob's answer accepted: {bob_answer.is_accepted}")
    print(f"Bob reputation after acceptance: {bob.reputation}")
    
    # Search by tag
    results = service.search_by_tag("python")
    print(f"\nSearch 'python': {len(results)} questions found")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()

"""
State Pattern - V3 Advanced: Document Review Workflow

Shows guarded transitions, audit-friendly context data, and state-specific
behavior for a collaborative publishing workflow.
"""
from abc import ABC
from dataclasses import dataclass, field
from typing import List, Optional


class DocumentState(ABC):
    """Base state with explicit transition guards."""

    status = "UNKNOWN"

    def edit(self, workflow: "DocumentWorkflow", content: str) -> None:
        raise ValueError(f"Cannot edit document while {workflow.status}")

    def submit_for_review(self, workflow: "DocumentWorkflow", author: str) -> None:
        raise ValueError(f"Cannot submit document while {workflow.status}")

    def approve(self, workflow: "DocumentWorkflow", reviewer: str) -> None:
        raise ValueError(f"Cannot approve document while {workflow.status}")

    def publish(self, workflow: "DocumentWorkflow", publisher: str) -> None:
        raise ValueError(f"Cannot publish document while {workflow.status}")

    def archive(self, workflow: "DocumentWorkflow", reason: str) -> None:
        raise ValueError(f"Cannot archive document while {workflow.status}")


class DraftState(DocumentState):
    status = "DRAFT"

    def edit(self, workflow: "DocumentWorkflow", content: str) -> None:
        workflow.content = content

    def submit_for_review(self, workflow: "DocumentWorkflow", author: str) -> None:
        workflow.submitted_by = author
        workflow.set_state(InReviewState())


class InReviewState(DocumentState):
    status = "IN_REVIEW"

    def edit(self, workflow: "DocumentWorkflow", content: str) -> None:
        workflow.content = content
        workflow.approvals.clear()

    def approve(self, workflow: "DocumentWorkflow", reviewer: str) -> None:
        if reviewer not in workflow.approvals:
            workflow.approvals.append(reviewer)

    def publish(self, workflow: "DocumentWorkflow", publisher: str) -> None:
        if not workflow.approvals:
            raise ValueError("Document needs at least one approval before publishing")
        workflow.published_by = publisher
        workflow.set_state(PublishedState())


class PublishedState(DocumentState):
    status = "PUBLISHED"

    def edit(self, workflow: "DocumentWorkflow", content: str) -> None:
        raise ValueError("Cannot edit published document")

    def archive(self, workflow: "DocumentWorkflow", reason: str) -> None:
        workflow.archive_reason = reason
        workflow.set_state(ArchivedState())


class ArchivedState(DocumentState):
    status = "ARCHIVED"


@dataclass
class DocumentWorkflow:
    """Context that delegates document actions to state objects."""

    document_id: str
    state: DocumentState = field(default_factory=DraftState)
    content: str = ""
    submitted_by: Optional[str] = None
    published_by: Optional[str] = None
    archive_reason: Optional[str] = None
    approvals: List[str] = field(default_factory=list)
    audit_log: List[str] = field(default_factory=lambda: ["DRAFT"])

    @property
    def status(self) -> str:
        return self.state.status

    def set_state(self, state: DocumentState) -> None:
        self.state = state
        self.audit_log.append(state.status)

    def edit(self, content: str) -> None:
        self.state.edit(self, content)

    def submit_for_review(self, author: str) -> None:
        self.state.submit_for_review(self, author)

    def approve(self, reviewer: str) -> None:
        self.state.approve(self, reviewer)

    def publish(self, publisher: str) -> None:
        self.state.publish(self, publisher)

    def archive(self, reason: str) -> None:
        self.state.archive(self, reason)


if __name__ == "__main__":
    workflow = DocumentWorkflow("design-doc")
    workflow.edit("Initial design")
    workflow.submit_for_review("alice")
    workflow.approve("lead")
    workflow.publish("alice")
    print(f"{workflow.document_id}: {workflow.status}")
    print(" -> ".join(workflow.audit_log))

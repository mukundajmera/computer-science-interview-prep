/**
 * State Pattern - V3 Advanced: Document Review Workflow
 *
 * Demonstrates guarded transitions, state-specific editing rules, and an
 * audit-friendly workflow context.
 */

import java.util.ArrayList;
import java.util.List;

interface DocumentState {
    String getStatus();
    default void edit(DocumentWorkflow workflow, String content) {
        throw new IllegalStateException("Cannot edit document while " + workflow.getStatus());
    }
    default void submitForReview(DocumentWorkflow workflow, String author) {
        throw new IllegalStateException("Cannot submit document while " + workflow.getStatus());
    }
    default void approve(DocumentWorkflow workflow, String reviewer) {
        throw new IllegalStateException("Cannot approve document while " + workflow.getStatus());
    }
    default void publish(DocumentWorkflow workflow, String publisher) {
        throw new IllegalStateException("Cannot publish document while " + workflow.getStatus());
    }
    default void archive(DocumentWorkflow workflow, String reason) {
        throw new IllegalStateException("Cannot archive document while " + workflow.getStatus());
    }
}

class DraftDocumentState implements DocumentState {
    @Override public String getStatus() { return "DRAFT"; }
    @Override public void edit(DocumentWorkflow workflow, String content) {
        workflow.setContent(content);
    }
    @Override public void submitForReview(DocumentWorkflow workflow, String author) {
        workflow.setSubmittedBy(author);
        workflow.setState(new InReviewDocumentState());
    }
}

class InReviewDocumentState implements DocumentState {
    @Override public String getStatus() { return "IN_REVIEW"; }
    @Override public void edit(DocumentWorkflow workflow, String content) {
        workflow.setContent(content);
        workflow.clearApprovals();
    }
    @Override public void approve(DocumentWorkflow workflow, String reviewer) {
        workflow.addApproval(reviewer);
    }
    @Override public void publish(DocumentWorkflow workflow, String publisher) {
        if (workflow.getApprovals().isEmpty()) {
            throw new IllegalStateException("Document needs at least one approval before publishing");
        }
        workflow.setPublishedBy(publisher);
        workflow.setState(new PublishedDocumentState());
    }
}

class PublishedDocumentState implements DocumentState {
    @Override public String getStatus() { return "PUBLISHED"; }
    @Override public void edit(DocumentWorkflow workflow, String content) {
        throw new IllegalStateException("Cannot edit published document");
    }
    @Override public void archive(DocumentWorkflow workflow, String reason) {
        workflow.setArchiveReason(reason);
        workflow.setState(new ArchivedDocumentState());
    }
}

class ArchivedDocumentState implements DocumentState {
    @Override public String getStatus() { return "ARCHIVED"; }
}

class DocumentWorkflow {
    private final String documentId;
    private final List<String> approvals = new ArrayList<>();
    private final List<String> auditLog = new ArrayList<>();
    private DocumentState state = new DraftDocumentState();
    private String content = "";
    private String submittedBy;
    private String publishedBy;
    private String archiveReason;

    public DocumentWorkflow(String documentId) {
        this.documentId = documentId;
        auditLog.add("DRAFT");
    }

    public String getDocumentId() { return documentId; }
    public String getStatus() { return state.getStatus(); }
    public DocumentState getState() { return state; }
    public String getContent() { return content; }
    public String getSubmittedBy() { return submittedBy; }
    public String getPublishedBy() { return publishedBy; }
    public String getArchiveReason() { return archiveReason; }
    public List<String> getApprovals() { return new ArrayList<>(approvals); }
    public List<String> getAuditLog() { return new ArrayList<>(auditLog); }

    public void setContent(String content) { this.content = content; }
    public void setSubmittedBy(String submittedBy) { this.submittedBy = submittedBy; }
    public void setPublishedBy(String publishedBy) { this.publishedBy = publishedBy; }
    public void setArchiveReason(String archiveReason) { this.archiveReason = archiveReason; }

    public void addApproval(String reviewer) {
        if (!approvals.contains(reviewer)) {
            approvals.add(reviewer);
        }
    }

    public void clearApprovals() { approvals.clear(); }

    public void setState(DocumentState state) {
        this.state = state;
        auditLog.add(state.getStatus());
    }

    public void edit(String content) { state.edit(this, content); }
    public void submitForReview(String author) { state.submitForReview(this, author); }
    public void approve(String reviewer) { state.approve(this, reviewer); }
    public void publish(String publisher) { state.publish(this, publisher); }
    public void archive(String reason) { state.archive(this, reason); }
}

public class DocumentWorkflowDemo {
    public static void main(String[] args) {
        DocumentWorkflow workflow = new DocumentWorkflow("design-doc");
        workflow.edit("Initial design");
        workflow.submitForReview("alice");
        workflow.approve("lead");
        workflow.publish("alice");

        System.out.println(workflow.getDocumentId() + ": " + workflow.getStatus());
        System.out.println(workflow.getAuditLog());
    }
}

package models;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;

/**
 * Loan.java - Book loan record.
 */
public class Loan {
    private final String loanId;
    private final Book book;
    private final Member member;
    private final LocalDate borrowDate;
    private final LocalDate dueDate;
    private LocalDate returnDate;
    private static final double DAILY_FINE = 0.50;

    public Loan(String loanId, Book book, Member member) {
        this.loanId = loanId;
        this.book = book;
        this.member = member;
        this.borrowDate = LocalDate.now();
        this.dueDate = borrowDate.plusDays(member.getLoanDays());
        this.returnDate = null;
    }

    public String getLoanId() {
        return loanId;
    }

    public Book getBook() {
        return book;
    }

    public Member getMember() {
        return member;
    }

    public LocalDate getBorrowDate() {
        return borrowDate;
    }

    public LocalDate getDueDate() {
        return dueDate;
    }

    public LocalDate getReturnDate() {
        return returnDate;
    }

    public boolean isReturned() {
        return returnDate != null;
    }

    public void returnBook() {
        this.returnDate = LocalDate.now();
    }

    public double calculateFine() {
        LocalDate checkDate = returnDate != null ? returnDate : LocalDate.now();
        long daysLate = ChronoUnit.DAYS.between(dueDate, checkDate);
        return Math.max(0, daysLate * DAILY_FINE);
    }

    @Override
    public String toString() {
        return String.format("Loan[%s: %s -> %s, Due: %s]",
                loanId, book.getTitle(), member.getName(), dueDate);
    }
}

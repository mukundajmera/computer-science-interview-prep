package enums;

/**
 * MemberType.java - Types of library members with borrowing limits.
 */
public enum MemberType {
    STUDENT(5, 14), // 5 books, 14 days
    FACULTY(10, 30), // 10 books, 30 days
    PUBLIC(3, 7); // 3 books, 7 days

    private final int borrowLimit;
    private final int loanDays;

    MemberType(int borrowLimit, int loanDays) {
        this.borrowLimit = borrowLimit;
        this.loanDays = loanDays;
    }

    public int getBorrowLimit() {
        return borrowLimit;
    }

    public int getLoanDays() {
        return loanDays;
    }
}

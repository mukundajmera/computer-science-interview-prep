package models;

import enums.MemberType;
import java.util.ArrayList;
import java.util.List;

/**
 * Member.java - Library member entity.
 */
public class Member {
    private final String memberId;
    private String name;
    private final MemberType type;
    private final List<Loan> activeLoans;

    public Member(String memberId, String name, MemberType type) {
        this.memberId = memberId;
        this.name = name;
        this.type = type;
        this.activeLoans = new ArrayList<>();
    }

    public String getMemberId() {
        return memberId;
    }

    public String getName() {
        return name;
    }

    public MemberType getType() {
        return type;
    }

    public int getBorrowLimit() {
        return type.getBorrowLimit();
    }

    public int getLoanDays() {
        return type.getLoanDays();
    }

    public boolean canBorrow() {
        return activeLoans.size() < getBorrowLimit();
    }

    public void addLoan(Loan loan) {
        activeLoans.add(loan);
    }

    public void removeLoan(Loan loan) {
        activeLoans.remove(loan);
    }

    public List<Loan> getActiveLoans() {
        return new ArrayList<>(activeLoans);
    }

    @Override
    public String toString() {
        return String.format("Member[%s: %s (%s)]", memberId, name, type);
    }
}

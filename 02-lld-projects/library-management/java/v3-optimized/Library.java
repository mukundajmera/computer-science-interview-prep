import enums.BookStatus;
import models.Book;
import models.Member;
import models.Loan;
import java.util.*;

/**
 * Library.java - Singleton library management system.
 */
public class Library {
    private static Library instance;
    private final String name;
    private final Map<String, Book> books;
    private final Map<String, Member> members;
    private final Map<String, Loan> loans;
    private int loanCounter;

    private Library(String name) {
        this.name = name;
        this.books = new HashMap<>();
        this.members = new HashMap<>();
        this.loans = new HashMap<>();
        this.loanCounter = 0;
    }

    public static synchronized Library getInstance(String name) {
        if (instance == null) {
            instance = new Library(name);
        }
        return instance;
    }

    public void addBook(Book book) {
        books.put(book.getIsbn(), book);
    }

    public void registerMember(Member member) {
        members.put(member.getMemberId(), member);
    }

    public Loan borrowBook(String memberId, String isbn) {
        Member member = members.get(memberId);
        Book book = books.get(isbn);

        if (member == null || book == null) {
            System.out.println("Invalid member or book");
            return null;
        }

        if (!member.canBorrow()) {
            System.out.println("Member has reached borrow limit");
            return null;
        }

        if (book.getStatus() != BookStatus.AVAILABLE) {
            System.out.println("Book is not available");
            return null;
        }

        String loanId = "LOAN-" + (++loanCounter);
        Loan loan = new Loan(loanId, book, member);
        loans.put(loanId, loan);
        member.addLoan(loan);
        book.setStatus(BookStatus.BORROWED);

        System.out.println("Borrowed: " + book.getTitle());
        return loan;
    }

    public double returnBook(String loanId) {
        Loan loan = loans.get(loanId);
        if (loan == null || loan.isReturned()) {
            System.out.println("Invalid loan");
            return 0;
        }

        loan.returnBook();
        loan.getBook().setStatus(BookStatus.AVAILABLE);
        loan.getMember().removeLoan(loan);

        double fine = loan.calculateFine();
        System.out.println("Returned: " + loan.getBook().getTitle() +
                (fine > 0 ? " - Fine: $" + fine : ""));
        return fine;
    }

    public List<Book> searchByTitle(String title) {
        List<Book> results = new ArrayList<>();
        for (Book book : books.values()) {
            if (book.getTitle().toLowerCase().contains(title.toLowerCase())) {
                results.add(book);
            }
        }
        return results;
    }

    public String getName() {
        return name;
    }
}

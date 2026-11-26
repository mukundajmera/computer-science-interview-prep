import enums.MemberType;
import models.Book;
import models.Member;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.*;

public class LibraryDemo {
    public static void main(String[] args) {
        System.out.println("=== Library Management System V2 Demo ===\n");

        Library.resetInstance();
        Library library = Library.getInstance("City Public Library");

        // Add observer
        library.addObserver(new NotificationService());

        // Set tiered fine calculator
        library.setFineCalculator(new TieredFine(0.50, 1.00));

        // Add books
        Book book1 = new Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin", 
                              BookCategory.TECHNOLOGY, 2008);
        book1.addCopy();

        Book book2 = new Book("978-0-14-028329-7", "1984", "George Orwell", 
                              BookCategory.FICTION, 1949);
        book2.addCopy();

        library.addBook(book1);
        library.addBook(book2);

        // Register members
        Member member1 = new Member("M001", "John Doe", "john@email.com", MemberType.STUDENT);
        Member member2 = new Member("M002", "Jane Smith", "jane@email.com", MemberType.TEACHER);

        library.registerMember(member1);
        library.registerMember(member2);

        // Issue book
        System.out.println("--- Issuing Book ---");
        BorrowingRecord record = library.issueBook("M001", "978-0-13-468599-1-001");

        // Try to reserve (book not available)
        System.out.println("\n--- Creating Reservation ---");
        Reservation res = library.reserveBook("M002", "978-0-13-468599-1");

        // Return book (triggers notification)
        System.out.println("\n--- Returning Book ---");
        if (record != null) {
            library.returnBook(record.getRecordId());
        }

        library.displayStatus();

        System.out.println("\n=== Demo Complete ===");
    }
}

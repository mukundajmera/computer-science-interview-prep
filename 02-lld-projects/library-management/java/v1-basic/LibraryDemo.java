import enums.MemberType;
import models.Book;
import models.Member;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.*;

public class LibraryDemo {
    public static void main(String[] args) {
        System.out.println("=== Library Management System Demo ===\n");

        Library.resetInstance();
        Library library = Library.getInstance("City Public Library");

        // Add books
        Book book1 = new Book("978-0-13-468599-1", "Clean Code", "Robert C. Martin", 
                              BookCategory.TECHNOLOGY, 2008);
        book1.addCopy();
        book1.addCopy();

        Book book2 = new Book("978-0-59-651798-1", "Head First Design Patterns", 
                              "Eric Freeman", BookCategory.TECHNOLOGY, 2004);
        book2.addCopy();

        Book book3 = new Book("978-0-14-028329-7", "1984", "George Orwell", 
                              BookCategory.FICTION, 1949);
        book3.addCopy();
        book3.addCopy();
        book3.addCopy();

        library.addBook(book1);
        library.addBook(book2);
        library.addBook(book3);

        // Register members
        Member member1 = new Member("M001", "John Doe", "john@email.com", MemberType.STUDENT);
        Member member2 = new Member("M002", "Jane Smith", "jane@email.com", MemberType.TEACHER);

        library.registerMember(member1);
        library.registerMember(member2);

        library.displayStatus();
        library.displayBooks();

        // Issue books
        System.out.println("\n--- Issuing Books ---");
        BorrowingRecord record1 = library.issueBook("M001", "978-0-13-468599-1-001");
        BorrowingRecord record2 = library.issueBook("M002", "978-0-59-651798-1-001");

        // Search books
        System.out.println("\n--- Searching Books ---");
        List<Book> results = library.searchByAuthor("Robert");
        System.out.println("Found " + results.size() + " books by 'Robert'");

        // Return book
        System.out.println("\n--- Returning Book ---");
        if (record1 != null) {
            double fine = library.returnBook(record1.getRecordId());
            System.out.println("Fine paid: $" + fine);
        }

        library.displayStatus();

        System.out.println("\n=== Demo Complete ===");
    }
}

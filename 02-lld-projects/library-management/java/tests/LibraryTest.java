import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for Library Management System
 */
class LibraryTest {

    @BeforeEach
    void setUp() {
        Library.resetInstance();
    }

    @AfterEach
    void tearDown() {
        Library.resetInstance();
    }

    @Test
    @DisplayName("Library singleton returns same instance")
    void testSingleton() {
        Library lib1 = Library.getInstance();
        Library lib2 = Library.getInstance();
        assertSame(lib1, lib2);
    }

    @Test
    @DisplayName("Add book to library")
    void testAddBook() {
        Library library = Library.getInstance();
        Book book = new Book("978-0-13-468599-1", "Clean Code", "Robert Martin", 
                            BookCategory.TECHNOLOGY, 2008);
        library.addBook(book);
        
        assertEquals(1, library.getBookCount());
        assertNotNull(library.getBook("978-0-13-468599-1"));
    }

    @Test
    @DisplayName("Add copies to book")
    void testAddCopies() {
        Book book = new Book("978-0-13-468599-1", "Clean Code", "Robert Martin", 
                            BookCategory.TECHNOLOGY, 2008);
        book.addCopy();
        book.addCopy();
        book.addCopy();
        
        assertEquals(3, book.getTotalCopies());
        assertEquals(3, book.getAvailableCopies().size());
    }

    @Test
    @DisplayName("Register member")
    void testRegisterMember() {
        Library library = Library.getInstance();
        Member member = new Member("M001", "John Doe", "john@email.com", MemberType.STUDENT);
        library.registerMember(member);
        
        assertEquals(1, library.getMemberCount());
        assertNotNull(library.getMember("M001"));
    }

    @Test
    @DisplayName("Issue book to member")
    void testIssueBook() {
        Library library = Library.getInstance();
        
        Book book = new Book("978-0-13-468599-1", "Clean Code", "Robert Martin", 
                            BookCategory.TECHNOLOGY, 2008);
        BookCopy copy = book.addCopy();
        library.addBook(book);
        
        Member member = new Member("M001", "John Doe", "john@email.com", MemberType.STUDENT);
        library.registerMember(member);
        
        BorrowingRecord record = library.issueBook("M001", copy.getCopyId());
        
        assertNotNull(record);
        assertEquals(member, record.getMember());
        assertEquals(copy, record.getBookCopy());
        assertFalse(copy.isAvailable());
    }

    @Test
    @DisplayName("Prevent borrowing over limit")
    void testBorrowingLimit() {
        Library library = Library.getInstance();
        
        Book book = new Book("978-0-13-468599-1", "Clean Code", "Robert Martin", 
                            BookCategory.TECHNOLOGY, 2008);
        for (int i = 0; i < 5; i++) {
            book.addCopy();
        }
        library.addBook(book);
        
        // Student has limit of 3
        Member member = new Member("M001", "John Doe", "john@email.com", MemberType.STUDENT);
        library.registerMember(member);
        
        // Borrow 3 books (should succeed)
        for (int i = 0; i < 3; i++) {
            assertNotNull(library.issueBook("M001", book.getCopies().get(i).getCopyId()));
        }
        
        // 4th should fail
        assertNull(library.issueBook("M001", book.getCopies().get(3).getCopyId()));
    }

    @Test
    @DisplayName("Return book and calculate fee")
    void testReturnBook() {
        Library library = Library.getInstance();
        
        Book book = new Book("978-0-13-468599-1", "Clean Code", "Robert Martin", 
                            BookCategory.TECHNOLOGY, 2008);
        BookCopy copy = book.addCopy();
        library.addBook(book);
        
        Member member = new Member("M001", "John Doe", "john@email.com", MemberType.STUDENT);
        library.registerMember(member);
        
        BorrowingRecord record = library.issueBook("M001", copy.getCopyId());
        assertNotNull(record);
        
        double fine = library.returnBook(record.getRecordId());
        
        assertEquals(0, fine); // No overdue
        assertTrue(copy.isAvailable());
    }

    @Test
    @DisplayName("Search books by title")
    void testSearchByTitle() {
        Library library = Library.getInstance();
        
        library.addBook(new Book("ISBN-1", "Clean Code", "Robert Martin", 
                                BookCategory.TECHNOLOGY, 2008));
        library.addBook(new Book("ISBN-2", "Clean Architecture", "Robert Martin", 
                                BookCategory.TECHNOLOGY, 2017));
        library.addBook(new Book("ISBN-3", "1984", "George Orwell", 
                                BookCategory.FICTION, 1949));
        
        java.util.List<Book> results = library.searchByTitle("clean");
        
        assertEquals(2, results.size());
    }

    @Test
    @DisplayName("Search books by author")
    void testSearchByAuthor() {
        Library library = Library.getInstance();
        
        library.addBook(new Book("ISBN-1", "Clean Code", "Robert Martin", 
                                BookCategory.TECHNOLOGY, 2008));
        library.addBook(new Book("ISBN-2", "Clean Architecture", "Robert Martin", 
                                BookCategory.TECHNOLOGY, 2017));
        library.addBook(new Book("ISBN-3", "1984", "George Orwell", 
                                BookCategory.FICTION, 1949));
        
        java.util.List<Book> results = library.searchByAuthor("Robert");
        
        assertEquals(2, results.size());
    }

    @Test
    @DisplayName("Cannot issue unavailable book")
    void testCannotIssueUnavailableBook() {
        Library library = Library.getInstance();
        
        Book book = new Book("978-0-13-468599-1", "Clean Code", "Robert Martin", 
                            BookCategory.TECHNOLOGY, 2008);
        BookCopy copy = book.addCopy();
        library.addBook(book);
        
        Member member1 = new Member("M001", "John Doe", "john@email.com", MemberType.STUDENT);
        Member member2 = new Member("M002", "Jane Doe", "jane@email.com", MemberType.STUDENT);
        library.registerMember(member1);
        library.registerMember(member2);
        
        // First member borrows
        assertNotNull(library.issueBook("M001", copy.getCopyId()));
        
        // Second member tries to borrow same copy - should fail
        assertNull(library.issueBook("M002", copy.getCopyId()));
    }

    @Test
    @DisplayName("BookCopy status changes correctly")
    void testBookCopyStatus() {
        Book book = new Book("ISBN-1", "Test Book", "Author", BookCategory.FICTION, 2020);
        BookCopy copy = book.addCopy();
        
        assertTrue(copy.isAvailable());
        assertEquals(CopyStatus.AVAILABLE, copy.getStatus());
        
        assertTrue(copy.borrow());
        assertFalse(copy.isAvailable());
        assertEquals(CopyStatus.BORROWED, copy.getStatus());
        
        copy.returnBook();
        assertTrue(copy.isAvailable());
        assertEquals(CopyStatus.AVAILABLE, copy.getStatus());
    }

    @Test
    @DisplayName("Member canBorrow works correctly")
    void testMemberCanBorrow() {
        Member student = new Member("M001", "Student", "s@email.com", MemberType.STUDENT);
        Member teacher = new Member("M002", "Teacher", "t@email.com", MemberType.TEACHER);
        
        assertTrue(student.canBorrow());
        assertTrue(teacher.canBorrow());
        
        assertEquals(3, student.getBorrowLimit());
        assertEquals(5, teacher.getBorrowLimit());
    }
}

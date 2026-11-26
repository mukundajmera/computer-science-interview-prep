package models;

import enums.BookStatus;

/**
 * Book.java - Library book entity.
 */
public class Book {
    private final String isbn;
    private String title;
    private String author;
    private BookStatus status;

    public Book(String isbn, String title, String author) {
        this.isbn = isbn;
        this.title = title;
        this.author = author;
        this.status = BookStatus.AVAILABLE;
    }

    public String getIsbn() {
        return isbn;
    }

    public String getTitle() {
        return title;
    }

    public String getAuthor() {
        return author;
    }

    public BookStatus getStatus() {
        return status;
    }

    public void setStatus(BookStatus status) {
        this.status = status;
    }

    @Override
    public String toString() {
        return String.format("Book[%s: %s by %s - %s]", isbn, title, author, status);
    }
}

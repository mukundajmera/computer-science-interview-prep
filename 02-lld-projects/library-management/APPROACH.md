# Design Approach for Library Management System

A step-by-step thought process for designing the library management system.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| Library | ✅ Yes | Main system container |
| Book | ✅ Yes | Item being tracked |
| BookCopy | ✅ Yes | Physical copy (multiple per book) |
| Member | ✅ Yes | User who borrows |
| Librarian | ✅ Yes | Staff who manages (v2) |
| Borrowing Record | ✅ Yes | Transaction record |
| Reservation | ✅ Yes | Future booking (v2) |
| Fine | ✅ Yes | Penalty calculation |

**Final Entities**: Library, Book, BookCopy, Member, BorrowingRecord, Reservation, Fine

---

## Step 2: Define Relationships

```
Library (1) ──contains──> (n) Book
Book (1) ──has──> (n) BookCopy
Library (1) ──has──> (n) Member
Member (1) ──borrows──> (n) BookCopy
BorrowingRecord ──links──> Member + BookCopy
Reservation ──links──> Member + Book
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| Library → Book | Composition | Books belong to library |
| Book → BookCopy | Composition | Copies belong to book |
| Library → Member | Aggregation | Members can exist independently |
| Member → BorrowingRecord | Association | Transaction history |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Singleton** | ✅ Yes | Single library instance |
| **Factory** | ✅ Yes | Create different member types |
| **Observer** | ✅ v2 | Notifications for due dates, reservations |
| **Strategy** | ✅ v2 | Different search algorithms |
| **Composite** | 🔄 Optional | Book categories/collections |
| **State** | ❌ No | Book states are simple |

### Pattern Application:

1. **Singleton Pattern** - Library
   - Single point of control
   - Centralized catalog management

2. **Factory Pattern** - MemberFactory
   - Create Student, Teacher, Staff members
   - Different borrowing limits per type

3. **Observer Pattern** - NotificationService (v2)
   - Notify on due date approaching
   - Notify when reserved book available

4. **Strategy Pattern** - SearchStrategy (v2)
   - Search by title, author, ISBN
   - Full-text search, fuzzy search

---

## Step 4: Design Classes

### Core Classes:

#### Library (Singleton)
- **Attributes**: 
  - `books: Map<String, Book>` (ISBN → Book)
  - `members: Map<String, Member>` (memberId → Member)
  - `activeLoans: Map<String, BorrowingRecord>`
- **Methods**:
  - `addBook(book)`, `removeBook(isbn)`
  - `registerMember(member)`, `removeMember(id)`
  - `issueBook(memberId, bookCopyId): BorrowingRecord`
  - `returnBook(recordId): Fine`
  - `searchBooks(query): List<Book>`

#### Book
- **Attributes**:
  - `isbn: String`
  - `title: String`
  - `author: String`
  - `category: BookCategory`
  - `copies: List<BookCopy>`
- **Methods**:
  - `getAvailableCopies(): List<BookCopy>`
  - `addCopy()`, `removeCopy(id)`

#### BookCopy
- **Attributes**:
  - `copyId: String`
  - `book: Book`
  - `status: CopyStatus` (AVAILABLE, BORROWED, RESERVED, LOST)
  - `condition: BookCondition`
- **Methods**:
  - `borrow(): boolean`
  - `return(): void`
  - `isAvailable(): boolean`

#### Member
- **Attributes**:
  - `memberId: String`
  - `name: String`
  - `email: String`
  - `borrowedBooks: List<BorrowingRecord>`
  - `borrowLimit: int`
- **Methods**:
  - `canBorrow(): boolean`
  - `getBorrowedCount(): int`

#### BorrowingRecord
- **Attributes**:
  - `recordId: String`
  - `member: Member`
  - `bookCopy: BookCopy`
  - `issueDate: Date`
  - `dueDate: Date`
  - `returnDate: Date`
  - `fine: Fine`
- **Methods**:
  - `isOverdue(): boolean`
  - `getDaysOverdue(): int`

#### Fine
- **Attributes**:
  - `amount: double`
  - `record: BorrowingRecord`
  - `isPaid: boolean`
- **Methods**:
  - `calculate(daysOverdue): double`

---

## Step 5: Handle Edge Cases

### Input Validation:
- Null/empty book or member
- Invalid ISBN format
- Non-existent member or book

### Business Logic:
- Member borrowing limit reached
- Book not available (all copies borrowed)
- Returning already returned book
- Double reservation by same member
- Member with unpaid fines trying to borrow

### Concurrency (v3):
- Multiple members trying to borrow last copy
- Concurrent return and reservation fulfillment
- Thread-safe catalog updates

---

## Step 6: Optimization Opportunities

### Data Structures:
| Operation | Naive | Optimized |
|-----------|-------|-----------|
| Search by title | O(n) scan | O(log n) with sorted index |
| Find by ISBN | O(n) search | O(1) with HashMap |
| Available copies | O(copies) scan | O(1) with counter cache |

### Indexing:
- `Map<String, Book>` - ISBN lookup
- `Map<String, List<Book>>` - Author index
- `Map<String, List<Book>>` - Category index
- `Map<String, Member>` - Member lookup

### Caching:
- Cache available copy count per book
- Cache member's borrowed book count

---

## Step 7: Version Progression

### v1-basic
- Core classes with simple implementation
- Linear search
- Basic issue/return
- Single-threaded

### v2-extended
- Fine calculation with strategy
- Reservation system
- Observer for notifications
- Better error handling

### v3-optimized
- Thread-safe with locks
- Concurrent checkout/return
- HashMap indexing for O(1) lookups
- Optimized search with multiple indexes

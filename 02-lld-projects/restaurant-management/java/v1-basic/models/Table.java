import enums.TableStatus;

/**
 * Table.java - Restaurant table.
 */
public class Table {
    private final int tableNumber;
    private final int capacity;
    private TableStatus status;

    public Table(int tableNumber, int capacity) {
        this.tableNumber = tableNumber;
        this.capacity = capacity;
        this.status = TableStatus.AVAILABLE;
    }

    public int getTableNumber() {
        return tableNumber;
    }

    public int getCapacity() {
        return capacity;
    }

    public TableStatus getStatus() {
        return status;
    }

    public void setStatus(TableStatus s) {
        this.status = s;
    }

    @Override
    public String toString() {
        return "Table " + tableNumber + " (capacity: " + capacity + ")";
    }
}

package abstractfactory.v2;

/**
 * v2-variant: Abstract Factory Pattern for Cross-Platform Database Ecosystems.
 * Demonstrates families of related database objects (Connection, Command, Transaction)
 * guaranteed to operate consistently together without mixing dialects.
 */
public class DatabaseFactoryDemo {

    public interface DbConnection {
        void open();
        boolean isOpen();
        String getDialect();
    }

    public interface DbCommand {
        String execute(String sql);
    }

    public interface DbTransaction {
        void begin();
        void commit();
        void rollback();
        boolean isActive();
    }

    public interface DatabaseFactory {
        DbConnection createConnection();
        DbCommand createCommand();
        DbTransaction createTransaction();
    }

    // --- PostgreSQL Family ---

    public static class PostgresConnection implements DbConnection {
        private boolean open = false;

        @Override
        public void open() {
            this.open = true;
        }

        @Override
        public boolean isOpen() {
            return open;
        }

        @Override
        public String getDialect() {
            return "POSTGRESQL";
        }
    }

    public static class PostgresCommand implements DbCommand {
        @Override
        public String execute(String sql) {
            return "[PostgreSQL Executed]: " + sql;
        }
    }

    public static class PostgresTransaction implements DbTransaction {
        private boolean active = false;

        @Override
        public void begin() {
            this.active = true;
        }

        @Override
        public void commit() {
            this.active = false;
        }

        @Override
        public void rollback() {
            this.active = false;
        }

        @Override
        public boolean isActive() {
            return active;
        }
    }

    public static class PostgresFactory implements DatabaseFactory {
        @Override
        public DbConnection createConnection() {
            return new PostgresConnection();
        }

        @Override
        public DbCommand createCommand() {
            return new PostgresCommand();
        }

        @Override
        public DbTransaction createTransaction() {
            return new PostgresTransaction();
        }
    }

    // --- MySQL Family ---

    public static class MySqlConnection implements DbConnection {
        private boolean open = false;

        @Override
        public void open() {
            this.open = true;
        }

        @Override
        public boolean isOpen() {
            return open;
        }

        @Override
        public String getDialect() {
            return "MYSQL";
        }
    }

    public static class MySqlCommand implements DbCommand {
        @Override
        public String execute(String sql) {
            return "[MySQL Executed]: " + sql;
        }
    }

    public static class MySqlTransaction implements DbTransaction {
        private boolean active = false;

        @Override
        public void begin() {
            this.active = true;
        }

        @Override
        public void commit() {
            this.active = false;
        }

        @Override
        public void rollback() {
            this.active = false;
        }

        @Override
        public boolean isActive() {
            return active;
        }
    }

    public static class MySqlFactory implements DatabaseFactory {
        @Override
        public DbConnection createConnection() {
            return new MySqlConnection();
        }

        @Override
        public DbCommand createCommand() {
            return new MySqlCommand();
        }

        @Override
        public DbTransaction createTransaction() {
            return new MySqlTransaction();
        }
    }

    public static void main(String[] args) {
        DatabaseFactory factory = new PostgresFactory();
        DbConnection conn = factory.createConnection();
        conn.open();
        DbTransaction tx = factory.createTransaction();
        tx.begin();
        DbCommand cmd = factory.createCommand();
        System.out.println(cmd.execute("SELECT * FROM metrics WHERE id = 1"));
        tx.commit();
    }
}

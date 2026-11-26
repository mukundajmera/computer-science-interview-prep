package com.sysdesign.databaseisolationlevels;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class MvccTransactionEngineTest {

    private MvccTransactionEngine engine;

    @BeforeEach
    public void setUp() {
        engine = new MvccTransactionEngine();
    }

    @Test
    public void testDirtyReadPrevention() {
        int tx1 = engine.begin(MvccTransactionEngine.IsolationLevel.READ_COMMITTED);
        engine.write(tx1, "k1", "v1");

        int tx2 = engine.begin(MvccTransactionEngine.IsolationLevel.READ_COMMITTED);
        String val = engine.read(tx2, "k1");

        assertNull(val, "Transaction 2 should not read uncommitted writes of Transaction 1");

        engine.commit(tx1);
        String val2 = engine.read(tx2, "k1");
        assertEquals("v1", val2, "Transaction 2 should read committed writes after tx1 commits (READ_COMMITTED)");
    }

    @Test
    public void testRepeatableReadSnapshotIsolation() {
        int tx0 = engine.begin();
        engine.write(tx0, "k1", "v0");
        engine.commit(tx0);

        int tx1 = engine.begin(MvccTransactionEngine.IsolationLevel.SNAPSHOT_ISOLATION);
        String val1 = engine.read(tx1, "k1");
        assertEquals("v0", val1);

        int tx2 = engine.begin(MvccTransactionEngine.IsolationLevel.READ_COMMITTED);
        engine.write(tx2, "k1", "v2");
        engine.commit(tx2);

        String val2 = engine.read(tx1, "k1");
        assertEquals("v0", val2, "Snapshot Isolation should provide repeatable reads");
    }

    @Test
    public void testFirstCommitterWins() {
        int tx0 = engine.begin();
        engine.write(tx0, "k1", "v0");
        engine.commit(tx0);

        int tx1 = engine.begin(MvccTransactionEngine.IsolationLevel.SNAPSHOT_ISOLATION);
        int tx2 = engine.begin(MvccTransactionEngine.IsolationLevel.SNAPSHOT_ISOLATION);

        engine.write(tx1, "k1", "v1");
        engine.write(tx2, "k1", "v2");

        assertTrue(engine.commit(tx1));
        assertFalse(engine.commit(tx2), "Second committer should fail under first-committer-wins rule");

        int tx3 = engine.begin();
        assertEquals("v1", engine.read(tx3, "k1"));
    }

    @Test
    public void testWriteSkewReproduction() {
        int tx0 = engine.begin();
        engine.write(tx0, "doc1", "on_call");
        engine.write(tx0, "doc2", "on_call");
        engine.commit(tx0);

        int tx1 = engine.begin(MvccTransactionEngine.IsolationLevel.SNAPSHOT_ISOLATION);
        int tx2 = engine.begin(MvccTransactionEngine.IsolationLevel.SNAPSHOT_ISOLATION);

        String doc2Status = engine.read(tx1, "doc2");
        if ("on_call".equals(doc2Status)) {
            engine.write(tx1, "doc1", "off_call");
        }

        String doc1Status = engine.read(tx2, "doc1");
        if ("on_call".equals(doc1Status)) {
            engine.write(tx2, "doc2", "off_call");
        }

        assertTrue(engine.commit(tx1));
        assertTrue(engine.commit(tx2));

        int tx3 = engine.begin();
        assertEquals("off_call", engine.read(tx3, "doc1"));
        assertEquals("off_call", engine.read(tx3, "doc2"));
    }
}

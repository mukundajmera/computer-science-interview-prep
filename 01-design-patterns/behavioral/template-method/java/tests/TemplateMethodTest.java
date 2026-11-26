import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

import templatemethod.v2.EtlPipelineDemo.*;
import templatemethod.v3.PaymentTransactionTemplateDemo.*;

public class TemplateMethodTest {

    @Test
    @DisplayName("CSVProcessor executes full template workflow without throwing")
    void testCSVProcessorExecution() {
        DataProcessor processor = new CSVProcessor();
        assertDoesNotThrow(() -> processor.processData());
    }

    @Test
    @DisplayName("JSONProcessor executes full template workflow without throwing")
    void testJSONProcessorExecution() {
        DataProcessor processor = new JSONProcessor();
        assertDoesNotThrow(() -> processor.processData());
    }

    @Test
    @DisplayName("XMLProcessor executes template workflow including custom report")
    void testXMLProcessorExecution() {
        DataProcessor processor = new XMLProcessor();
        assertDoesNotThrow(() -> processor.processData());
    }

    @Test
    @DisplayName("v2 EtlPipeline runs extraction, transformation, validation, and post-execution hooks")
    void testEtlPipelineHooks() {
        EtlPipeline sales = new EcommerceSalesEtl();
        assertTrue(sales.runPipeline("s3://orders", "dw://analytics"));
        assertTrue(sales.getExecutionLog().stream().anyMatch(l -> l.contains("Extracted 3 records")));
        assertTrue(sales.getExecutionLog().stream().anyMatch(l -> l.contains("cleanup hook executed")));

        EtlPipeline failingAudit = new StrictAuditLogEtl(true);
        assertFalse(failingAudit.runPipeline("log://audit", "dw://archive"));
        assertTrue(failingAudit.getExecutionLog().stream().anyMatch(l -> l.contains("Validation failed")));
    }

    @Test
    @DisplayName("v3 PaymentTransactionTemplate enforces invariants and executes compensation on failure")
    void testPaymentTransactionTemplate() {
        PaymentProcessorTemplate card = new CreditCardProcessor();
        TransactionResult res1 = card.processPayment("TXN-101", 100.0, "USD");
        assertTrue(res1.isSuccess());
        assertEquals("Success", res1.getMessage());

        // Fraud check hook catches large amounts
        TransactionResult resFraud = card.processPayment("TXN-102", 50000.0, "USD");
        assertFalse(resFraud.isSuccess());
        assertTrue(resFraud.getAuditLogs().stream().anyMatch(l -> l.contains("Compensation executed")));

        // Debit failure triggers compensation
        PaymentProcessorTemplate cryptoFail = new HighRiskCryptoProcessor(true);
        TransactionResult resDebitFail = cryptoFail.processPayment("TXN-103", 20.0, "BTC");
        assertFalse(resDebitFail.isSuccess());
        assertTrue(resDebitFail.getAuditLogs().stream().anyMatch(l -> l.contains("Compensation executed")));
    }
}

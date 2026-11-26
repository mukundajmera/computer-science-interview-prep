package templatemethod.v2;

import java.util.ArrayList;
import java.util.List;

/**
 * v2-variant: Template Method Pattern for ETL Data Pipelines with Hooks.
 * Encapsulates the immutable step skeleton: Extract -> Transform -> Validate (Hook) -> Load -> Cleanup (Hook).
 */
public class EtlPipelineDemo {

    public abstract static class EtlPipeline {
        private final List<String> executionLog = new ArrayList<>();

        // The Template Method (final to prevent overriding algorithm sequence)
        public final boolean runPipeline(String sourceUri, String destUri) {
            executionLog.clear();
            log("Pipeline started for " + sourceUri);
            
            List<String> rawData = extract(sourceUri);
            log("Extracted " + rawData.size() + " records");

            List<String> transformed = transform(rawData);
            log("Transformed records");

            if (shouldValidate() && !validate(transformed)) {
                log("Validation failed; pipeline aborted");
                onValidationFailure(sourceUri);
                return false;
            }

            load(destUri, transformed);
            log("Loaded records to " + destUri);

            postExecutionHook();
            return true;
        }

        protected abstract List<String> extract(String source);
        protected abstract List<String> transform(List<String> data);
        protected abstract void load(String destination, List<String> data);

        // Hooks with default implementations
        protected boolean shouldValidate() {
            return true;
        }

        protected boolean validate(List<String> data) {
            return data != null && !data.isEmpty();
        }

        protected void onValidationFailure(String source) {
            // default hook: no-op or alert
        }

        protected void postExecutionHook() {
            log("Pipeline finished cleanup hook executed");
        }

        protected void log(String msg) {
            executionLog.add(msg);
        }

        public List<String> getExecutionLog() {
            return new ArrayList<>(executionLog);
        }
    }

    public static class EcommerceSalesEtl extends EtlPipeline {
        @Override
        protected List<String> extract(String source) {
            return List.of("order_1:100", "order_2:250", "order_3:40");
        }

        @Override
        protected List<String> transform(List<String> data) {
            List<String> out = new ArrayList<>();
            for (String item : data) {
                out.add("PROCESSED_" + item.toUpperCase());
            }
            return out;
        }

        @Override
        protected void load(String destination, List<String> data) {
            log("Saved to data-warehouse: " + destination);
        }
    }

    public static class StrictAuditLogEtl extends EtlPipeline {
        private final boolean failValidation;

        public StrictAuditLogEtl(boolean failValidation) {
            this.failValidation = failValidation;
        }

        @Override
        protected List<String> extract(String source) {
            return List.of("log_entry_1", "log_entry_2");
        }

        @Override
        protected List<String> transform(List<String> data) {
            return data;
        }

        @Override
        protected boolean validate(List<String> data) {
            return !failValidation;
        }

        @Override
        protected void load(String destination, List<String> data) {
            log("Audited and stored to " + destination);
        }
    }

    public static void main(String[] args) {
        EtlPipeline salesEtl = new EcommerceSalesEtl();
        boolean ok = salesEtl.runPipeline("s3://sales-bucket/raw", "dw://sales-table");
        System.out.println("Sales ETL Success: " + ok);
    }
}

/**
 * Template Method Pattern - Data Processing
 */

// Abstract Class with Template Method
abstract class DataProcessor {
    // Template Method - defines the algorithm skeleton
    public final void processData() {
        readData();
        parseData();
        analyzeData();
        generateReport();
    }
    
    // Concrete methods
    protected void readData() {
        System.out.println("Reading data from source...");
    }
    
    protected void generateReport() {
        System.out.println("Generating final report");
    }
    
    // Abstract methods - to be implemented by subclasses
    protected abstract void parseData();
    protected abstract void analyzeData();
}

// Concrete Implementations
class CSVProcessor extends DataProcessor {
    @Override
    protected void parseData() {
        System.out.println("Parsing CSV: splitting by commas");
    }
    
    @Override
    protected void analyzeData() {
        System.out.println("Analyzing CSV: calculating statistics");
    }
}

class JSONProcessor extends DataProcessor {
    @Override
    protected void parseData() {
        System.out.println("Parsing JSON: building object tree");
    }
    
    @Override
    protected void analyzeData() {
        System.out.println("Analyzing JSON: traversing nodes");
    }
}

class XMLProcessor extends DataProcessor {
    @Override
    protected void parseData() {
        System.out.println("Parsing XML: building DOM tree");
    }
    
    @Override
    protected void analyzeData() {
        System.out.println("Analyzing XML: XPath queries");
    }
    
    @Override
    protected void generateReport() {
        System.out.println("Generating XML report with XSLT");
    }
}

public class TemplateMethodDemo {
    public static void main(String[] args) {
        System.out.println("=== CSV Processing ===");
        DataProcessor csv = new CSVProcessor();
        csv.processData();
        
        System.out.println("\n=== JSON Processing ===");
        DataProcessor json = new JSONProcessor();
        json.processData();
        
        System.out.println("\n=== XML Processing ===");
        DataProcessor xml = new XMLProcessor();
        xml.processData();
    }
}

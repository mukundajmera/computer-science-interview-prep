/**
 * Decorator Pattern - V2: Data Stream Decorators
 * 
 * Real-world example showing how to add features to data streams
 * like compression, encryption, and logging.
 */

import java.io.*;
import java.util.Base64;
import java.util.zip.*;

// Component Interface
interface DataSource {
    void writeData(String data) throws Exception;
    String readData() throws Exception;
}

// Concrete Component - File Data Source
class FileDataSource implements DataSource {
    private String filename;
    
    public FileDataSource(String filename) {
        this.filename = filename;
    }
    
    @Override
    public void writeData(String data) throws Exception {
        try (FileWriter writer = new FileWriter(filename)) {
            writer.write(data);
        }
    }
    
    @Override
    public String readData() throws Exception {
        try (BufferedReader reader = new BufferedReader(new FileReader(filename))) {
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                sb.append(line);
            }
            return sb.toString();
        }
    }
}

// Abstract Decorator
abstract class DataSourceDecorator implements DataSource {
    protected DataSource wrappee;
    
    public DataSourceDecorator(DataSource source) {
        this.wrappee = source;
    }
    
    @Override
    public void writeData(String data) throws Exception {
        wrappee.writeData(data);
    }
    
    @Override
    public String readData() throws Exception {
        return wrappee.readData();
    }
}

// Concrete Decorator - Encryption
class EncryptionDecorator extends DataSourceDecorator {
    public EncryptionDecorator(DataSource source) {
        super(source);
    }
    
    @Override
    public void writeData(String data) throws Exception {
        String encrypted = encrypt(data);
        super.writeData(encrypted);
    }
    
    @Override
    public String readData() throws Exception {
        String data = super.readData();
        return decrypt(data);
    }
    
    private String encrypt(String data) {
        // Simple Base64 encoding for demo (use real encryption in production!)
        return Base64.getEncoder().encodeToString(data.getBytes());
    }
    
    private String decrypt(String data) {
        return new String(Base64.getDecoder().decode(data));
    }
}

// Concrete Decorator - Compression
class CompressionDecorator extends DataSourceDecorator {
    public CompressionDecorator(DataSource source) {
        super(source);
    }
    
    @Override
    public void writeData(String data) throws Exception {
        String compressed = compress(data);
        super.writeData(compressed);
    }
    
    @Override
    public String readData() throws Exception {
        String data = super.readData();
        return decompress(data);
    }
    
    private String compress(String data) throws Exception {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        try (GZIPOutputStream gzip = new GZIPOutputStream(baos)) {
            gzip.write(data.getBytes());
        }
        return Base64.getEncoder().encodeToString(baos.toByteArray());
    }
    
    private String decompress(String data) throws Exception {
        byte[] bytes = Base64.getDecoder().decode(data);
        ByteArrayInputStream bais = new ByteArrayInputStream(bytes);
        try (GZIPInputStream gzip = new GZIPInputStream(bais);
             ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[256];
            int len;
            while ((len = gzip.read(buffer)) > 0) {
                out.write(buffer, 0, len);
            }
            return out.toString();
        }
    }
}

// Concrete Decorator - Logging
class LoggingDecorator extends DataSourceDecorator {
    public LoggingDecorator(DataSource source) {
        super(source);
    }
    
    @Override
    public void writeData(String data) throws Exception {
        System.out.println("[LOG] Writing data: " + data.length() + " chars");
        super.writeData(data);
        System.out.println("[LOG] Write complete");
    }
    
    @Override
    public String readData() throws Exception {
        System.out.println("[LOG] Reading data...");
        String data = super.readData();
        System.out.println("[LOG] Read complete: " + data.length() + " chars");
        return data;
    }
}

// Demo
public class DataStreamDemo {
    public static void main(String[] args) throws Exception {
        String testData = "Hello, World! This is sensitive data that needs protection.";
        String filename = "test_data.txt";
        
        // Example 1: Plain file storage
        System.out.println("=== Plain File Storage ===");
        DataSource source1 = new FileDataSource(filename);
        source1.writeData(testData);
        System.out.println("Written: " + testData);
        System.out.println("Read: " + source1.readData());
        
        // Example 2: With encryption
        System.out.println("\n=== Encrypted Storage ===");
        DataSource source2 = new EncryptionDecorator(
            new FileDataSource(filename)
        );
        source2.writeData(testData);
        System.out.println("Read (decrypted): " + source2.readData());
        
        // Example 3: With compression + encryption + logging
        System.out.println("\n=== Full Stack: Logging + Compression + Encryption ===");
        DataSource source3 = new LoggingDecorator(
            new CompressionDecorator(
                new EncryptionDecorator(
                    new FileDataSource(filename)
                )
            )
        );
        source3.writeData(testData);
        System.out.println("Read: " + source3.readData());
        
        // Cleanup
        new File(filename).delete();
    }
}

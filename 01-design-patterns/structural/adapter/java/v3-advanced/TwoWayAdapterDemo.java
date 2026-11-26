/**
 * Adapter Pattern - V3 Advanced: Two-Way Adapter
 * 
 * Scenario: Legacy XML-based system needs to work with new JSON-based system.
 * The adapter works in both directions, allowing each system to communicate.
 */

import java.util.*;

// Legacy System - Uses XML format
interface XMLDataSource {
    String fetchAsXML(String query);
    void saveFromXML(String xml);
}

// New System - Uses JSON format  
interface JSONDataSource {
    Map<String, Object> fetchAsJSON(String query);
    void saveFromJSON(Map<String, Object> data);
}

// Concrete Legacy System
class LegacyXMLDatabase implements XMLDataSource {
    private Map<String, String> storage = new HashMap<>();
    
    public LegacyXMLDatabase() {
        // Pre-populate with some data
        storage.put("user_1", "<user><id>1</id><name>Alice</name><email>alice@test.com</email></user>");
        storage.put("user_2", "<user><id>2</id><name>Bob</name><email>bob@test.com</email></user>");
    }
    
    @Override
    public String fetchAsXML(String query) {
        System.out.println("Legacy XML DB: Fetching " + query);
        return storage.getOrDefault(query, "<empty/>");
    }
    
    @Override
    public void saveFromXML(String xml) {
        System.out.println("Legacy XML DB: Saving XML data");
        // Parse and store
        String id = extractValue(xml, "id");
        storage.put("user_" + id, xml);
    }
    
    private String extractValue(String xml, String tag) {
        int start = xml.indexOf("<" + tag + ">") + tag.length() + 2;
        int end = xml.indexOf("</" + tag + ">");
        return xml.substring(start, end);
    }
}

// Concrete New System
class ModernJSONAPI implements JSONDataSource {
    private Map<String, Map<String, Object>> storage = new HashMap<>();
    
    public ModernJSONAPI() {
        // Pre-populate
        storage.put("product_1", Map.of("id", 1, "name", "Laptop", "price", 999.99));
        storage.put("product_2", Map.of("id", 2, "name", "Mouse", "price", 29.99));
    }
    
    @Override
    public Map<String, Object> fetchAsJSON(String query) {
        System.out.println("Modern JSON API: Fetching " + query);
        return storage.getOrDefault(query, Map.of());
    }
    
    @Override
    public void saveFromJSON(Map<String, Object> data) {
        System.out.println("Modern JSON API: Saving JSON data");
        String id = "item_" + data.get("id");
        storage.put(id, data);
    }
}

// Two-Way Adapter - Implements BOTH interfaces
class TwoWayDataAdapter implements XMLDataSource, JSONDataSource {
    private XMLDataSource xmlSource;
    private JSONDataSource jsonSource;
    
    public TwoWayDataAdapter(XMLDataSource xmlSource) {
        this.xmlSource = xmlSource;
    }
    
    public TwoWayDataAdapter(JSONDataSource jsonSource) {
        this.jsonSource = jsonSource;
    }
    
    public TwoWayDataAdapter(XMLDataSource xmlSource, JSONDataSource jsonSource) {
        this.xmlSource = xmlSource;
        this.jsonSource = jsonSource;
    }
    
    // XMLDataSource implementation - Adapts JSON to XML
    @Override
    public String fetchAsXML(String query) {
        if (xmlSource != null) {
            return xmlSource.fetchAsXML(query);
        }
        // Convert JSON to XML
        Map<String, Object> json = jsonSource.fetchAsJSON(query);
        return jsonToXml(json);
    }
    
    @Override
    public void saveFromXML(String xml) {
        if (xmlSource != null) {
            xmlSource.saveFromXML(xml);
            return;
        }
        // Convert XML to JSON and save
        Map<String, Object> json = xmlToJson(xml);
        jsonSource.saveFromJSON(json);
    }
    
    // JSONDataSource implementation - Adapts XML to JSON
    @Override
    public Map<String, Object> fetchAsJSON(String query) {
        if (jsonSource != null) {
            return jsonSource.fetchAsJSON(query);
        }
        // Convert XML to JSON
        String xml = xmlSource.fetchAsXML(query);
        return xmlToJson(xml);
    }
    
    @Override
    public void saveFromJSON(Map<String, Object> data) {
        if (jsonSource != null) {
            jsonSource.saveFromJSON(data);
            return;
        }
        // Convert JSON to XML and save
        String xml = jsonToXml(data);
        xmlSource.saveFromXML(xml);
    }
    
    // Conversion utilities
    private String jsonToXml(Map<String, Object> json) {
        if (json.isEmpty()) return "<empty/>";
        
        StringBuilder xml = new StringBuilder("<item>");
        for (Map.Entry<String, Object> entry : json.entrySet()) {
            xml.append("<").append(entry.getKey()).append(">")
               .append(entry.getValue())
               .append("</").append(entry.getKey()).append(">");
        }
        xml.append("</item>");
        return xml.toString();
    }
    
    private Map<String, Object> xmlToJson(String xml) {
        if (xml.equals("<empty/>")) return Map.of();
        
        Map<String, Object> result = new HashMap<>();
        // Simple XML parsing (production would use proper parser)
        String[] tags = {"id", "name", "email", "price"};
        for (String tag : tags) {
            String startTag = "<" + tag + ">";
            String endTag = "</" + tag + ">";
            int start = xml.indexOf(startTag);
            if (start != -1) {
                start += startTag.length();
                int end = xml.indexOf(endTag);
                String value = xml.substring(start, end);
                // Try to parse as number
                try {
                    if (value.contains(".")) {
                        result.put(tag, Double.parseDouble(value));
                    } else {
                        result.put(tag, Integer.parseInt(value));
                    }
                } catch (NumberFormatException e) {
                    result.put(tag, value);
                }
            }
        }
        return result;
    }
}

// Demo
public class TwoWayAdapterDemo {
    public static void main(String[] args) {
        // Legacy XML system
        LegacyXMLDatabase legacyDb = new LegacyXMLDatabase();
        
        // Modern JSON system
        ModernJSONAPI modernApi = new ModernJSONAPI();
        
        // Two-way adapter for both
        TwoWayDataAdapter adapter = new TwoWayDataAdapter(legacyDb, modernApi);
        
        System.out.println("=== JSON client reading from Legacy XML system ===");
        Map<String, Object> userAsJson = adapter.fetchAsJSON("user_1");
        System.out.println("Got JSON: " + userAsJson);
        
        System.out.println("\n=== XML client reading from Modern JSON system ===");
        String productAsXml = adapter.fetchAsXML("product_1");
        System.out.println("Got XML: " + productAsXml);
        
        System.out.println("\n=== JSON client saving to Legacy XML system ===");
        TwoWayDataAdapter xmlOnlyAdapter = new TwoWayDataAdapter(legacyDb);
        xmlOnlyAdapter.saveFromJSON(Map.of("id", 3, "name", "Charlie", "email", "charlie@test.com"));
        
        // Verify save
        String saved = legacyDb.fetchAsXML("user_3");
        System.out.println("Saved as XML: " + saved);
        
        System.out.println("\n=== XML client saving to Modern JSON system ===");
        TwoWayDataAdapter jsonOnlyAdapter = new TwoWayDataAdapter(modernApi);
        jsonOnlyAdapter.saveFromXML("<item><id>3</id><name>Keyboard</name><price>79.99</price></item>");
        
        // Verify save
        Map<String, Object> savedProduct = modernApi.fetchAsJSON("item_3");
        System.out.println("Saved as JSON: " + savedProduct);
    }
}

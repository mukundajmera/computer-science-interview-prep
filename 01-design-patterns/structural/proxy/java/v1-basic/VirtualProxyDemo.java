/**
 * Proxy Pattern - V1 Basic: Virtual Proxy for Images
 * 
 * Demonstrates lazy loading of expensive resources.
 */

// Subject Interface
interface Image {
    void display();
    int getWidth();
    int getHeight();
}

// Real Subject - Expensive to create
class RealImage implements Image {
    private String filename;
    private int width;
    private int height;
    
    public RealImage(String filename) {
        this.filename = filename;
        loadFromDisk();
    }
    
    private void loadFromDisk() {
        System.out.println("Loading image from disk: " + filename);
        // Simulate expensive loading
        try { Thread.sleep(1000); } catch (Exception e) {}
        this.width = 1920;
        this.height = 1080;
        System.out.println("Image loaded: " + width + "x" + height);
    }
    
    @Override
    public void display() {
        System.out.println("Displaying image: " + filename);
    }
    
    @Override public int getWidth() { return width; }
    @Override public int getHeight() { return height; }
}

// Virtual Proxy - Lazy loading
class ProxyImage implements Image {
    private RealImage realImage;
    private String filename;
    
    public ProxyImage(String filename) {
        this.filename = filename;
    }
    
    @Override
    public void display() {
        if (realImage == null) {
            realImage = new RealImage(filename);  // Lazy load
        }
        realImage.display();
    }
    
    @Override
    public int getWidth() {
        if (realImage == null) {
            realImage = new RealImage(filename);
        }
        return realImage.getWidth();
    }
    
    @Override
    public int getHeight() {
        if (realImage == null) {
            realImage = new RealImage(filename);
        }
        return realImage.getHeight();
    }
}

// Demo
public class VirtualProxyDemo {
    public static void main(String[] args) {
        System.out.println("=== Creating proxy images (no loading yet) ===");
        Image image1 = new ProxyImage("photo1.jpg");
        Image image2 = new ProxyImage("photo2.jpg");
        Image image3 = new ProxyImage("photo3.jpg");
        System.out.println("Proxies created.");
        
        System.out.println("\n=== Displaying image1 (loads now) ===");
        image1.display();
        
        System.out.println("\n=== Displaying image1 again (already loaded) ===");
        image1.display();
        
        System.out.println("\n=== Image2 and Image3 never loaded ===");
        // image2 and image3 never accessed, never loaded
    }
}

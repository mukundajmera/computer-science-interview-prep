/**
 * Flyweight Pattern - V3 Advanced: Icon System
 *
 * Shares expensive icon asset data while each toolbar button keeps its own
 * position, size, tint, and enabled state.
 */

import java.util.*;

// Flyweight - shared intrinsic icon resource
class IconAsset {
    private final String name;
    private final String vectorPath;
    
    public IconAsset(String name, String vectorPath) {
        this.name = name;
        this.vectorPath = vectorPath;
    }
    
    public String draw(int x, int y, int size, String tint, boolean enabled) {
        return String.format(
            "%s at (%d,%d), size=%d, tint=%s, enabled=%s",
            name, x, y, size, tint, enabled
        );
    }
    
    public String getVectorPath() {
        return vectorPath;
    }
}

// Flyweight Factory
class IconAssetFactory {
    private static final Map<String, String> KNOWN_PATHS = new HashMap<>();
    private static final Map<String, IconAsset> assets = new HashMap<>();
    
    static {
        KNOWN_PATHS.put("save", "M4,4 L20,4 L20,20 L4,20 Z");
        KNOWN_PATHS.put("search", "M10,4 A6,6 0 1,0 10,16 L18,24");
        KNOWN_PATHS.put("settings", "M12,2 L15,8 L22,9 L17,14 L18,21 L12,18 L6,21 L7,14 L2,9 L9,8 Z");
    }
    
    public static IconAsset getAsset(String name) {
        if (!assets.containsKey(name)) {
            String vectorPath = KNOWN_PATHS.getOrDefault(name, "M0,0 L1,1");
            assets.put(name, new IconAsset(name, vectorPath));
        }
        return assets.get(name);
    }
    
    public static int getAssetCount() {
        return assets.size();
    }
    
    public static void reset() {
        assets.clear();
    }
}

// Context - extrinsic button data
class IconButton {
    private final IconAsset asset;
    private final int x;
    private final int y;
    private final int size;
    private final String tint;
    private final boolean enabled;
    
    public IconButton(IconAsset asset, int x, int y, int size, String tint, boolean enabled) {
        this.asset = asset;
        this.x = x;
        this.y = y;
        this.size = size;
        this.tint = tint;
        this.enabled = enabled;
    }
    
    public String render() {
        return asset.draw(x, y, size, tint, enabled);
    }
}

// Client toolbar
class Toolbar {
    private final List<IconButton> buttons = new ArrayList<>();
    
    public void addButton(String name, int x, int y, int size, String tint, boolean enabled) {
        IconAsset asset = IconAssetFactory.getAsset(name);
        buttons.add(new IconButton(asset, x, y, size, tint, enabled));
    }
    
    public List<String> render() {
        List<String> rendered = new ArrayList<>();
        for (IconButton button : buttons) {
            rendered.add(button.render());
        }
        return rendered;
    }
    
    public int getButtonCount() {
        return buttons.size();
    }
    
    public int getAssetCount() {
        return IconAssetFactory.getAssetCount();
    }
}

public class IconSystemDemo {
    public static void main(String[] args) {
        IconAssetFactory.reset();
        Toolbar toolbar = new Toolbar();
        toolbar.addButton("save", 0, 0, 24, "blue", true);
        toolbar.addButton("save", 32, 0, 32, "gray", false);
        toolbar.addButton("search", 64, 0, 24, "blue", true);
        
        for (String command : toolbar.render()) {
            System.out.println(command);
        }
        System.out.println("Buttons: " + toolbar.getButtonCount());
        System.out.println("Loaded assets: " + toolbar.getAssetCount());
    }
}

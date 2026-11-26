/**
 * Flyweight Pattern - V2 Variant: Text Editor
 *
 * Shares immutable character styles across many glyph occurrences.
 */

import java.util.*;

// Flyweight - shared intrinsic text style
class CharacterStyle {
    private final String fontFamily;
    private final int fontSize;
    private final String color;
    
    public CharacterStyle(String fontFamily, int fontSize, String color) {
        this.fontFamily = fontFamily;
        this.fontSize = fontSize;
        this.color = color;
    }
    
    public String render(char character, int x, int y) {
        return String.format(
            "%c@(%d,%d)[%s/%d/%s]",
            character, x, y, fontFamily, fontSize, color
        );
    }
}

// Flyweight Factory
class CharacterStyleFactory {
    private static final Map<String, CharacterStyle> styles = new HashMap<>();
    
    public static CharacterStyle getStyle(String fontFamily, int fontSize, String color) {
        String key = fontFamily + ":" + fontSize + ":" + color;
        if (!styles.containsKey(key)) {
            styles.put(key, new CharacterStyle(fontFamily, fontSize, color));
        }
        return styles.get(key);
    }
    
    public static int getStyleCount() {
        return styles.size();
    }
    
    public static void reset() {
        styles.clear();
    }
}

// Context - extrinsic glyph data
class Glyph {
    private final char character;
    private final int x;
    private final int y;
    private final CharacterStyle style;
    
    public Glyph(char character, int x, int y, CharacterStyle style) {
        this.character = character;
        this.x = x;
        this.y = y;
        this.style = style;
    }
    
    public int getY() {
        return y;
    }
    
    public String render() {
        return style.render(character, x, y);
    }
}

// Client document
class TextDocument {
    private final List<Glyph> glyphs = new ArrayList<>();
    private int cursorX = 0;
    private int cursorY = 0;
    
    public void append(String text, String fontFamily, int fontSize, String color) {
        CharacterStyle style = CharacterStyleFactory.getStyle(fontFamily, fontSize, color);
        for (char character : text.toCharArray()) {
            glyphs.add(new Glyph(character, cursorX, cursorY, style));
            cursorX++;
        }
    }
    
    public void newLine() {
        cursorX = 0;
        cursorY++;
    }
    
    public String renderLine(int lineNumber) {
        List<String> rendered = new ArrayList<>();
        for (Glyph glyph : glyphs) {
            if (glyph.getY() == lineNumber) {
                rendered.add(glyph.render());
            }
        }
        return String.join(" ", rendered);
    }
    
    public int getGlyphCount() {
        return glyphs.size();
    }
    
    public int getStyleCount() {
        return CharacterStyleFactory.getStyleCount();
    }
}

public class TextEditorFlyweightDemo {
    public static void main(String[] args) {
        CharacterStyleFactory.reset();
        TextDocument document = new TextDocument();
        document.append("Fly", "Inter", 14, "black");
        document.append("weight", "Inter", 14, "black");
        document.append("!", "Inter", 18, "red");
        
        System.out.println(document.renderLine(0));
        System.out.println("Glyphs: " + document.getGlyphCount());
        System.out.println("Shared styles: " + document.getStyleCount());
    }
}

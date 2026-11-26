public class Player {
    private final String name;
    private final DiscColor color;

    public Player(String name, DiscColor color) {
        if (color == null || color == DiscColor.EMPTY) {
            throw new IllegalArgumentException("Player color must be RED or YELLOW");
        }
        this.name = name;
        this.color = color;
    }

    public String getName() {
        return name;
    }

    public DiscColor getColor() {
        return color;
    }
}

import java.util.Scanner;

/**
 * Human player that gets moves from console input.
 */
public class HumanPlayer extends Player {
    private final Scanner scanner;

    public HumanPlayer(String name, Mark mark) {
        super(name, mark);
        this.scanner = new Scanner(System.in);
    }

    public HumanPlayer(String name, Mark mark, Scanner scanner) {
        super(name, mark);
        this.scanner = scanner;
    }

    @Override
    public Position makeMove(Board board) {
        int size = board.getSize();
        int maxPos = size * size;
        
        while (true) {
            System.out.print(getName() + " (" + getMark() + "), enter position (1-" + maxPos + "): ");
            
            try {
                String input = scanner.nextLine().trim();
                int pos = Integer.parseInt(input);
                
                if (pos < 1 || pos > maxPos) {
                    System.out.println("Invalid position! Enter a number between 1 and " + maxPos);
                    continue;
                }
                
                // Convert 1-indexed position to row, col
                int row = (pos - 1) / size;
                int col = (pos - 1) % size;
                Position position = new Position(row, col);
                
                if (!board.isEmpty(position)) {
                    System.out.println("That cell is already occupied! Try again.");
                    continue;
                }
                
                return position;
            } catch (NumberFormatException e) {
                System.out.println("Invalid input! Please enter a number.");
            }
        }
    }
}

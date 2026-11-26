/**
 * Snake and Ladder Game - V1 Basic Demo
 */
public class SnakeAndLadderDemoV1 {
    
    public static void main(String[] args) {
        System.out.println("==========================================");
        System.out.println("   Snake and Ladder Game - V1 Basic Demo");
        System.out.println("==========================================\n");
        
        // Create game with standard board
        Game game = new Game();
        
        // Display board configuration
        game.getBoard().displayBoard();
        
        // Add players
        game.addPlayer("Alice");
        game.addPlayer("Bob");
        game.addPlayer("Charlie");
        
        // Play the game
        System.out.println("\n--- Starting Game ---");
        Player winner = game.playGame();
        
        // Final status
        game.displayStatus();
        
        System.out.println("\n--- Demo Complete ---");
    }
}

/**
 * Snake and Ladder GameV2 - V1 Basic Demo
 */
public class SnakeAndLadderDemoV2 {
    
    public static void main(String[] args) {
        System.out.println("==========================================");
        System.out.println("   Snake and Ladder GameV2 - V1 Basic Demo");
        System.out.println("==========================================\n");
        
        // Create game with standard board
        GameV2 game = new GameV2();
        
        // Display board configuration
        game.getBoard().displayBoard();
        
        // Add players
        game.addPlayer("Alice");
        game.addPlayer("Bob");
        game.addPlayer("Charlie");
        
        // Play the game
        System.out.println("\n--- Starting GameV2 ---");
        PlayerV2 winner = game.playGame();
        
        // Final status
        game.displayStatus();
        
        System.out.println("\n--- Demo Complete ---");
    }
}

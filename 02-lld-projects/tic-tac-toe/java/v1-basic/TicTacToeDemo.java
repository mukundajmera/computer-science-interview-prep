/**
 * Demo for Tic-Tac-Toe v1 Basic.
 */
public class TicTacToeDemo {
    
    public static void main(String[] args) {
        System.out.println("============================================");
        System.out.println("       TIC-TAC-TOE - v1 Basic");
        System.out.println("============================================");
        
        // Create players
        Player player1 = new HumanPlayer("Player 1", Mark.X);
        Player player2 = new HumanPlayer("Player 2", Mark.O);
        
        // Create and play game
        Game game = new Game(player1, player2);
        game.play();
        
        System.out.println("\nThanks for playing!");
    }
}

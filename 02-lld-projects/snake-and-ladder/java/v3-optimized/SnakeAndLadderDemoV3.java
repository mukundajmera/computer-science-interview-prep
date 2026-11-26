/**
 * Snake and Ladder Game - V3 Optimized Demo
 */
public class SnakeAndLadderDemoV3 {
    
    public static void main(String[] args) {
        System.out.println("==========================================");
        System.out.println("   Snake and Ladder Game - V3 Optimized Demo");
        System.out.println("==========================================\n");
        
        BoardV3 board = BoardV3.createStandardBoard();
        
        System.out.println("--- Standard Game Play ---");
        GameV3 game = new GameV3(board);
        game.addPlayer("Alice");
        game.addPlayer("Bob");
        game.playGame();
        
        System.out.println("\n--- Monte Carlo Simulation ---");
        // Run 10,000 simulations
        MonteCarloSimulation simulation = new MonteCarloSimulation(board, 10000);
        simulation.runSimulation(2);
        
        System.out.println("\n--- Demo Complete ---");
    }
}

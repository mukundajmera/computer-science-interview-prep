import java.util.*;

/**
 * Monte Carlo Simulation Engine to compute win-rate probabilities
 */
public class MonteCarloSimulation {
    private final BoardV3 board;
    private final int numSimulations;

    public MonteCarloSimulation(BoardV3 board, int numSimulations) {
        this.board = board;
        this.numSimulations = numSimulations;
    }

    public void runSimulation(int numPlayers) {
        System.out.println("Running Monte Carlo Simulation...");
        System.out.println("Simulations: " + numSimulations);
        System.out.println("Players: " + numPlayers);

        int[] wins = new int[numPlayers];
        long totalTurns = 0;

        for (int i = 0; i < numSimulations; i++) {
            GameV3 game = new GameV3(board);
            game.setQuietMode(true);
            for (int p = 0; p < numPlayers; p++) {
                game.addPlayer("P" + (p + 1));
            }
            game.setQuietMode(true);
            game.startGame();

            int turns = 0;
            while (!game.isGameOver()) {
                game.playTurn(true); // we need to add this method or suppress output
                turns++;
            }
            
            PlayerV3 winner = game.getWinner();
            if (winner != null) {
                // Determine player index
                int playerIndex = Integer.parseInt(winner.getName().substring(1)) - 1;
                wins[playerIndex]++;
            }
            totalTurns += turns;
        }

        System.out.println("\n--- Simulation Results ---");
        for (int p = 0; p < numPlayers; p++) {
            double winRate = (wins[p] * 100.0) / numSimulations;
            System.out.printf("Player %d Win Rate: %.2f%%\n", (p + 1), winRate);
        }
        System.out.printf("Average turns per game: %.2f\n", (double) totalTurns / numSimulations);
    }
}

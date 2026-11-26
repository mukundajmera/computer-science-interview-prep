"""
Tests for Snake and Ladder Game
"""
import unittest
import sys
import os
import threading
import importlib.util

def load_module(version_dir, module_name):
    base_path = os.path.join(os.path.dirname(__file__), '..', version_dir)
    file_path = os.path.join(base_path, f'{module_name}.py')
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    
    # Store old sys.modules to prevent pollution across versions
    old_mod = sys.modules.get(module_name)
    sys.modules[module_name] = module
    
    # Temporary prepend path to allow intra-module imports for this specific version
    sys.path.insert(0, base_path)
    
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
        if old_mod is not None:
            sys.modules[module_name] = old_mod
        else:
            del sys.modules[module_name]
            
    return module

class TestV1BasicSnakeAndLadder(unittest.TestCase):
    """Tests for V1 Basic Snake and Ladder"""
    
    def test_dice_roll_range(self):
        """Dice should roll within valid range"""
        mod = load_module('v1-basic', 'game_entities')
        dice = mod.Dice()
        for _ in range(100):
            roll = dice.roll()
            self.assertTrue(1 <= roll <= 6)
    
    def test_player_creation(self):
        """Player should be created with valid data"""
        mod = load_module('v1-basic', 'game_entities')
        player = mod.Player("P1", "Alice")
        self.assertEqual(player.id, "P1")
        self.assertEqual(player.name, "Alice")
        self.assertEqual(player.position, 0)
    
    def test_player_movement(self):
        """Player movement should work"""
        mod = load_module('v1-basic', 'game_entities')
        player = mod.Player("P1", "Alice")
        player.move_to(10)
        self.assertEqual(player.position, 10)
    
    def test_snake_creation(self):
        """Snake should be created with valid positions"""
        mod = load_module('v1-basic', 'game_entities')
        snake = mod.Snake(16, 6)
        self.assertEqual(snake.head, 16)
        self.assertEqual(snake.tail, 6)
    
    def test_snake_invalid_positions(self):
        """Snake should reject invalid positions"""
        mod = load_module('v1-basic', 'game_entities')
        with self.assertRaises(ValueError):
            mod.Snake(6, 16)
    
    def test_ladder_creation(self):
        """Ladder should be created with valid positions"""
        mod = load_module('v1-basic', 'game_entities')
        ladder = mod.Ladder(4, 14)
        self.assertEqual(ladder.bottom, 4)
        self.assertEqual(ladder.top, 14)
    
    def test_board_next_position(self):
        """Board should calculate next position correctly"""
        mod = load_module('v1-basic', 'board')
        board = mod.Board(100)
        self.assertEqual(board.get_next_position(0, 5), 5)
        self.assertEqual(board.get_next_position(10, 5), 15)
    
    def test_board_snake_effect(self):
        """Board should apply snake effect"""
        mod = load_module('v1-basic', 'board')
        board = mod.Board(100)
        board.add_snake(16, 6)
        self.assertEqual(board.get_next_position(10, 6), 6)
    
    def test_board_ladder_effect(self):
        """Board should apply ladder effect"""
        mod = load_module('v1-basic', 'board')
        board = mod.Board(100)
        board.add_ladder(4, 14)
        self.assertEqual(board.get_next_position(0, 4), 14)
    
    def test_board_beyond_size(self):
        """Board should prevent move beyond size"""
        mod = load_module('v1-basic', 'board')
        board = mod.Board(100)
        self.assertEqual(board.get_next_position(98, 5), 98)
    
    def test_game_minimum_players(self):
        """Game should require minimum 2 players"""
        mod = load_module('v1-basic', 'game')
        game = mod.Game()
        game.add_player("Alice")
        with self.assertRaises(RuntimeError):
            game.start_game()
    
    def test_game_adds_players(self):
        """Game should add players correctly"""
        mod = load_module('v1-basic', 'game')
        game = mod.Game()
        game.add_player("Alice")
        game.add_player("Bob")
        self.assertEqual(len(game.players), 2)


class TestV2ExtendedSnakeAndLadder(unittest.TestCase):
    """Tests for V2 Extended Snake and Ladder (Strategy Pattern)"""
    
    def test_strategy_pattern_snake(self):
        """Test snake effect strategy directly"""
        mod = load_module('v2-extended', 'game_entities')
        strategy = mod.SnakeEffectStrategy(20, 10)
        self.assertEqual(strategy.apply_effect(20), 10)
        self.assertEqual(strategy.apply_effect(15), 15)  # No effect if not head
        
    def test_strategy_pattern_ladder(self):
        """Test ladder effect strategy directly"""
        mod = load_module('v2-extended', 'game_entities')
        strategy = mod.LadderEffectStrategy(10, 20)
        self.assertEqual(strategy.apply_effect(10), 20)
        self.assertEqual(strategy.apply_effect(15), 15)  # No effect if not bottom
        
    def test_board_with_strategies(self):
        """Test board uses strategies correctly"""
        # Load game_entities for v2 before loading board for v2
        ge_mod = load_module('v2-extended', 'game_entities')
        old_ge = sys.modules.get('game_entities')
        sys.modules['game_entities'] = ge_mod
        
        try:
            board_mod = load_module('v2-extended', 'board')
            board = board_mod.Board(100)
            board.add_snake(16, 6)
            board.add_ladder(4, 14)
            
            self.assertEqual(board.get_next_position(10, 6), 6)  # Snake
            self.assertEqual(board.get_next_position(0, 4), 14)  # Ladder
        finally:
            if old_ge is not None:
                sys.modules['game_entities'] = old_ge
            else:
                del sys.modules['game_entities']


class TestV3ConcurrentSnakeAndLadder(unittest.TestCase):
    """Tests for V3 Concurrent Snake and Ladder"""
    
    def test_concurrent_games(self):
        """Multiple games should run concurrently"""
        # For V3 tests to work nicely without cross contamination we need to do the full dance
        base_path = os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')
        sys.path.insert(0, base_path)
        
        try:
            if 'game_entities' in sys.modules: del sys.modules['game_entities']
            if 'board' in sys.modules: del sys.modules['board']
            if 'game' in sys.modules: del sys.modules['game']
            
            import game as gmod
            Game = gmod.Game
            
            winners = []
            lock = threading.Lock()
            
            def play_game(game_num):
                g = Game()
                g.add_player(f"Player{game_num}A")
                g.add_player(f"Player{game_num}B")
                winner = g.play_game()
                with lock:
                    winners.append(winner)
            
            threads = []
            for i in range(3):
                t = threading.Thread(target=play_game, args=(i,))
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join()
            
            # All games should have completed
            self.assertEqual(len(winners), 3)
        finally:
            sys.path.pop(0)


if __name__ == "__main__":
    unittest.main()

class TestV3OptimizedSnakeAndLadder(unittest.TestCase):
    """Tests for V3 Optimized Snake and Ladder with Turn Timeout"""
    
    def test_turn_timeout_rule(self):
        """Player should lose turn if they exceed timeout"""
        base_path = os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')
        sys.path.insert(0, base_path)
        
        try:
            if 'game_entities' in sys.modules: del sys.modules['game_entities']
            if 'board' in sys.modules: del sys.modules['board']
            if 'game' in sys.modules: del sys.modules['game']
            
            import game as gmod
            Game = gmod.Game
            
            # Use small timeout for test
            game = Game(turn_timeout_seconds=0.1)
            game.add_player("Alice")
            game.add_player("Bob")
            game.start_game()
            
            self.assertEqual(game.current_player.name, "Alice")
            
            # Bob plays with delay > 0.1
            game.play_turn(delay=0.15)
            
            # Alice's turn was skipped due to timeout
            self.assertEqual(game.current_player.name, "Bob")
            self.assertEqual(game.players[0].position, 0) # Alice didn't move
            
            # Bob plays normally
            game.play_turn()
            self.assertEqual(game.current_player.name, "Alice")
            self.assertGreater(game.players[1].position, 0) # Bob moved
            
        finally:
            sys.path.pop(0)


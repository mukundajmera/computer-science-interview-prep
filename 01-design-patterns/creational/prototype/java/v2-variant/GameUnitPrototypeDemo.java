package prototype.v2;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * v2-variant: Game Unit Prototype with Deep Copy and Registry Spawner.
 * Demonstrates cloning complex objects containing mutable nested state
 * (stats, inventory, abilities) to avoid costly re-initialization during spawning.
 */
public class GameUnitPrototypeDemo {

    public interface GameUnit extends Cloneable {
        GameUnit cloneUnit();
        String getName();
        int getHealth();
        void takeDamage(int amount);
        List<String> getAbilities();
        void addAbility(String ability);
    }

    public static class Warrior implements GameUnit {
        private final String name;
        private int health;
        private final List<String> abilities;

        public Warrior(String name, int health, List<String> abilities) {
            this.name = name;
            this.health = health;
            this.abilities = new ArrayList<>(abilities);
        }

        @Override
        public GameUnit cloneUnit() {
            // Deep copy of mutable abilities list
            return new Warrior(this.name, this.health, new ArrayList<>(this.abilities));
        }

        @Override
        public String getName() {
            return name;
        }

        @Override
        public int getHealth() {
            return health;
        }

        @Override
        public void takeDamage(int amount) {
            this.health = Math.max(0, this.health - amount);
        }

        @Override
        public List<String> getAbilities() {
            return abilities;
        }

        @Override
        public void addAbility(String ability) {
            this.abilities.add(ability);
        }
    }

    public static class Mage implements GameUnit {
        private final String name;
        private int health;
        private final List<String> abilities;

        public Mage(String name, int health, List<String> abilities) {
            this.name = name;
            this.health = health;
            this.abilities = new ArrayList<>(abilities);
        }

        @Override
        public GameUnit cloneUnit() {
            return new Mage(this.name, this.health, new ArrayList<>(this.abilities));
        }

        @Override
        public String getName() {
            return name;
        }

        @Override
        public int getHealth() {
            return health;
        }

        @Override
        public void takeDamage(int amount) {
            this.health = Math.max(0, this.health - amount);
        }

        @Override
        public List<String> getAbilities() {
            return abilities;
        }

        @Override
        public void addAbility(String ability) {
            this.abilities.add(ability);
        }
    }

    public static class UnitSpawnerRegistry {
        private final Map<String, GameUnit> prototypes = new HashMap<>();

        public void registerPrototype(String key, GameUnit unit) {
            prototypes.put(key, unit);
        }

        public GameUnit spawn(String key) {
            GameUnit prototype = prototypes.get(key);
            if (prototype == null) {
                throw new IllegalArgumentException("Unknown unit prototype: " + key);
            }
            return prototype.cloneUnit();
        }

        public boolean hasPrototype(String key) {
            return prototypes.containsKey(key);
        }
    }

    public static void main(String[] args) {
        UnitSpawnerRegistry registry = new UnitSpawnerRegistry();
        registry.registerPrototype("elite_warrior", new Warrior("Berserker", 150, List.of("Slash", "Whirlwind")));
        registry.registerPrototype("frost_mage", new Mage("Archmage", 80, List.of("Blizzard", "IceArmor")));

        GameUnit unit1 = registry.spawn("elite_warrior");
        unit1.takeDamage(30);
        System.out.println("Spawned " + unit1.getName() + " with HP: " + unit1.getHealth());
    }
}

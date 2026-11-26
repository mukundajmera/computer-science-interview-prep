/**
 * Facade Pattern - V1 Basic: Home Theater System
 */

// Complex Subsystem Classes
class DVDPlayer {
    public void on() { System.out.println("DVD Player on"); }
    public void play(String movie) { System.out.println("Playing: " + movie); }
    public void stop() { System.out.println("DVD stopped"); }
    public void off() { System.out.println("DVD Player off"); }
}

class Projector {
    public void on() { System.out.println("Projector on"); }
    public void wideScreenMode() { System.out.println("Widescreen mode"); }
    public void off() { System.out.println("Projector off"); }
}

class SoundSystem {
    public void on() { System.out.println("Sound system on"); }
    public void setVolume(int level) { System.out.println("Volume: " + level); }
    public void setSurroundSound() { System.out.println("Surround sound on"); }
    public void off() { System.out.println("Sound system off"); }
}

class Lights {
    public void dim(int level) { System.out.println("Lights dimmed to " + level + "%"); }
    public void on() { System.out.println("Lights on"); }
}

// Facade
class HomeTheaterFacade {
    private DVDPlayer dvd;
    private Projector projector;
    private SoundSystem sound;
    private Lights lights;
    
    public HomeTheaterFacade(DVDPlayer dvd, Projector projector, 
                             SoundSystem sound, Lights lights) {
        this.dvd = dvd;
        this.projector = projector;
        this.sound = sound;
        this.lights = lights;
    }
    
    public void watchMovie(String movie) {
        System.out.println("=== Starting movie: " + movie + " ===");
        lights.dim(10);
        projector.on();
        projector.wideScreenMode();
        sound.on();
        sound.setSurroundSound();
        sound.setVolume(50);
        dvd.on();
        dvd.play(movie);
    }
    
    public void endMovie() {
        System.out.println("=== Shutting down ===");
        dvd.stop();
        dvd.off();
        sound.off();
        projector.off();
        lights.on();
    }
}

public class HomeTheaterDemo {
    public static void main(String[] args) {
        HomeTheaterFacade theater = new HomeTheaterFacade(
            new DVDPlayer(), new Projector(), new SoundSystem(), new Lights()
        );
        
        theater.watchMovie("Inception");
        System.out.println();
        theater.endMovie();
    }
}

/**
 * Adapter Pattern - V1 Basic: Media Player Adapter
 * 
 * Scenario: Our application expects MediaPlayer interface, but we have
 * third-party VLCPlayer and MP4Player with different interfaces.
 */

// Target Interface - What our application expects
interface MediaPlayer {
    void play(String filename);
    void stop();
    String getPlayerType();
}

// Adaptee 1 - Third-party VLC player with incompatible interface
class VLCPlayer {
    public void playVLC(String file) {
        System.out.println("VLC: Playing " + file);
    }
    
    public void stopVLC() {
        System.out.println("VLC: Stopped");
    }
}

// Adaptee 2 - Another third-party player with different interface
class MP4Player {
    public void loadMP4(String filename) {
        System.out.println("MP4: Loading " + filename);
    }
    
    public void startPlayback() {
        System.out.println("MP4: Playback started");
    }
    
    public void endPlayback() {
        System.out.println("MP4: Playback ended");
    }
}

// Adapter for VLC Player - Uses composition (Object Adapter)
class VLCPlayerAdapter implements MediaPlayer {
    private final VLCPlayer vlcPlayer;
    
    public VLCPlayerAdapter() {
        this.vlcPlayer = new VLCPlayer();
    }
    
    public VLCPlayerAdapter(VLCPlayer vlcPlayer) {
        this.vlcPlayer = vlcPlayer;
    }
    
    @Override
    public void play(String filename) {
        vlcPlayer.playVLC(filename);
    }
    
    @Override
    public void stop() {
        vlcPlayer.stopVLC();
    }
    
    @Override
    public String getPlayerType() {
        return "VLC";
    }
}

// Adapter for MP4 Player
class MP4PlayerAdapter implements MediaPlayer {
    private final MP4Player mp4Player;
    private String currentFile;
    
    public MP4PlayerAdapter() {
        this.mp4Player = new MP4Player();
    }
    
    @Override
    public void play(String filename) {
        this.currentFile = filename;
        mp4Player.loadMP4(filename);
        mp4Player.startPlayback();
    }
    
    @Override
    public void stop() {
        mp4Player.endPlayback();
    }
    
    @Override
    public String getPlayerType() {
        return "MP4";
    }
}

// Client code - Works with any MediaPlayer
class AudioPlayerClient {
    private MediaPlayer mediaPlayer;
    
    public void setPlayer(MediaPlayer player) {
        this.mediaPlayer = player;
    }
    
    public void playFile(String filename) {
        System.out.println("Using " + mediaPlayer.getPlayerType() + " player");
        mediaPlayer.play(filename);
    }
    
    public void stopPlayback() {
        mediaPlayer.stop();
    }
}

// Demo
public class AdapterDemo {
    public static void main(String[] args) {
        AudioPlayerClient client = new AudioPlayerClient();
        
        // Use VLC adapter
        client.setPlayer(new VLCPlayerAdapter());
        client.playFile("movie.vlc");
        client.stopPlayback();
        
        System.out.println();
        
        // Use MP4 adapter
        client.setPlayer(new MP4PlayerAdapter());
        client.playFile("video.mp4");
        client.stopPlayback();
    }
}

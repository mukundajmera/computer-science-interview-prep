/**
 * Bridge Pattern - V1 Basic: Remote Control + Devices
 */

// Implementation Interface
interface Device {
    void powerOn();
    void powerOff();
    void setChannel(int channel);
    void setVolume(int volume);
    boolean isOn();
}

// Concrete Implementations
class TV implements Device {
    private boolean on = false;
    private int channel = 1;
    private int volume = 30;
    
    @Override public void powerOn() { on = true; System.out.println("TV is ON"); }
    @Override public void powerOff() { on = false; System.out.println("TV is OFF"); }
    @Override public void setChannel(int ch) { channel = ch; System.out.println("TV Channel: " + ch); }
    @Override public void setVolume(int vol) { volume = vol; System.out.println("TV Volume: " + vol); }
    @Override public boolean isOn() { return on; }
}

class Radio implements Device {
    private boolean on = false;
    private int station = 88;
    private int volume = 20;
    
    @Override public void powerOn() { on = true; System.out.println("Radio is ON"); }
    @Override public void powerOff() { on = false; System.out.println("Radio is OFF"); }
    @Override public void setChannel(int st) { station = st; System.out.println("Radio Station: " + st + " FM"); }
    @Override public void setVolume(int vol) { volume = vol; System.out.println("Radio Volume: " + vol); }
    @Override public boolean isOn() { return on; }
}

// Abstraction
abstract class RemoteControl {
    protected Device device;  // Bridge to implementation
    
    public RemoteControl(Device device) {
        this.device = device;
    }
    
    public void togglePower() {
        if (device.isOn()) device.powerOff();
        else device.powerOn();
    }
    
    public abstract void volumeUp();
    public abstract void volumeDown();
    public abstract void channelUp();
    public abstract void channelDown();
}

// Refined Abstraction
class BasicRemote extends RemoteControl {
    private int volume = 30;
    private int channel = 1;
    
    public BasicRemote(Device device) { super(device); }
    
    @Override public void volumeUp() { device.setVolume(++volume); }
    @Override public void volumeDown() { device.setVolume(--volume); }
    @Override public void channelUp() { device.setChannel(++channel); }
    @Override public void channelDown() { device.setChannel(--channel); }
}

class AdvancedRemote extends RemoteControl {
    private int volume = 30;
    private int channel = 1;
    
    public AdvancedRemote(Device device) { super(device); }
    
    @Override public void volumeUp() { device.setVolume(++volume); }
    @Override public void volumeDown() { device.setVolume(--volume); }
    @Override public void channelUp() { device.setChannel(++channel); }
    @Override public void channelDown() { device.setChannel(--channel); }
    
    public void mute() {
        System.out.println("Muting...");
        device.setVolume(0);
    }
}

public class BridgeDemo {
    public static void main(String[] args) {
        System.out.println("=== Basic Remote + TV ===");
        RemoteControl tvRemote = new BasicRemote(new TV());
        tvRemote.togglePower();
        tvRemote.channelUp();
        tvRemote.volumeUp();
        
        System.out.println("\n=== Advanced Remote + Radio ===");
        AdvancedRemote radioRemote = new AdvancedRemote(new Radio());
        radioRemote.togglePower();
        radioRemote.channelUp();
        radioRemote.mute();
    }
}

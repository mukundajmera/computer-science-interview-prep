/**
 * Command Pattern - V1 Basic: Remote Control
 */

import java.util.*;

// Command Interface
interface Command {
    void execute();
    void undo();
}

// Receiver Classes
class Light {
    private String location;
    private boolean on = false;
    
    public Light(String location) {
        this.location = location;
    }
    
    public void on() { on = true; System.out.println(location + " light is ON"); }
    public void off() { on = false; System.out.println(location + " light is OFF"); }
    public boolean isOn() { return on; }
}

class Fan {
    private int speed = 0;
    
    public void high() { speed = 3; System.out.println("Fan is on HIGH"); }
    public void medium() { speed = 2; System.out.println("Fan is on MEDIUM"); }
    public void low() { speed = 1; System.out.println("Fan is on LOW"); }
    public void off() { speed = 0; System.out.println("Fan is OFF"); }
    public int getSpeed() { return speed; }
}

// Concrete Commands
class LightOnCommand implements Command {
    private Light light;
    
    public LightOnCommand(Light light) { this.light = light; }
    
    @Override
    public void execute() { light.on(); }
    
    @Override
    public void undo() { light.off(); }
}

class LightOffCommand implements Command {
    private Light light;
    
    public LightOffCommand(Light light) { this.light = light; }
    
    @Override
    public void execute() { light.off(); }
    
    @Override
    public void undo() { light.on(); }
}

class FanHighCommand implements Command {
    private Fan fan;
    private int prevSpeed;
    
    public FanHighCommand(Fan fan) { this.fan = fan; }
    
    @Override
    public void execute() {
        prevSpeed = fan.getSpeed();
        fan.high();
    }
    
    @Override
    public void undo() {
        switch (prevSpeed) {
            case 3: fan.high(); break;
            case 2: fan.medium(); break;
            case 1: fan.low(); break;
            default: fan.off();
        }
    }
}

class NoCommand implements Command {
    @Override
    public void execute() { }
    
    @Override
    public void undo() { }
}

// Invoker
class RemoteControl {
    private Command[] onCommands;
    private Command[] offCommands;
    private Stack<Command> undoStack = new Stack<>();
    
    public RemoteControl(int slots) {
        onCommands = new Command[slots];
        offCommands = new Command[slots];
        Command noCommand = new NoCommand();
        for (int i = 0; i < slots; i++) {
            onCommands[i] = noCommand;
            offCommands[i] = noCommand;
        }
    }
    
    public void setCommand(int slot, Command onCmd, Command offCmd) {
        onCommands[slot] = onCmd;
        offCommands[slot] = offCmd;
    }
    
    public void pressOnButton(int slot) {
        onCommands[slot].execute();
        undoStack.push(onCommands[slot]);
    }
    
    public void pressOffButton(int slot) {
        offCommands[slot].execute();
        undoStack.push(offCommands[slot]);
    }
    
    public void pressUndo() {
        if (!undoStack.isEmpty()) {
            System.out.println("--- Undo ---");
            undoStack.pop().undo();
        }
    }
}

public class CommandDemo {
    public static void main(String[] args) {
        RemoteControl remote = new RemoteControl(3);
        
        Light livingRoom = new Light("Living Room");
        Light kitchen = new Light("Kitchen");
        Fan fan = new Fan();
        
        remote.setCommand(0, new LightOnCommand(livingRoom), new LightOffCommand(livingRoom));
        remote.setCommand(1, new LightOnCommand(kitchen), new LightOffCommand(kitchen));
        remote.setCommand(2, new FanHighCommand(fan), new NoCommand());
        
        System.out.println("=== Remote Control ===");
        remote.pressOnButton(0);   // Living room light ON
        remote.pressOnButton(1);   // Kitchen light ON
        remote.pressOnButton(2);   // Fan HIGH
        
        remote.pressUndo();  // Undo fan
        remote.pressUndo();  // Undo kitchen light
        
        remote.pressOffButton(0);  // Living room OFF
    }
}

package models;

import java.util.*;

public class Branch {
    private final String branchId;
    private final String name;
    private final String location;

    public Branch(String branchId, String name, String location) {
        this.branchId = branchId;
        this.name = name;
        this.location = location;
    }

    public String getBranchId() { return branchId; }
    public String getName() { return name; }
    public String getLocation() { return location; }
    
    @Override
    public String toString() {
        return name + " (" + location + ")";
    }
}

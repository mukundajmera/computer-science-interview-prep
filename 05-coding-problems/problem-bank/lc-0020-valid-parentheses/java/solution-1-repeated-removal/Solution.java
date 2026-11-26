class Solution {
    public boolean isValid(String s) {
        int previousLength = -1;
        String current = s;
        while (current.length() != previousLength) {
            previousLength = current.length();
            current = current.replace("()", "").replace("[]", "").replace("{}", "");
        }
        return current.isEmpty();
    }
}

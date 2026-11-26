class Solution {
    private int index;

    public String decodeString(String s) {
        index = 0;
        return parse(s);
    }

    private String parse(String s) {
        StringBuilder builder = new StringBuilder();
        while (index < s.length() && s.charAt(index) != ']') {
            char current = s.charAt(index);
            if (Character.isDigit(current)) {
                int repeat = 0;
                while (index < s.length() && Character.isDigit(s.charAt(index))) {
                    repeat = repeat * 10 + (s.charAt(index) - '0');
                    index++;
                }
                index++;
                String inner = parse(s);
                index++;
                for (int count = 0; count < repeat; count++) {
                    builder.append(inner);
                }
            } else {
                builder.append(current);
                index++;
            }
        }
        return builder.toString();
    }
}

class StringIterator {
    private final String expanded;
    private int index = 0;

    public StringIterator(String compressedString) {
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < compressedString.length();) {
            char c = compressedString.charAt(i++);
            int count = 0;
            while (i < compressedString.length() && Character.isDigit(compressedString.charAt(i))) count = count * 10 + compressedString.charAt(i++) - '0';
            for (int j = 0; j < count; j++) builder.append(c);
        }
        expanded = builder.toString();
    }

    public char next() {
        return hasNext() ? expanded.charAt(index++) : ' ';
    }

    public boolean hasNext() {
        return index < expanded.length();
    }
}

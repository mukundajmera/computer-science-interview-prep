/**
 * v2 Base62 encoder: parity with v1.
 * See PastebinServiceV2 for the v2 improvement list.
 */
public class Base62EncoderV2 {
    private static final String ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    private static final int BASE = ALPHABET.length();

    public static String encode(long num) {
        if (num < 0) {
            throw new IllegalArgumentException("Number must be non-negative.");
        }
        if (num == 0) {
            return String.valueOf(ALPHABET.charAt(0));
        }

        StringBuilder sb = new StringBuilder();
        while (num > 0) {
            sb.append(ALPHABET.charAt((int) (num % BASE)));
            num /= BASE;
        }

        return sb.reverse().toString();
    }

    public static long decode(String s) {
        if (s == null || s.isEmpty()) {
            throw new IllegalArgumentException("String cannot be empty.");
        }

        long num = 0;
        for (char c : s.toCharArray()) {
            int index = ALPHABET.indexOf(c);
            if (index == -1) {
                throw new IllegalArgumentException("Invalid character in Base62 string: " + c);
            }
            num = num * BASE + index;
        }

        return num;
    }
}

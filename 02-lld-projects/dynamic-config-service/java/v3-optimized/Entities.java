import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

class UserContext {
    private final String userId;
    private final Map<String, String> attributes;

    public UserContext(String userId) {
        this.userId = userId;
        this.attributes = new HashMap<>();
    }

    public void setAttribute(String key, String value) {
        attributes.put(key, value);
    }

    public String getAttribute(String key) {
        return attributes.get(key);
    }

    public String getUserId() {
        return userId;
    }
}

class Variant {
    private final Object value;

    public Variant(Object value) {
        this.value = value;
    }

    public Object getValue() {
        return value;
    }
}

enum Operator {
    EQUALS
}

class RolloutBucket {
    private final int percentage;
    private final Variant variant;

    public RolloutBucket(int percentage, Variant variant) {
        this.percentage = percentage;
        this.variant = variant;
    }

    public int getPercentage() {
        return percentage;
    }

    public Variant getVariant() {
        return variant;
    }
}

class Rollout {
    private final List<RolloutBucket> buckets;

    public Rollout(List<RolloutBucket> buckets) {
        this.buckets = new ArrayList<>(buckets);
    }

    public Variant getVariant(String userId, String flagKey) {
        int hash = getDeterministicHash(userId, flagKey);
        int bucket = (hash & 0x7FFFFFFF) % 100;

        int cumulative = 0;
        for (RolloutBucket rb : buckets) {
            cumulative += rb.getPercentage();
            if (bucket < cumulative) {
                return rb.getVariant();
            }
        }
        return new Variant(null);
    }

    private int getDeterministicHash(String userId, String flagKey) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] hashBytes = md.digest((userId + ":" + flagKey).getBytes());
            int hash = 0;
            for (int i = 0; i < 4; i++) {
                hash = (hash << 8) | (hashBytes[i] & 0xFF);
            }
            return hash;
        } catch (NoSuchAlgorithmException e) {
            return (userId + ":" + flagKey).hashCode();
        }
    }
}

class Rule {
    private final String attribute;
    private final Operator operator;
    private final String value;
    private final Variant result;
    private final Rollout rollout;

    public Rule(String attribute, Operator operator, String value, Variant result) {
        this.attribute = attribute;
        this.operator = operator;
        this.value = value;
        this.result = result;
        this.rollout = null;
    }

    public Rule(String attribute, Operator operator, String value, Rollout rollout) {
        this.attribute = attribute;
        this.operator = operator;
        this.value = value;
        this.rollout = rollout;
        this.result = null;
    }

    public boolean matches(UserContext context) {
        String ctxValue = context.getAttribute(attribute);
        if (ctxValue == null) return false;
        
        if (operator == Operator.EQUALS) {
            return value.equals(ctxValue);
        }
        return false;
    }

    public Variant getResult(UserContext context, String flagKey) {
        if (rollout != null) {
            return rollout.getVariant(context.getUserId(), flagKey);
        }
        return result;
    }
}

class FeatureFlag {
    private final String key;
    private final Variant defaultVariant;
    private final List<Rule> rules;

    public FeatureFlag(String key, Variant defaultVariant, List<Rule> rules) {
        this.key = key;
        this.defaultVariant = defaultVariant;
        this.rules = rules == null ? Collections.emptyList() : new ArrayList<>(rules);
    }

    public Variant evaluate(UserContext context) {
        for (Rule rule : rules) {
            if (rule.matches(context)) {
                return rule.getResult(context, key);
            }
        }
        return defaultVariant;
    }

    public String getKey() {
        return key;
    }
}

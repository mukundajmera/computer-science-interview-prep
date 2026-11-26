import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

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

class Rule {
    private final String attribute;
    private final Operator operator;
    private final String value;
    private final Variant result;

    public Rule(String attribute, Operator operator, String value, Variant result) {
        this.attribute = attribute;
        this.operator = operator;
        this.value = value;
        this.result = result;
    }

    public boolean matches(UserContext context) {
        String ctxValue = context.getAttribute(attribute);
        if (ctxValue == null) return false;
        
        if (operator == Operator.EQUALS) {
            return value.equals(ctxValue);
        }
        return false;
    }

    public Variant getResult() {
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
        this.rules = rules == null ? new ArrayList<>() : rules;
    }

    public Variant evaluate(UserContext context) {
        for (Rule rule : rules) {
            if (rule.matches(context)) {
                return rule.getResult();
            }
        }
        return defaultVariant;
    }

    public String getKey() {
        return key;
    }
}

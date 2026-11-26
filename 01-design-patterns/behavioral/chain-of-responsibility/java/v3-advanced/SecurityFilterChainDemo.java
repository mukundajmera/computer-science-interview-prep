package chainofresponsibility.v3;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * v3-advanced: Priority-Ordered Interceptor Chain with Context and Metrics.
 * Demonstrates an enterprise security filter chain sorting handlers by priority order,
 * accumulating execution audit logs, and supporting circuit-breaking on critical failure.
 */
public class SecurityFilterChainDemo {

    public static class SecurityContext {
        private final String userId;
        private final List<String> roles;
        private final Map<String, Object> attributes = new HashMap<>();
        private final List<String> auditTrail = new ArrayList<>();

        public SecurityContext(String userId, List<String> roles) {
            this.userId = userId;
            this.roles = new ArrayList<>(roles);
        }

        public String getUserId() {
            return userId;
        }

        public List<String> getRoles() {
            return Collections.unmodifiableList(roles);
        }

        public void setAttribute(String key, Object val) {
            this.attributes.put(key, val);
        }

        public Object getAttribute(String key) {
            return this.attributes.get(key);
        }

        public void addAudit(String message) {
            this.auditTrail.add(message);
        }

        public List<String> getAuditTrail() {
            return Collections.unmodifiableList(auditTrail);
        }
    }

    public enum FilterResult {
        PROCEED,
        BLOCK
    }

    public interface SecurityFilter {
        int getOrder();
        String getName();
        FilterResult filter(SecurityContext context);
    }

    public static class BlacklistFilter implements SecurityFilter {
        private final List<String> blockedUsers = List.of("banned_user_1", "bot_99");

        @Override
        public int getOrder() {
            return 10; // Highest priority, check first
        }

        @Override
        public String getName() {
            return "BlacklistFilter";
        }

        @Override
        public FilterResult filter(SecurityContext context) {
            if (blockedUsers.contains(context.getUserId())) {
                context.addAudit("BLOCKED: User is blacklisted");
                return FilterResult.BLOCK;
            }
            context.addAudit("PASSED: User not in blacklist");
            return FilterResult.PROCEED;
        }
    }

    public static class RoleValidationFilter implements SecurityFilter {
        private final String requiredRole;

        public RoleValidationFilter(String requiredRole) {
            this.requiredRole = requiredRole;
        }

        @Override
        public int getOrder() {
            return 20;
        }

        @Override
        public String getName() {
            return "RoleValidationFilter";
        }

        @Override
        public FilterResult filter(SecurityContext context) {
            if (!context.getRoles().contains(requiredRole)) {
                context.addAudit("BLOCKED: Missing required role: " + requiredRole);
                return FilterResult.BLOCK;
            }
            context.addAudit("PASSED: Role verified: " + requiredRole);
            return FilterResult.PROCEED;
        }
    }

    public static class SecurityFilterChain {
        private final List<SecurityFilter> filters = new ArrayList<>();

        public SecurityFilterChain addFilter(SecurityFilter filter) {
            filters.add(filter);
            filters.sort(Comparator.comparingInt(SecurityFilter::getOrder));
            return this;
        }

        public boolean execute(SecurityContext context) {
            for (SecurityFilter filter : filters) {
                FilterResult res = filter.filter(context);
                if (res == FilterResult.BLOCK) {
                    return false;
                }
            }
            return true;
        }
    }

    public static void main(String[] args) {
        SecurityFilterChain chain = new SecurityFilterChain()
                .addFilter(new RoleValidationFilter("ADMIN"))
                .addFilter(new BlacklistFilter());

        SecurityContext validUser = new SecurityContext("alice", List.of("ADMIN", "USER"));
        boolean allowed = chain.execute(validUser);
        System.out.println("Alice allowed: " + allowed + ", Audit: " + validUser.getAuditTrail());

        SecurityContext blockedUser = new SecurityContext("banned_user_1", List.of("ADMIN"));
        boolean blocked = chain.execute(blockedUser);
        System.out.println("Banned user allowed: " + blocked + ", Audit: " + blockedUser.getAuditTrail());
    }
}

/**
 * Notification Service - V1 Basic
 * 
 * Template service and renderer.
 */

import java.util.Map;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Template service interface.
 */
interface TemplateService {
    /**
     * Get template by ID.
     */
    Optional<NotificationTemplate> getTemplate(String templateId);
    
    /**
     * Create or update template.
     */
    NotificationTemplate saveTemplate(NotificationTemplate template);
    
    /**
     * List all active templates.
     */
    java.util.List<NotificationTemplate> listTemplates();
}

/**
 * Template renderer for variable substitution.
 */
class TemplateRenderer {
    
    // Pattern to match {{variableName}}
    private static final Pattern VARIABLE_PATTERN = 
        Pattern.compile("\\{\\{\\s*(\\w+)\\s*\\}\\}");
    
    /**
     * Render a template with provided variables.
     */
    public RenderedContent render(NotificationTemplate template, 
                                  Map<String, String> variables) {
        // Validate required variables
        for (String required : template.getRequiredVariables()) {
            if (!variables.containsKey(required)) {
                throw new IllegalArgumentException(
                    "Missing required variable: " + required);
            }
        }
        
        String renderedSubject = substituteVariables(template.getSubject(), variables);
        String renderedBody = substituteVariables(template.getBody(), variables);
        
        return new RenderedContent(renderedSubject, renderedBody);
    }
    
    /**
     * Substitute variables in a string.
     */
    private String substituteVariables(String text, Map<String, String> variables) {
        if (text == null) {
            return null;
        }
        
        StringBuffer result = new StringBuffer();
        Matcher matcher = VARIABLE_PATTERN.matcher(text);
        
        while (matcher.find()) {
            String variableName = matcher.group(1);
            String value = variables.getOrDefault(variableName, "");
            matcher.appendReplacement(result, Matcher.quoteReplacement(value));
        }
        matcher.appendTail(result);
        
        return result.toString();
    }
}

/**
 * Rendered content after variable substitution.
 */
class RenderedContent {
    private final String subject;
    private final String body;
    
    public RenderedContent(String subject, String body) {
        this.subject = subject;
        this.body = body;
    }
    
    public String getSubject() { return subject; }
    public String getBody() { return body; }
}

/**
 * In-memory template service implementation.
 */
class InMemoryTemplateService implements TemplateService {
    
    private final Map<String, NotificationTemplate> templates = 
        new java.util.concurrent.ConcurrentHashMap<>();
    
    @Override
    public Optional<NotificationTemplate> getTemplate(String templateId) {
        return Optional.ofNullable(templates.get(templateId));
    }
    
    @Override
    public NotificationTemplate saveTemplate(NotificationTemplate template) {
        templates.put(template.getTemplateId(), template);
        return template;
    }
    
    @Override
    public java.util.List<NotificationTemplate> listTemplates() {
        return new java.util.ArrayList<>(templates.values());
    }
}

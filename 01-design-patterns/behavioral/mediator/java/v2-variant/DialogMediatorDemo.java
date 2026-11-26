package mediator.v2;

/**
 * v2-variant: UI Dialog Component Mediator Pattern.
 * Coordinates interactions between UI controls (TextBoxes, Checkboxes, Buttons)
 * so that widgets don't depend directly on one another.
 */
public class DialogMediatorDemo {

    public interface DialogMediator {
        void notify(Component sender, String event);
    }

    public abstract static class Component {
        protected DialogMediator mediator;

        public void setMediator(DialogMediator mediator) {
            this.mediator = mediator;
        }
    }

    public static class TextBox extends Component {
        private String text = "";

        public void setText(String text) {
            this.text = text == null ? "" : text;
            if (mediator != null) {
                mediator.notify(this, "textChanged");
            }
        }

        public String getText() {
            return text;
        }

        public boolean isEmpty() {
            return text.trim().isEmpty();
        }
    }

    public static class Checkbox extends Component {
        private boolean checked = false;

        public void setChecked(boolean checked) {
            this.checked = checked;
            if (mediator != null) {
                mediator.notify(this, "checkChanged");
            }
        }

        public boolean isChecked() {
            return checked;
        }
    }

    public static class Button extends Component {
        private boolean enabled = false;

        public void setEnabled(boolean enabled) {
            this.enabled = enabled;
        }

        public boolean isEnabled() {
            return enabled;
        }

        public void click() {
            if (enabled && mediator != null) {
                mediator.notify(this, "click");
            }
        }
    }

    public static class AuthenticationDialogMediator implements DialogMediator {
        private final TextBox usernameBox = new TextBox();
        private final TextBox passwordBox = new TextBox();
        private final Checkbox termsCheckbox = new Checkbox();
        private final Button submitButton = new Button();
        private boolean submitted = false;

        public AuthenticationDialogMediator() {
            usernameBox.setMediator(this);
            passwordBox.setMediator(this);
            termsCheckbox.setMediator(this);
            submitButton.setMediator(this);
            updateButtonState();
        }

        public TextBox getUsernameBox() {
            return usernameBox;
        }

        public TextBox getPasswordBox() {
            return passwordBox;
        }

        public Checkbox getTermsCheckbox() {
            return termsCheckbox;
        }

        public Button getSubmitButton() {
            return submitButton;
        }

        public boolean isSubmitted() {
            return submitted;
        }

        @Override
        public void notify(Component sender, String event) {
            if ("textChanged".equals(event) || "checkChanged".equals(event)) {
                updateButtonState();
            } else if ("click".equals(event) && sender == submitButton) {
                if (submitButton.isEnabled()) {
                    this.submitted = true;
                }
            }
        }

        private void updateButtonState() {
            boolean valid = !usernameBox.isEmpty() && !passwordBox.isEmpty() && termsCheckbox.isChecked();
            submitButton.setEnabled(valid);
        }
    }

    public static void main(String[] args) {
        AuthenticationDialogMediator dialog = new AuthenticationDialogMediator();
        dialog.getUsernameBox().setText("admin");
        dialog.getPasswordBox().setText("p@ssword");
        System.out.println("Button enabled before terms: " + dialog.getSubmitButton().isEnabled());

        dialog.getTermsCheckbox().setChecked(true);
        System.out.println("Button enabled after terms: " + dialog.getSubmitButton().isEnabled());

        dialog.getSubmitButton().click();
        System.out.println("Form submitted: " + dialog.isSubmitted());
    }
}

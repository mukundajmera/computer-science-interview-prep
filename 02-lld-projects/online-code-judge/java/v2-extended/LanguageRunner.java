
/**
 * Trusted fake execution-adapter simulation.
 * 
 * SECURITY NOTICE:
 * Do not execute user-supplied code, shell commands, compilers, or arbitrary files on the host.
 * stdlib timeouts/resource labels are not a security sandbox.
 * Actual execution must occur in a separately approved VM/container boundary 
 * with strict filesystem, network, CPU, memory, output, and process controls.
 * MLE/TLE are adapter-reported simulations, not unproven isolation.
 */
public interface LanguageRunner {
    ExecutionResult execute(String code, String input);
}

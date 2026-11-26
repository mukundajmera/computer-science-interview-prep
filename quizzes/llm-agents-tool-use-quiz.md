# LLM Agents and Tool Use Quiz

21 questions covering ReAct loops, function calling JSON schemas, Plan-and-Solve architectures, memory, tool sandboxing, and error recovery.

### Question 1
What is the primary defining characteristic of the ReAct (Reasoning and Acting) framework?

A) It forces the LLM to output a JSON object representing a completely static plan before taking any actions
B) It interleaves chain-of-thought reasoning steps with actionable tool use, allowing the model to observe outcomes before deciding the next step
C) It is a specialized React.js frontend component used to render LLM chat interfaces
D) It strictly limits the model to only using mathematical tools for reasoning tasks

### Question 2
When implementing function calling with LLMs, why is providing a rigid JSON Schema (like OpenAPI specs) superior to standard plain-text prompt instructions?

A) JSON schemas compress the prompt, saving token costs compared to plain text
B) JSON schemas automatically execute the code within the LLM's internal runtime without needing application logic
C) Models fine-tuned for function calling use the schema to strongly constrain generation, guaranteeing structured, parsable arguments and preventing hallucinated parameters
D) The schema allows the LLM to write directly to the database without API middleware

### Question 3
In a Plan-and-Solve agent architecture, how does the system mitigate the risk of 'getting stuck in a loop' commonly seen in autonomous ReAct agents?

A) By randomly changing the temperature of the model whenever an identical tool call is detected
B) By explicitly generating a comprehensive, multi-step plan upfront, and then executing the steps sequentially while checking off progress
C) By routing the agent to a human operator after exactly 3 tool calls
D) By restricting the agent to only use one tool per conversation session

### Question 4
Why is 'tool sandboxing' a critical security requirement when building agents capable of executing generated Python code?

A) Because sandboxing automatically fixes syntax errors in the LLM's generated code
B) Because LLMs require a specific version of Python (3.8) to run properly, which sandboxes provide
C) Because sandboxing makes the generated code run faster by utilizing GPU acceleration
D) Because an LLM could generate malicious or destructive code (e.g., deleting files, network exfiltration) either via hallucination or via prompt injection from the user

### Question 5
In an agentic workflow, what is the best strategy for handling an error where the LLM calls a tool with missing required arguments?

A) Catch the parser error in the application layer, format the error as an 'Observation', and feed it back to the LLM so it can self-correct the argument list
B) Immediately crash the application and return a 500 Internal Server Error to the user
C) Silently pass 'None' or empty strings for the missing arguments and execute the tool anyway
D) Switch to a larger, more expensive LLM model and restart the entire conversation

### Question 6
Which memory architecture is most appropriate for a coding agent that needs to maintain context over a project containing hundreds of files and tens of thousands of lines of code over multiple days?

A) Stuffing all the files into the context window at the start of every single prompt
B) A hierarchical memory system combining a vector database for semantic search of files and a summarization loop to maintain a condensed 'working state'
C) A standard FIFO (First In First Out) queue that drops the oldest messages when the context limit is reached
D) Storing the code in a Redis cache and only retrieving it when the user explicitly asks for it

### Question 7
What is the primary vulnerability known as 'Indirect Prompt Injection' in the context of LLM agents?

A) The user explicitly types a jailbreak prompt like 'DAN (Do Anything Now)' directly into the chat interface
B) The agent reads a third-party document (e.g., an email or website) via a tool, and that document contains hidden instructions that hijack the agent's behavior
C) The LLM injects harmful code into the application's database due to a SQL injection vulnerability in the tool's backend
D) The system prompt is accidentally exposed to the user in the frontend UI

### Question 8
When designing an agent that uses a SQL querying tool, why is a 'Read-Only' restriction on the database connection insufficient for total system safety?

A) The LLM will refuse to generate queries if it knows it cannot modify the database
B) Read-only connections can still execute DROP TABLE commands in PostgreSQL
C) The agent could still extract sensitive PII or proprietary data via valid SELECT queries if data access controls and row-level security are not enforced
D) Read-only queries consume too many tokens, leading to out-of-memory errors on the LLM provider

### Question 9
In a Multi-Agent architecture (like AutoGen or CrewAI), what is the primary benefit of dividing a complex task among multiple specialized agents (e.g., a 'Researcher', a 'Coder', and a 'Reviewer')?

A) It scopes the system prompts and tools for each agent tightly, reducing distraction and hallucination while enabling explicit critique and feedback loops
B) It allows the system to bypass the API rate limits of the LLM provider by sending requests in parallel
C) It completely eliminates the need for tool sandboxing, as agents monitor each other
D) It mathematically guarantees that the final output will be logically correct

### Question 10
What is 'Semantic Routing' in the context of agentic tool selection?

A) Using an LLM to rewrite the URL paths in a web application
B) Routing the user's request to different LLM models based on the token count
C) Using vector similarity to compare the user's intent against the descriptions of available tools to select the right one, rather than passing all tool schemas to the LLM
D) Routing network traffic between the agent's microservices based on semantic headers

### Question 11
Which scenario best describes a situation where an agent should utilize a 'Human-in-the-Loop' (HITL) approval step?

A) When the agent is summarizing a publicly available Wikipedia article
B) Every time the agent uses a tool to read the current time or date
C) Before executing an irreversible or high-stakes action, such as executing a financial transaction, sending an email to a client, or modifying production infrastructure
D) When the agent's temperature is set to exactly 0.0

### Question 12
How does the 'Reflexion' pattern improve agent performance on complex coding tasks?

A) By translating the generated code into an intermediate language before execution
B) By reflecting the user's prompt back to them to ensure they typed it correctly
C) By mirroring the codebase across two different vector databases for redundancy
D) By asking the LLM to explicitly reflect on its past failures, generate a diagnosis of what went wrong, and store that 'lesson' in a memory scratchpad for the next attempt

### Question 13
When defining a JSON Schema for a tool that searches a database, why is it critical to enforce strict 'enum' values or highly descriptive parameter types?

A) It prevents the user from typing injection attacks in the chat interface
B) It speeds up the LLM's token generation rate by bypassing the decoding layer
C) It allows the database to cache the query results permanently
D) It narrows the LLM's output space, preventing it from hallucinating invalid column names, unsupported filters, or arbitrary strings that the backend cannot parse

### Question 14
What is the primary cause of 'Context Window Exhaustion' in long-running agent loops, and how is it typically managed?

A) The system prompt being too complex; managed by removing all safety instructions
B) The LLM generating too many 'Thought' tokens; managed by forbidding the LLM from reasoning
C) The user typing prompts that are too long; managed by imposing a 50-character limit on the UI
D) The accumulation of verbose tool observations (e.g., massive JSON API responses or full file contents); managed by truncating, summarizing, or filtering the observations before appending them to the prompt

### Question 15
In the context of evaluating agents, what does 'Trajectory Evaluation' measure?

A) It evaluates how quickly the user types their prompt into the interface
B) It measures the physical trajectory of the data packets between the LLM provider and the cloud server
C) It tracks the memory usage of the agent over time
D) It assesses not just the final answer, but the logical sequence of thoughts, tool choices, and error recoveries the agent took to arrive at the answer

### Question 16
Why is 'Idempotency' a crucial design principle for tools exposed to LLM agents?

A) Because agents may retry failed plans, hallucinate duplicate tool calls, or timeout, and calling an action (like charging a credit card) twice must not result in duplicate side effects
B) Because idempotent tools use fewer tokens in the schema definition
C) Because idempotency encrypts the data before it is sent to the LLM
D) Because it prevents the LLM from using tools concurrently

### Question 17
What is the function of the 'Scratchpad' (or internal monologue) in an agentic prompt?

A) It provides a dedicated space for the LLM to output its reasoning and intermediate calculations before emitting a structured tool call or final answer, heavily improving accuracy
B) It is a temporary file written to disk where the LLM stores downloaded images
C) It is a hidden prompt that the user cannot see but contains their personal data
D) It is a Redis cache used to store the results of previous identical queries

### Question 18
When building a web-browsing agent, why is simply passing the raw HTML of a webpage to the LLM generally a poor architectural choice?

A) Raw HTML causes the LLM to execute cross-site scripting (XSS) attacks against itself
B) LLMs are fundamentally unable to understand HTML syntax
C) Raw HTML is filled with noisy, token-heavy markup (CSS, scripts, deeply nested tags) that wastes context limits and distracts the model from the actual content
D) Passing HTML violates the terms of service of most LLM providers

### Question 19
Which technique is most appropriate to prevent an agent from endlessly looping between two faulty tool calls (e.g., trying A, failing, trying B, failing, trying A...)?

A) Implementing a strict maximum iteration limit (e.g., max_steps=5) and forcing the agent to return a failure message to the user if the limit is hit
B) Allowing the loop to continue until the LLM naturally learns its mistake via gradient descent
C) Hiding all error messages from the agent so it always thinks the tool succeeded
D) Increasing the model's temperature to 1.5 to introduce maximum randomness

### Question 20
In a tool-calling architecture, where does the actual execution of the tool's code occur?

A) Inside the LLM's neural network weights during the forward pass
B) In the application environment (e.g., your Python backend or serverless function); the LLM merely generates the name and arguments of the tool
C) Directly on the user's local browser via WebAssembly
D) On the GPU memory where the LLM is hosted


### Question 21
When dealing with an LLM agent that has access to both a high-latency external web API tool and a fast internal vector database tool, what is the most robust strategy for the agent to optimize response time for user queries that require up-to-date facts?

A) Always execute the high-latency web API tool first, since it guarantees the most recent information, then fall back to the vector DB if the web search fails.
B) Modify the system prompt to explicitly instruct the agent to query the fast internal vector database tool first, and only call the high-latency external web API tool if the vector search returns insufficient or outdated context.
C) Call both tools concurrently in every ReAct loop iteration to maximize context size and let the LLM sort out conflicting information later.
D) Remove the vector database tool entirely to simplify the schema, relying solely on the web API to prevent hallucination.

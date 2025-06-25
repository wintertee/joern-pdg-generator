class PromptGenerator:
    """
    A class to generate structured prompts for a Large Language Model (LLM)
    to analyze code based on a 7-level specification. Each method corresponds
    to a specific analysis level.
    """

    def __init__(self, problem_description: str, language: str, code: str):
        """
        Initializes the generator with the necessary context for a single coding problem.

        Args:
            problem_description (str): The full text of the problem from the Online Judge.
            language (str): The programming language of the code (e.g., 'python', 'java').
            code (str): The source code submission.
        """
        self.problem_description = problem_description
        self.language = language
        self.code = code

    def build_level_1_message(self) -> list[dict]:
        """Generates the prompt for Level 1: Computational Intent."""
        return [
            {
                "role": "user",
                "content": f"""**Task**:
Your task is to analyze the provided problem description and code to distill its core computational goal.

**Specification**:
Generate a **single line of raw text**. This text must be a concise sentence describing the core computational problem, reduced to its fundamental computer science essence and stripped of all narrative context and input / output details.

**Example Output**:
Find the k-th largest element in an unsorted integer array.

**Problem Description**:
```html
{self.problem_description}
```

**Code**:
```{self.language}
{self.code}
```
""",
            }
        ]

    def build_level_2_message(self) -> list[dict]:
        """Generates the prompt for Level 2: Algorithmic Strategy."""
        return [
            {
                "role": "user",
                "content": f"""**Task**:
Your task is to identify the primary algorithmic strategy employed by the provided code to solve the problem.

**Specification**:
Generate a **single line of raw text** containing the standard, industry-recognized name of the core algorithm or technique used.

**Example Output**:
Quickselect Algorithm

**Problem Description**:
```html
{self.problem_description}
```

**Code**:
```{self.language}
{self.code}
```
""",
            }
        ]

    def build_level_3_message(self) -> list[dict]:
        """Generates the prompt for Level 3: Function Architecture."""
        return [
            {
                "role": "user",
                "content": f"""**Task**:
Your task is to analyze the static structure of the code and describe the role of each of its functions.

**Specification**:
Generate a **JSON array of objects** directly. Each object must represent a single user-defined function (including the main entry point if applicable) and contain a `role` description focusing on its single primary purpose.

```json
[
  {{
    "functionName": "string", // The name of the function. e.g. main.
    "role": "string" // A one-sentence description of the function's single responsibility.
  }}
]
```

**Code**:
```{self.language}
{self.code}
```
""",
            }
        ]

    def build_level_4_message(self) -> list[dict]:
        """Generates the prompt for Level 4: Data Structures."""
        return [
            {
                "role": "user",
                "content": f"""**Task**:
Your task is to identify the key data structures used in the code and explain their purpose within the algorithm.

**Specification**:
Generate a **JSON array of objects** directly. Each object must identify a data structure central to the algorithm's logic and explain its purpose (the "why," e.g., "Used for O(1) lookups"). Do not include primitive types. Leave the JSON array blank if no data structures are used.

```json
[
  {{
    "name": "string", // The name of the data structure (e.g., 'HashMap', 'Min-Heap').
    "purpose": "string" // A one-sentence explanation of why this structure was chosen for this algorithm.
  }}
]
```

**Code**:
```{self.language}
{self.code}
```
""",
            }
        ]

    def build_level_5_message(self) -> list[dict]:
        """Generates the prompt for Level 5: Complexity Analysis."""
        return [
            {
                "role": "user",
                "content": f"""**Task**:
Your task is to determine the time and space complexity of the provided code.

**Specification**:
Generate a **single JSON object** directly. It must contain the worst-case time and space complexity in Big O notation, along with a crucial justification explaining the analysis.

```json
{{
  "time": "string", // Time complexity in Big O notation (e.g., "O(N log N)").
  "space": "string", // Space complexity in Big O notation (e.g., "O(N)").
  "reasoning": "string" // A brief (1-2 sentences) justification, mentioning the dominant operations.
}}
```

**Code**:
```{self.language}
{self.code}
```
""",
            }
        ]

    def build_level_6_message(self) -> list[dict]:
        """Generates the prompt for Level 6: Edge Case Handling."""
        return [
            {
                "role": "user",
                "content": f"""**Task**:
Your task is to identify how the code handles important edge cases and boundary conditions.

**Specification**:
Generate a **JSON array of objects** directly. Each object must describe a specific edge case and explain how it's handled, whether through explicit checks or implicitly by the algorithm's logic.

[
  {{
    "caseDescription": "string", // Description of the edge case (e.g., 'Input array is empty', 'k is out of bounds').
    "handlingExplanation": "string" // How the code's logic addresses this case, or if it fails to.
  }}
]

**Problem Description**:
```html
{self.problem_description}
```

**Code**:
```{self.language}
{self.code}
```
""",
            }
        ]

    def build_level_7_message(self) -> list[dict]:
        """Generates the prompt for Level 7: Control & Data Flow."""
        return [
            {
                "role": "user",
                "content": f"""**Task**:
Your task is to produce a detailed, step-by-step trace of the code's execution flow for each function, describing both control decisions and data transformations.

**Specification**:
Generate a **single JSON object which is a dictionary**. Each key is a function name, and the value is an array of "Step Objects" tracing the execution. The `description` for each step must explain its purpose (the "why"), and low-level operations should be grouped into single, meaningful semantic steps.

```json
{{
  "functionName_1": [ // Note: "functionName_1" is a placeholder for an actual function name.
    {{
      "stepId": "integer", // Sequential ID starting from 1 for each function.
      "type": "string", // The category of the operation. Must be one of the following enum values:
                       // - `INITIALIZATION`: The creation and/or setting of an initial value.
                       // - `LOOP`: The beginning of a repetitive control structure (for, while).
                       // - `CONDITION`: A decision point in the code (if, else, switch).
                       // - `COMPUTATION`: Performing a calculation or data transformation.
                       // - `DATA_WRITE`: Modifying the state of a data structure (add, update, remove).
                       // - `DATA_READ`: Accessing data from a variable or structure without changing it.
                       // - `INVOKE`: The act of calling a function or method.
                       // - `RETURN`: Exiting a function, possibly providing a value back.
                       // - `TERMINATION`: Abruptly altering loop flow (break, continue).
                       // - `TRY`: The start of a block monitored for exceptions.
                       // - `CATCH`: The start of a block that handles a specific exception.
                       // - `FINALLY`: A block guaranteed to execute after a try/catch. Used for cleanup.
                       // - `THROW` / `RAISE`: Explicitly creating and signaling an exception.
                       // - `RESOURCE_MANAGEMENT`: A block that automatically manages a resource's lifecycle (e.g., Python's `with`).
      "scopeLevel": "integer", // Nesting depth (0 for top-level, 1 for inside a loop/if, etc.).
      "description": "string", // Explains the PURPOSE and WHY of the step, not just WHAT it does.
      "keyVariables": ["string"], // List of 1-3 most important variables for this step's state.
      // --- Optional fields below ---
      "targetFunction": "string", // For 'INVOKE'
      "arguments": {{}},            // For 'INVOKE'
      "returnVariable": "string", // For 'INVOKE'
      "exceptionType": "string",  // For 'CATCH'
      "exceptionObject": "string",// For 'THROW'
      "resourceVariable": "string"// For 'RESOURCE_MANAGEMENT'
    }}
  ]
}}
```

**Code**:
```{self.language}
{self.code}
```
""",
            }
        ]

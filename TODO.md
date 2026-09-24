# Activities that still need to be done

## Testing strategy
We need to show that the eval has control over the context window, and that each addition to the context window is driving value to the evaluation.

1. Testing prompts with MCP
2. Testing prompts with Tera harness and MCP
3. Testing prompts with Tera harness, skills and MCP
4. Testing prompts with Tera harness, skills, other context (Database, files, etc) and MCP


## Skills
- need a way to include skills in the prompt call
- need to see if the skill was used in the evaluation


## Usage
- need to have a limit on the number of tokens used in the turn
- need to evaluate the usage of the model in terms of tokens used, time taken, etc.
    - we want to understand if the harness is being efficient in terms of time and cost
    
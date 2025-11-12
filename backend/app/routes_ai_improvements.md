Improvements made / to make:

1) Ensure RAG returns a generated LLM answer (not just excerpts)
- Build a prompt that includes a short system instruction, user query, and a limited amount of retrieved context.
- Truncate context by characters to avoid exceeding model input limits.
- For OpenAI: use ChatCompletion with messages=[{'role':'system',...}, {'role':'user',...}]
- For Hugging Face: send the combined prompt to the text-generation endpoint and parse the returned `generated_text`.

2) Citation / source handling
- Include source markers with the message id in the context (e.g., "[msg:12] Subject: ...") so the LLM can cite exact messages.

3) Robust parsing and retries
- If provider call fails, retry once then fall back to extractive output.
- Log errors for diagnosis.

4) Prompt engineering
- Ask the model to answer only from context and say "I don't know" if the answer cannot be found.

5) Token / length management
- Use a simple character-based truncation (approximate tokens) to keep prompt size within a safe window (e.g., 12k characters total).

6) Optional enhancements
- Introduce streaming for long responses.
- Add a Redis-backed embedding/response cache for scalability.

If you want I can now apply a small code patch to `backend/app/routes_ai.py` implementing context truncation, system message, and safer OpenAI/HF calls (with retries).
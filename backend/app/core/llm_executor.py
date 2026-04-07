async def safe_llm_call(llms, prompt, trace_id=None):
    last_error = None

    for llm in llms:
        try:
            model_name = getattr(llm, "model_name", "unknown")

            print(f"[{trace_id}] Trying model: {model_name}")

            response = await llm.ainvoke(prompt)

            print(f"[{trace_id}] Success: {model_name}")
            return response

        except Exception as e:
            print(f"[{trace_id}] Failed: {model_name} | {str(e)}")
            last_error = e
            continue

    raise Exception(f"All models failed. Last error: {last_error}")
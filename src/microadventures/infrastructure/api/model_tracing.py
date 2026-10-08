"""Sentry spans for every call to the model, so latency and tokens show up in Sentry's AI views.

Without SENTRY_DSN, sentry_sdk does nothing and these helpers cost nothing. What the person
wrote and their photos are never sent to Sentry: only the model, sizes, token counts and timings.
"""

from contextlib import contextmanager

import sentry_sdk


@contextmanager
def traced_model_call(operation: str, model: str, prompt: str):
    """Wraps one request to the model. `operation` says why, e.g. "generate_challenges"."""
    with sentry_sdk.start_span(op="gen_ai.request", name=f"{operation} {model}") as span:
        span.set_data("gen_ai.system", "ollama")
        span.set_data("gen_ai.operation.name", operation)
        span.set_data("gen_ai.request.model", model)
        span.set_data("prompt.characters", len(prompt))
        yield span


def record_usage(span, ollama_response: dict) -> None:
    """Copies token counts and the model's own timings from an Ollama reply onto the span."""
    input_tokens = ollama_response.get("prompt_eval_count")
    output_tokens = ollama_response.get("eval_count")
    if input_tokens is not None:
        span.set_data("gen_ai.usage.input_tokens", input_tokens)
    if output_tokens is not None:
        span.set_data("gen_ai.usage.output_tokens", output_tokens)
    if input_tokens is not None and output_tokens is not None:
        span.set_data("gen_ai.usage.total_tokens", input_tokens + output_tokens)
    for field in ("total_duration", "load_duration"):  # nanoseconds in Ollama
        if ollama_response.get(field) is not None:
            span.set_data(f"ollama.{field}_ms", round(ollama_response[field] / 1_000_000))

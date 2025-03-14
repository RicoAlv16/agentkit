# ... existing imports ...
from app.core.prometheus import llm_request_counter, llm_request_duration, TimerContextManager

# ... existing code ...

def get_llm_model(llm_model: Optional[str], temperature: float = 0.0) -> BaseChatModel:
    """
    Get the LLM model from the LLM model type.
    """
    # ... existing code ...
    
    # Wrap the model with Prometheus metrics
    original_generate = model.generate
    
    def instrumented_generate(*args, **kwargs):
        model_name = llm_model or "default"
        with TimerContextManager(llm_request_duration, {"model": model_name}):
            try:
                result = original_generate(*args, **kwargs)
                llm_request_counter.labels(model=model_name, status="success").inc()
                return result
            except Exception as e:
                llm_request_counter.labels(model=model_name, status="error").inc()
                raise e
    
    model.generate = instrumented_generate
    return model

# ... rest of the file ...
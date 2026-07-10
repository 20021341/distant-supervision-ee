import time
import functools
import logging

logger = logging.getLogger(__name__)

def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    A decorator to retry a function call if it raises an Exception.
    
    Args:
        max_attempts (int): Maximum number of attempts before raising the exception.
        delay (float): Initial delay between retries in seconds.
        backoff (float): Multiplier applied to delay after each failure.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            current_delay = delay
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    logger.warning(
                        f"[Retry] Attempt {attempts}/{max_attempts} for '{func.__module__}.{func.__name__}' "
                        f"failed with error: {e}. Retrying in {current_delay}s..."
                    )
                    if attempts >= max_attempts:
                        logger.error(
                            f"[Retry] Function '{func.__module__}.{func.__name__}' failed after {max_attempts} attempts."
                        )
                        raise e
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator


class parallel_batch:
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.func = None

    def __call__(self, func):
        self.func = func
        @functools.wraps(func)
        def wrapper(instance, *args, **kwargs):
            return func(instance, *args, **kwargs)
        self.wrapper = wrapper
        return self

    def __set_name__(self, owner, name):
        setattr(owner, name, self.wrapper)
        batch_name = f"{name}_batch"
        
        def batch_method(instance, items, max_workers=None, callback=None, *args, **kwargs):
            if max_workers is None:
                max_workers = self.max_workers
            from concurrent.futures import ThreadPoolExecutor, as_completed
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_index = {}
                for idx, item in enumerate(items):
                    if isinstance(item, (tuple, list)) and not isinstance(item, str):
                        future = executor.submit(self.func, instance, *item, **kwargs)
                    else:
                        future = executor.submit(self.func, instance, item, **kwargs)
                    future_to_index[future] = idx
                
                from tqdm import tqdm
                results_indexed = [None] * len(items)
                for future in tqdm(as_completed(future_to_index), total=len(items), desc="Processing batch", leave=True):
                    idx = future_to_index[future]
                    result = future.result()
                    results_indexed[idx] = result
                    if callback is not None:
                        try:
                            callback(result)
                        except Exception as cb_err:
                            logger.error(f"Error in batch callback: {cb_err}")
                return results_indexed

                
        setattr(owner, batch_name, batch_method)

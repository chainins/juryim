import sys
from collections.abc import Mapping, MutableMapping, Sequence
from inspect import getfullargspec
import asyncio
import functools

# Patch collections for Python 3.11 compatibility
sys.modules['collections'].Mapping = Mapping
sys.modules['collections'].MutableMapping = MutableMapping
sys.modules['collections'].Sequence = Sequence

# Patch inspect.getargspec for Python 3.11 compatibility
def getargspec(func):
    spec = getfullargspec(func)
    return spec[:4]  # Returns (args, varargs, keywords, defaults)

sys.modules['inspect'].getargspec = getargspec

# Patch asyncio.coroutine for Python 3.11 compatibility
def coroutine(func):
    """Compatibility wrapper for asyncio.coroutine"""
    if asyncio.iscoroutinefunction(func):
        return func
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    return wrapper

# Replace the deprecated asyncio.coroutine
asyncio.coroutine = coroutine
sys.modules['asyncio'].coroutine = coroutine 
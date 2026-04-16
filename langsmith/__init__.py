def traceable(func=None, *, name=None):
    if func is None:
        return lambda f: f
    return func

from lru_cache import lru_cache
import functools

INVOKE_COUNT = 0
# LRU_CACHE = None

def lru_cache_dec(size):    
    # global LRU_CACHE
    # if not LRU_CACHE:
        # LRU_CACHE = lru_cache(size)

    LRU_CACHE = lru_cache(size)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # if func.__name__ == 'delete':
            #     print("==DELETE==")
            #     LRU_CACHE.delete(args[0])
            #     return func(*args, **kwargs)
            
            cache = LRU_CACHE.get(args[0])
            if cache:
                print('==HIT==')
                # print(cache)
                return cache
            else:
                print("==MISS==")
                # if func.__name__ == 'put':
                if len(args) > 1:
                    LRU_CACHE.add(args[0], args[1])
                else:
                    value = func(*args, **kwargs)
                    LRU_CACHE.add(args[0], value)
                    return value
                
                # return func(*args, **kwargs)

        return wrapper
    return decorator

@lru_cache_dec(3)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-2) + fibonacci(n-1)

@lru_cache_dec(4)
def get_data(key):
    global INVOKE_COUNT
    INVOKE_COUNT = INVOKE_COUNT + 1
    return { 'id': key, 'value': f'Foo Bar - {key}' }

def test_get_data(keys):
    for x in keys:
        result = get_data(x)
        print(result)
    print(f'Num of function calls:{len(keys)}')

  
if __name__=='__main__':
    print(f'fibonacci(6)={fibonacci(6)}\n')
    test_get_data([1, 2, 3, 4, 1, 2, 3, 4, 5, 6])
    print(f'Num of cache misses:{INVOKE_COUNT}')
    assert INVOKE_COUNT == 6
 
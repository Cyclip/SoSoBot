from functools import lru_cache
import sys
import random
from mezmorize import Cache
import time
import string
from pathlib import Path
import os
import math

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

try:
    os.rmdir('cache')
except:
    pass

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

cache = Cache(CACHE_TYPE='filesystem', CACHE_DIR='cache')
chars = list(string.ascii_letters + string.digits)

@cache.memoize(10)
def s(stair):
    a = []
    for i in range(20):
        a.append(''.join([random.choice(chars) for i in range(16)]))
    return random.choice(a)

checked = {}

def test():
    global checked
    iters = 0

    while True:
        n = random.randint(5, 30)

        if n in checked.keys():
            prefix = '[+]'
            addChecked = False
        else:
            prefix = '[ ]'
            addChecked = True
        
        start = time.time()
        r = s(n)
        timed = round(time.time() - start, 5)

        msg = f'{prefix} [{timed}s] {n} = {r}'

        if addChecked:
            checked[n] = timed
        else:
            msg += f'\t[{checked[n]}]'

        iters += 1
        ds = get_size(start_path='./cache')
        print(f'  [{convert_size(ds)}] Iterations: {iters}\t', end='\r')

test()

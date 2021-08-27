This allows to override things.

Some examples:
```python
$ cat target.py
import sys

print(sys.executable)
$ python target.py
/usr/bin/python
$ cat patch.py
from hijack import BinLaden

patcher = BinLaden()
patcher.override("sys.executable", "nope")
patcher.run("target.py")
$ python patch.py
nope
$
```

This could be useful to add some functionality or act as a decorator:
```python
$ cat target.py
import requests

try:
    r = requests.get("fsf.org")
    print(r.status_code, r.reason)
except Exception as e:
    print(e)
$ python target.py
Invalid URL 'fsf.org': No schema supplied. Perhaps you meant http://fsf.org?
$ cat patch.py
from hijack import BinLaden

patcher = BinLaden()
old_get = patcher.import_("requests").get

@patcher.override("requests.get")
def get(url, *a, **kw):
    if not url.startswith("http"):
        url = "https://" + url
    return old_get(url, *a, **kw)

patcher.run("target.py")
$ python patch.py
200 OK
$
```

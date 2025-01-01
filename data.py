import asyncio


class SafeDict:
    def __init__(self):
        self._mutex = asyncio.Lock()
        self._map = dict()

    def __setitem__(self, key, value):
        async with self._mutex:
            self._map[key] = value

    def __getitem__(self, key):
        async with self._mutex:
            return self._map[key]

    def __contains__(self, key):
        async with self._mutex:
            return key in self._map

    def __len__(self):
        async with self._mutex:
            return len(self._map)

    def __str__(self):
        async with self._mutex:
            return str(self._map)

    def keys(self):
        async with self._mutex:
            return self._map.keys()

    def pop(self, key):
        async with self._mutex:
            self._map.pop(key)


onlinerspass:SafeDict = SafeDict()
onlinerskey:SafeDict = SafeDict()
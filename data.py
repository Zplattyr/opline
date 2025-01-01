import asyncio

class TrackingLock:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.owner = None  # Track the task holding the lock

    async def acquire(self):
        await self.lock.acquire()
        # Track the task that acquired the lock
        self.owner = asyncio.current_task()

    def release(self):
        self.lock.release()
        # Reset the owner when the lock is released
        self.owner = None

    async def __aenter__(self):
        await self.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def get_owner(self):
        # Return the task holding the lock, or None if no task holds it
        return self.owner

class SafeDict:
    def __init__(self):
        self._mutex = TrackingLock()
        self._map = dict()

    def __setitem__(self, key, value):
        with self._mutex:
            self._map[key] = value

    def __getitem__(self, key):
        with self._mutex:
            return self._map[key]

    def __contains__(self, key):
        owner = self._mutex.get_owner()
        if owner:
            print(f"Lock is held by task: {owner.get_name()}")
        else:
            print("Lock is currently not held by any task.")
        with self._mutex:
            return key in self._map

    def __len__(self):
        with self._mutex:
            return len(self._map)

    def __str__(self):
        with self._mutex:
            return str(self._map)

    def keys(self):
        with self._mutex:
            return self._map.keys()

    def pop(self, key):
        with self._mutex:
            self._map.pop(key)


onlinerspass:SafeDict = SafeDict()
onlinerskey:SafeDict = SafeDict()
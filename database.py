import aiosqlite

class Database:

    def __init__(self):
        self.DB_PATH = 'database.db'
        self.conn = None
        self.curs = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.DB_PATH)
    
    async def __aenter__(self, *args, **kwargs):
        self.curs = await self.conn.cursor()

    async def __aexit__(self, *args, **kwargs):
        await self.curs.close()

    async def is_user_exists(self, user_id: int) -> bool:
        async with self:
            await self.curs.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            return bool(await self.curs.fetchone())

    async def is_user_admin(self, user_id: int) -> bool:
        async with self:
            await self.curs.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            fetch = await self.curs.fetchone()
            if fetch[4] == 1:
                return True
            else:
                return False
        
    async def register_user(self, user_id: int, username: str) -> None:
        is_exists = await self.is_user_exists(user_id)
        if not is_exists:
            async with self:
                await self.curs.execute('INSERT INTO users (user_id, username) VALUES (?, ?)', (user_id, username,))
                await self.conn.commit()

    async def get_expiration_date(self, user_id) -> str:
        async with self:
            await self.curs.execute('SELECT expiration FROM users WHERE subscription=? AND user_id=?', (1, user_id,))
            fetch = await self.curs.fetchone()
            return fetch[0]

    async def subscription_expired(self, user_id) -> None:
        async with self:
            await self.curs.execute('UPDATE users SET subscription=? WHERE user_id=?', (0, user_id,))
            await self.curs.execute('UPDATE users SET expiration=? WHERE user_id=?', (None, user_id,))
            await self.conn.commit()

    async def get_subscription(self, user_id, date) -> None:
        async with self:
            await self.curs.execute('UPDATE users SET subscription=? WHERE user_id=?', (1, user_id,))
            await self.curs.execute('UPDATE users SET expiration=? WHERE user_id=?', (date, user_id,))
            await self.conn.commit()

    async def get_code_date(self, code) -> int:
        async with self:
            await self.curs.execute('SELECT valid FROM codes WHERE code=?', (code,))
            fetch = await self.curs.fetchone()
            await self.curs.execute('DELETE FROM codes WHERE code=?', (code,))
            return fetch

    async def insert_code(self, code, valid) -> None:
        async with self:
            await self.curs.execute('INSERT INTO codes (code, valid) VALUES (?, ?)', (code, valid,))
            await self.conn.commit()

    async def getuserscount(self):
        self.conn = await aiosqlite.connect(self.DB_PATH)
        self.curs = await self.conn.cursor()
        await self.curs.execute('SELECT count(user_id) FROM users')
        return [i[0] for i in await self.curs.fetchall()][0]
    
    async def getuserslist(self):
        async with self:
            await self.curs.execute('SELECT user_id FROM users WHERE subscription=?', (1,))
            return [i[0] for i in await self.curs.fetchall()]

    async def getuserslistformailing(self):
        return [await self.getuserscount(), await self.getuserslist()]
    
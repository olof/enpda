import sqlite3
import secrets

class Data:
    def __init__(self, dbpath):
        self.db = sqlite3.connect(dbpath, isolation_level=None)
        try:
            self.schema = self.get_config('schema')
        except sqlite3.OperationalError as exc:
            if not exc.args[0].startswith('no such table:'):
                raise
            self.init_db()

    def init_db(self):
        self.schema = 1
        self.db.execute('''
            CREATE TABLE dynamo (
                hashkey VARCHAR NOT NULL,
                sortkey VARCHAR NOT NULL,
                value TEXT,
                unique(hashkey, sortkey)
            );
        ''')
        self.insert('config', 'schema', self.schema)

    def get_config(self, what):
        return self.get_value('config', what)

    def get_value(self, hashkey, sortkey):
        try:
            return list(self.db.execute(
                'SELECT value FROM dynamo WHERE hashkey=? AND sortkey=?', (
                    str(hashkey),
                    str(sortkey)
                )
            ))[0][0]
        except IndexError:
            return

    def get_collection(self, what):
        return self.db.execute('''
            SELECT hashkey, sortkey, value
            FROM dynamo
            WHERE hashkey=?
            ORDER BY sortkey
        ''', (str(what), ))

    def insert(self, hashkey, sortkey, value):
        return self.db.execute('''
            INSERT INTO dynamo VALUES (?, ?, ?)
        ''', [str(hashkey), str(sortkey), str(value)])

    def update(self, hashkey, sortkey, value):
        return self.db.execute('''
            UPDATE dynamo
            SET value=?
            WHERE hashkey=? AND sortkey=?
        ''', [str(value), str(hashkey), str(sortkey)])

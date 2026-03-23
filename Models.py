import json
import sqlite3

def prnt(arg):
    print(arg, type(arg))
    return arg

class DBManager:
    def __init__(self) -> None:
        self.eng = sqlite3.connect("./db.sqlite3")
        self.build_table()

    def build_table(self) -> None:
        cursor = self.eng.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER NOT NULL UNIQUE, save_history BOOLEAN NOT NULL DEFAULT TRUE, history TEXT DEFAULT '[]', len INTEGER NOT NULL DEFAULT 24, upper BOOLEAN NOT NULL DEFAULT TRUE, lower BOOLEAN NOT NULL DEFAULT TRUE, digits BOOLEAN NOT NULL DEFAULT TRUE, special BOOLEAN NOT NULL DEFAULT FALSE)")
        cursor.close()
        self.eng.commit()

    def add_user(self, id: int) -> None:
        cursor = self.eng.cursor()
        cursor.execute(f"INSERT INTO users(id) VALUES ({id})")
        cursor.close()
        self.eng.commit()

    def check_user(self, id: int) -> bool:
        cursor = self.eng.cursor()
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM users WHERE id = ?)", (id,))
        return bool(cursor.fetchone()[0])

    def confirm_user(self, id: int) -> None:
        if not self.check_user(id): self.add_user(id)

    def get_password_settings(self, id: int) -> tuple[int, bool, bool, bool, bool]:
        cursor = self.eng.cursor()
        cursor.execute("SELECT len, upper, lower, digits, special FROM users WHERE id = ?", (id,))
        return cursor.fetchone()

    def add_to_history(self, id: int, nw: str) -> None:
        cursor = self.eng.cursor()
        cursor.execute("""
            UPDATE users SET history = (
                SELECT json_group_array(value) FROM (
                    SELECT value FROM (
                        SELECT key, value 
                        FROM json_each(json_insert(history, '$[#]', ?))
                        ORDER BY key DESC
                        LIMIT 5
                    )
                    ORDER BY key ASC
                )
            ) WHERE id = ?
        """, (nw, id))
        self.eng.commit()
        cursor.close()

    def clear_history(self, id: int) -> None:
        cursor = self.eng.cursor()
        cursor.execute("UPDATE users SET history = json('[]') WHERE id = ?", (id,))
        cursor.close()
        self.eng.commit()

    def get_history(self, id: int) -> list:
        cursor = self.eng.cursor()
        cursor.execute("SELECT (history) FROM users WHERE id = ?", (id,))
        return json.loads(cursor.fetchall()[0][0])

    def save_history(self, id: int, new_val: bool) -> None:
        cursor = self.eng.cursor()
        cursor.execute("UPDATE users SET save_history = ? WHERE id = ?", (new_val, id))
        cursor.close()
        self.eng.commit()

    def change_password_parameter(self, id: int, key: str, val: int) -> None:
        cursor = self.eng.cursor()
        cursor.execute(f"UPDATE users SET {key} = ? WHERE id = ?", (val, id))
        cursor.close()
        self.eng.commit()

    def is_saving_history(self, id: int) -> bool:
        cursor = self.eng.cursor()
        cursor.execute("SELECT save_history FROM users WHERE id = ?", (id,))
        return bool(cursor.fetchone()[0])

if __name__ == "__main__":
    test = DBManager()
    # test.add_user(2)
    # test.add_to_history(2, "sth")
    # print(test.get_history(2))
    # test.save_history(2, True)
    # print(test.is_saving_history(2))

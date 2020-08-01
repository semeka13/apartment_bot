import sqlite3
import config

DBNAME = config.DBNAME

# Класс для взаимодействия с пользователями
class User:
    def get_from_tg_id(self, tg_id: int) -> dict:
        """
        Инициализация объекта класса и проверка есть ли пользователь с данным tg_id в базе данных
        На выход:
        {"status": "ok"}
        {"status": "user not found"}
        {"status": unknown error}
        """
        try:
            with sqlite3.connect(DBNAME) as conn:
                cursor = conn.cursor()
                assert type(tg_id) == int, "invalid type for tg_id"
                cursor.execute("SELECT user_id FROM users WHERE tg_id = ?", (tg_id,))
                if cursor.fetchone():
                    conn.commit()
                    self.tg_id = tg_id
                    return {"status": "ok"}
                return {"status": "user not found"}
        except Exception as ex:
            return {"status": ex.args[0]}
        finally:
            conn.close()

    def get_apt(self) -> dict:
        try:
            with sqlite3.connect(DBNAME) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT apartment FROM users WHERE tg_id = ?", (self.tg_id,))
                apt = cursor.fetchone()
                if apt:
                    conn.commit()
                    return {"status": "ok", "out": apt}
                return {"status": "no apt"}
        except Exception as ex:
            return {"status": ex.args[0]}
        finally:
            conn.close()

    def add_transport_time(self, transport, time):
        try:
            with sqlite3.connect(DBNAME) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO VALUES users (transport, arriving_time) VALUES (?, ?) WHERE tg_id = ?", (transport, time, self.tg_id,))
                conn.commit()
                return {"status": "ok"}
        except Exception as ex:
            return {"status": ex.args[0]}
        finally:
            conn.close()
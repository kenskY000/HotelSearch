from typing import Dict, List, TypeVar

from peewee import ModelSelect

from database.models import db, ModelBase

T = TypeVar('T')


def _store_data(db: db, model: T, *data: List[Dict]) -> None:
    """
    Скрытая функция для записи каких либо данных в базу данных
    :param db: База, в которую нужно внести запись
    :param model: Таблица в которую нужно внести запись
    :param data: Данные которые необходимо записать
    """
    with db.atomic():
        model.insert_many(*data).execute()


def _retrieve_all_data(db: db, model: T, *columns: ModelBase) -> ModelSelect:
    """
    Функция для получения каких либо данных из базы.
    :param db: База из которой необходимо получить информацию
    :param model: Таблица из которой необходимо получить запись
    :param columns: Количество записей которые необходимо получить
    :return: Возвращает таблицу
    """
    with db.atomic():
        response = model.select(*columns)

    return response


class CRUDInterface:
    @staticmethod
    def create():
        return _store_data

    @staticmethod
    def retrieve():
        return _retrieve_all_data


if __name__ == "__main__":
    _store_data()
    _retrieve_all_data()
    CRUDInterface()

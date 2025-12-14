# Library API

RESTful API для управления библиотечным каталогом с JWT аутентификацией, разработанное на FastAPI.

## Cтек проекта
- **Python 3.12**
- **FastAPI** - веб-фреймворк
- **PostgreSQL** - База данных
- **SQLAlchemy** - ORM для работы с БД
- **Alembic** - управление миграциями
- **python-jose** - создание и валидация JWT токенов
- **passlib[bcrypt]** - хеширование паролей
- **Pydantic** - валидация данных

## Принятые решения по структуре БД
1. Сделал отдельную таблицу `borrowed_books`, чтобы можно было полностью видеть историю выдачи книг
2. В таблице `books` сделал `return_date` nullable, так, например можно проверить, сдана ли та или иная книга

## Реализация бизнес-логики
### 4.1 - Книгу можно выдать, только если есть доступные экземляры

`src/api/borrowing.py`:
```python
if book.copies_available <= 0:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Book '{book.title}' has no available copies"
    )
```
**Сложности**: При большом количестве запросов возможна гонка данных. Решил, используя транзакции

### 4.2 - Один читатель не может взять более 3-х книг одновременно

`src/api/borrowing.py`
```python
active_borrowings_result = await db.execute(
    select(func.count(BorrowedBook.id))
    .where(
        and_(
            BorrowedBook.reader_id == borrow_data.reader_id,
            BorrowedBook.return_date.is_(None)
        )
    )
)
active_count = active_borrowings_result.scalar_one()

if active_count >= 3:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Reader '{reader.name}' already has {active_count} active borrowings. Maximum is 3."
    )
```

**Сложности**: Нужно было правильно посчитать только те книги, которые пользователь еще не вернул, решил условием `return_date is NULL`

### 4.3 - Нельзя вернуть книгу, которая не была выдана этому читателю или уже возвращена

`src/api/borrowing.py`
```python
result = await db.execute(
    select(BorrowedBook)
    .where(
        and_(
            BorrowedBook.book_id == return_data.book_id,
            BorrowedBook.reader_id == return_data.reader_id,
            BorrowedBook.return_date.is_(None)
        )
    )
)
borrowing = result.scalar_one_or_none()

if not borrowing:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="This book was not borrowed by this reader or was already returned"
    )
```

**Сложности**: Нужно было проверять все три условия одновременно для того, чтобы быть уверенным в точности ответа

## Аутентификация JWT

### Библиотеки:

- **python-jose** - для создания и декодирования JWT токенов
- **passlib[bcrypt]** - для хеширования паролей

### Эндпоинты

1. **Регистрация** `POST /auth/register`:
   - Принимает email и password
   - Хеширует пароль с помощью bcrypt
   - Сохраняет пользователя в БД

2. **Вход** `POST /auth/login`:
   - Проверяет email и password
   - Генерирует JWT access token со сроком действия (по умолчанию 30 минут)
   - Возвращает токен клиенту

3. **Защита**:
   - Все операции с книгами, читателями, выдачей требуют заголовок `Authorization: Bearer ...`
   - Сделал dependency `get_current_user`, который сразу проверяет и декодирует токен
   - При невалидном токене возвращается 401 Unauthorized

### Защищенные эндпоинты

- Все CRUD операции с книгами
- Все CRUD операции с читателями
- Выдача и возврат книг
- Получение списка книг читателя

### Незащищенные эндпоинты
- Регистрация и вход
- Список всех книг

### Проблема, с которой столкнулся
- Выдавалась ошибка (длина пароля более 72 символов, что не соответствовало действительности) при хешировании пароля через `passlib[bcrypt]`. Решил проблему даунгрейдом с версии `bcrypt==5.0.0` до `bcrypt==4.3.0`

## Предложения по доработке
- Добавить кеширование Redis для статичных данных книги. Например, для названия, описания, и т.д.

## Инструкция по запуску
1. Клонируем репозиторий:
`git clone https://github.com/aiopalm/library-api.git`
2. Создаем `.env` файл, используя содержимое `.env.example`
3. Билдим проект:
docker compose build`
4. Запускаем:
`docker compose up`. Добавьте флаг `-d` для запуска в фоне
### Документация
`http://localhost:8000/docs`



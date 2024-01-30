from sqlalchemy import create_engine

# db_url = 'postgresql://username:password@host:port/dbname'
db = 'postgresql://postgres:Mother1505@localhost:5432/new_bank_service'
print("Подключение установлено")

engine = create_engine(db, echo=False)
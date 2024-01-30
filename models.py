from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DECIMAL, TIMESTAMP, func
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now(), default=func.now())


class BankAccount(Base):
    __tablename__ = 'bank_accounts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    accounts = Column(String, nullable=False, unique=True)
    amount = Column(Float, default=0.0)
    status = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), default=func.now())
    transactions = relationship('Transaction', back_populates='account')


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, nullable=False)
    account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=False)
    operation = Column(String(2000), nullable=False)
    amount = Column(DECIMAL(1000, 2), nullable=False)
    timestamp = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', nullable=False)

    account = relationship('BankAccount', back_populates='transactions')

    def __repr__(self):
        return f"<Transaction(id={self.id}, account_id={self.account_id}, operation={self.operation}, amount={self.amount}, timestamp={self.timestamp})>"

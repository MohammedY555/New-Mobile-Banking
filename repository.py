from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from connections import engine
from models import User, BankAccount, Transaction
from datetime import datetime

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def index():
    return render_template('main_page.html')


@app.route('/users')
def users():
    Session = sessionmaker(bind=engine)
    session = Session()
    users = session.query(User).all()
    session.close()
    return render_template('users.html', users=users)


@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    user_id = request.form.get('userId')

    new_user = User(username=username, password=password, created_at=datetime.utcnow())

    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(new_user)
    session.commit()
    session.close()

    return jsonify({'status': 'success', 'message': 'Пользователь добавлен успешно!'})


@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form.get('user_id')

    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter(User.id == user_id).first()

    if user:
        try:
            session.delete(user)
            session.commit()
            session.close()
            return jsonify({'status': 'success', 'message': 'Пользователь удален успешно!'})
        except IntegrityError:
            session.rollback()
            session.close()
            return jsonify({'status': 'error',
                            'message': 'Не удается удалить пользователя. Пользователь связан с другими объектами в '
                                       'базе данных.'})
    else:
        session.close()
        return jsonify({'status': 'error', 'message': 'Пользователь не найден!'})


@app.route('/bank_accounts')
def accounts():
    Session = sessionmaker(bind=engine)
    session = Session()
    bank_accounts = session.query(BankAccount).all()
    session.close()
    return render_template('bank_accounts.html', bank_accounts=bank_accounts)


@app.route('/create_account', methods=['POST'])
def create_account():
    try:
        user_id = request.form.get('user_id')
        accounts = request.form.get('accounts')
        amount = float(request.form.get('amount', 0.0))
        status = bool(request.form.get('status', True))

        new_account = BankAccount(user_id=user_id, accounts=accounts, amount=amount, status=status)

        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(new_account)
        session.commit()
        session.close()

        return jsonify({"status": "success", "message": "Банковский счет создан успешно!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/delete_account', methods=['POST'])
def delete_account():
    account_id = request.form.get('id')
    Session = sessionmaker(bind=engine)
    session = Session()

    account = session.query(BankAccount).filter(BankAccount.id == account_id).first()

    if account:
        try:
            session.delete(account)
            session.commit()
            session.close()
            return jsonify({'status': 'success', 'message': 'Банковский счет удален успешно!'})
        except IntegrityError:
            session.rollback()
            session.close()
            return jsonify({'status': 'error', 'message': 'Не удается удалить банковский счет.'})
    else:
        session.close()
        return jsonify({'status': 'error', 'message': 'Банковский счет не найден!'})


@app.route('/deposit', methods=['POST'])
def deposit():
    try:
        data = request.json
        description = data.get('description')
        account_id = data.get('accountId')
        amount = float(data.get('amount', 0.0))

        Session = sessionmaker(bind=engine)
        session = Session()

        account = session.query(BankAccount).filter(BankAccount.id == account_id).first()

        if account:
            try:
                account.amount += amount
                new_transaction = Transaction(operation=description, account_id=account_id, amount=amount)
                session.add(new_transaction)
                session.commit()
                session.close()

                return jsonify({"status": "success", "message": "Банковский счет успешно пополнен!"})

            except IntegrityError:
                session.rollback()
                session.close()
                return jsonify({'status': 'error', 'message': 'Не удается обновить банковский счет.'})
        else:
            session.close()
            return jsonify({'status': 'error', 'message': 'Банковский счет не найден!'})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/withdraw', methods=['POST'])
def withdraw():
    try:
        data = request.json
        description = data.get('description')
        account_id = data.get('accountId')
        amount = float(data.get('amount', 0.0))

        Session = sessionmaker(bind=engine)
        session = Session()

        account = session.query(BankAccount).filter(BankAccount.id == account_id).first()

        if account:
            try:
                if account.amount >= amount:
                    account.amount -= amount
                    new_transaction = Transaction(operation=description, account_id=account_id, amount=-amount)
                    session.add(new_transaction)
                    session.commit()
                    session.close()

                    return jsonify({"status": "success", "message": "Средства успешно списаны с банковского счета!"})
                else:
                    session.close()
                    return jsonify({'status': 'error', 'message': 'Недостаточно средств на банковском счете.'})

            except IntegrityError:
                session.rollback()
                session.close()
                return jsonify({'status': 'error', 'message': 'Не удается обновить банковский счет.'})
        else:
            session.close()
            return jsonify({'status': 'error', 'message': 'Банковский счет не найден!'})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/transfer', methods=['POST'])
def transfer():
    try:
        data = request.json
        description = data.get('description')
        from_account_id = data.get('fromAccountId')
        to_account_id = data.get('toAccountId')
        amount = float(data.get('amount', 0.0))

        Session = sessionmaker(bind=engine)
        session = Session()

        from_account = session.query(BankAccount).filter(BankAccount.id == from_account_id).first()
        to_account = session.query(BankAccount).filter(BankAccount.id == to_account_id).first()

        if from_account and to_account:
            try:
                if from_account.amount >= amount:
                    from_account.amount -= amount
                    to_account.amount += amount

                    transaction_from = Transaction(operation=description, account_id=from_account_id, amount=-amount)
                    transaction_to = Transaction(operation=description, account_id=to_account_id, amount=amount)

                    session.add_all([transaction_from, transaction_to])
                    session.commit()
                    session.close()

                    return jsonify({"status": "success", "message": "Трансфер успешно выполнен!"})
                else:
                    session.close()
                    return jsonify({'status': 'error', 'message': 'Недостаточно средств на счете для трансфера.'})
            except IntegrityError:
                session.rollback()
                session.close()
                return jsonify({'status': 'error', 'message': 'Не удается обновить банковские счета.'})
        else:
            session.close()
            return jsonify({'status': 'error', 'message': 'Один из банковских счетов не найден!'})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/transactions')
def transactions():
    Session = sessionmaker(bind=engine)
    session = Session()
    transactions = session.query(Transaction).all()

    session.close()

    return render_template('transactions.html', transactions=transactions)


if __name__ == '__main__':
    app.run(debug=True)

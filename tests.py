from database import db, Account, Transaction, NegativeAmountException, \
    NoBalanceException
import os
import pytest
from decimal import Decimal

@pytest.fixture(scope="module")
def database():
    db.connect()
    db.create_tables([Account, Transaction])
    yield db
    
    db.close()
    os.remove('test.sqlite3')
    

def test(database):
    account1 = Account.create()
    account2 = Account.create()

    with pytest.raises(NegativeAmountException):
        assert account1.deposit(-1000)    

    assert account1.balance == Decimal("0")
    account1.deposit(1000)
    assert account1.balance == Decimal("1000.00")

    assert account2.balance == Decimal("0")
    account2.deposit(2000)
    assert account2.balance == Decimal("2000.00")
    
    account1.transfer(500, account2)
    assert account1.balance == Decimal("500")
    assert account2.balance == Decimal("2500")

    with pytest.raises(NoBalanceException):
        assert account1.transfer(1000, account2)
    
    with pytest.raises(NegativeAmountException):
        assert account1.transfer(-500, account2)

    with pytest.raises(NoBalanceException):
        account1.withdraw(600)
    
    with pytest.raises(NegativeAmountException):
        account1.withdraw(-400)
    
    account1.withdraw(500)
    assert account1.balance == 0

    assert str(account1.get_statement()[0]).startswith('1000, type: e, date:')
    assert str(account1.get_statement()[1]).startswith('-500, type: d, date:')
    assert str(account1.get_statement()[2]).startswith('-500, type: w, date:')


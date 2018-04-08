import peewee
from decouple import config
from datetime import datetime, timedelta

TYPE_DEBIT = 'd'
TYPE_CREDIT = 'c'
TYPE_DEPOSIT = 'e'
TYPE_WITHDRAW = 'w'

db = peewee.SqliteDatabase(config('DATABASE_NAME', default='test.sqlite3'))

class NoBalanceException(Exception):
    pass


class NegativeAmountException(Exception):
    pass



class Account(peewee.Model):

    class Meta:
        database = db  # This model uses the "people.db" database.

    def __str__(self):
        return "#{}".format(self.id)

    @property
    def balance(self):
        query = Transaction.select(
            peewee.fn.Sum(Transaction.amount).alias('balance')) \
        .where(Transaction.account == self)

        if query.first().balance:
            return query.first().balance
        return 0

    def deposit(self, amount):
        if amount < 0:
            raise NegativeAmountException
        
        return Transaction.create(
            type=TYPE_DEPOSIT, amount=amount, account=self)
    
    def transfer(self, amount, destination):
        if self.balance < amount:
            raise NoBalanceException
        
        if amount < 0:
            raise NegativeAmountException
        
        Transaction.create(type=TYPE_DEBIT, amount=-amount, account=self)
        Transaction.create(type=TYPE_CREDIT, amount=amount, account=destination)
    
    def withdraw(self, amount):
        if self.balance < amount:
            raise NoBalanceException
        
        if amount < 0:
            raise NegativeAmountException
        
        Transaction.create(type=TYPE_WITHDRAW, amount=-amount, account=self)
    
    def get_statement(self):
        return Transaction.select().where(Transaction.account == self)

class Transaction(peewee.Model):
    
    TYPES_CHOICES = (
        (TYPE_CREDIT, 'Credit'),
        (TYPE_DEBIT, 'Debit'),
        (TYPE_DEPOSIT, 'Deposit'),
        (TYPE_WITHDRAW, 'Withdraw'),
    )

    type = peewee.CharField(max_length=1, choices=TYPES_CHOICES)
    amount = peewee.DecimalField()
    account = peewee.ForeignKeyField(Account)
    created = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = db # This model uses the "people.db" database.

    def __str__(self):
        return "{}, type: {}, date: {}".format(
            self.amount, self.type, self.created)

from sqlalchemy import Column, String,Integer, ForeignKey
from .payment import Payment

class DebitCardPayment(Payment):
    __tablename__ = 'debit_card_payments'

    id = Column(Integer, ForeignKey('payments.id'), primary_key=True)
    bank_name = Column(String(50), nullable=False)
    debit_card_number = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<DebitCardPayment(amount={self.payment_amount}, bank_name={self.bank_name})>"

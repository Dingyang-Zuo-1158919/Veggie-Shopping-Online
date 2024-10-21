from sqlalchemy import Column, String, Integer, ForeignKey, Date
from .payment import Payment

class CreditCardPayment(Payment):
    __tablename__ = 'credit_card_payments'

    id = Column(Integer, ForeignKey('payments.id'), primary_key=True)
    card_expiry_date = Column(Date, nullable=False)
    card_number = Column(String(50), nullable=False)
    card_type = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<CreditCardPayment(amount={self.payment_amount}, card_type={self.card_type})>"

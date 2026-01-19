
from intasend import APIService
from django.conf import settings

class IntaSendService:
    def __init__(self):
        self.service = APIService(
            token=settings.INTASEND_SECRET_KEY,
            publishable_key=settings.INTASEND_PUBLISHABLE_KEY,
            test=settings.INTASEND_TEST_MODE
        )

    def trigger_stk_push(self, phone_number, amount, narrative="Food Order Payment"):
        """
        Trigger M-Pesa STK Push
        """
        payment = self.service.collect.mpesa_stk_push(
            phone_number=phone_number,
            email="customer@example.com", # Optional or get from user
            amount=amount,
            narrative=narrative
        )
        return payment

    def check_status(self, invoice_id):
        """
        Check payment status
        """
        status = self.service.collect.status(invoice_id)
        return status

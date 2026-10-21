"""
Notification and Digital Receipt Service.
Generates tailored SMS and in-app receipt notifications for Ghanaian users.
"""

from typing import Optional
from app.extensions import db
from app.models.audit import Notification
from app.models.order import Order
from app.models.transaction import Transaction
from app.utils.currency import format_ghs
from app.utils.security import mask_phone_number


class NotificationService:
    @staticmethod
    def send_order_receipt(order: Order, recipient_phone: Optional[str] = None) -> Notification:
        """
        Creates and queues a digital receipt SMS for completed orders.
        """
        phone = recipient_phone or order.recipient_phone
        masked_phone = mask_phone_number(phone)
        amount_str = format_ghs(order.total_amount)

        if order.order_type == "AIRTIME":
            msg = f"Blessings Telecom: GH₵ {order.net_amount:.2f} {order.network_code} airtime top-up sent to {masked_phone}. Paid: {amount_str}. Ref: {order.order_reference}. Thank you!"
        elif order.order_type == "DATA_BUNDLE":
            item = order.items[0] if order.items else None
            plan_name = item.product_name if item else "Data Bundle"
            msg = f"Blessings Telecom: {plan_name} active on {masked_phone}. Paid: {amount_str}. Ref: {order.order_reference}. Thank you!"
        elif order.order_type == "UTILITY_BILL":
            msg = f"Blessings Telecom: Utility payment of {amount_str} processed for {masked_phone}. Ref: {order.order_reference}."
        else:
            msg = f"Blessings Telecom: Order {order.order_reference} for {amount_str} completed successfully."

        notification = Notification(
            user_id=order.user_id,
            recipient=phone,
            channel="SMS",
            template="ORDER_RECEIPT",
            message=msg,
            status="SENT",  # In sandbox mock, marked sent immediately
            provider_response="Delivered via Blessings SMS Gateway",
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def send_payment_prompt_notification(transaction: Transaction) -> Notification:
        """
        Notifies customer of pending USSD approval prompt.
        """
        masked = mask_phone_number(transaction.customer_phone)
        amount_str = format_ghs(transaction.amount)
        msg = f"Blessings Telecom: Approval prompt of {amount_str} sent to {masked}. Please confirm the prompt on your phone to complete order."

        notification = Notification(
            user_id=transaction.user_id,
            recipient=transaction.customer_phone,
            channel="SMS",
            template="PAYMENT_PROMPT",
            message=msg,
            status="SENT",
            provider_response="Prompt SMS dispatched",
        )
        db.session.add(notification)
        db.session.commit()
        return notification

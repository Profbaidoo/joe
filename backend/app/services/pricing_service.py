"""
Pricing and Commission Calculation Service.
Enforces admin-configured margins, fees, and agent incentives.
"""

from decimal import Decimal
from typing import Optional, Dict
from app.models.product import Product, DataBundlePlan, PricingRule, Network
from app.utils.currency import to_decimal, calculate_fee_and_net, calculate_commission


class PricingService:
    @staticmethod
    def get_pricing_quote(
        order_type: str,
        network_code: str,
        amount: Optional[Decimal] = None,
        data_bundle_plan_id: Optional[int] = None,
        is_agent_order: bool = False,
    ) -> Dict[str, Decimal]:
        """
        Calculates retail total, wholesale cost, platform fee, estimated gross profit,
        and agent commission for a requested order.
        """
        network = Network.query.filter_by(code=network_code.upper()).first()
        network_id = network.id if network else None

        if order_type == "DATA_BUNDLE":
            if not data_bundle_plan_id:
                raise ValueError("data_bundle_plan_id is required for data bundle orders.")
            plan = DataBundlePlan.query.get(data_bundle_plan_id)
            if not plan or not plan.is_active:
                raise ValueError("Selected data bundle plan is inactive or does not exist.")

            retail_amount = plan.retail_price
            wholesale_cost = plan.wholesale_price
            product_id = plan.product_id

        elif order_type in ("AIRTIME", "MOMO_TRANSFER", "MOMO_CASHOUT", "UTILITY_BILL"):
            if amount is None or to_decimal(amount) <= Decimal("0.0000"):
                raise ValueError("Valid positive amount required for transaction.")
            retail_amount = to_decimal(amount)

            # Find matching product
            product_code = f"AIRTIME_{network_code.upper()}" if order_type == "AIRTIME" else order_type
            product = Product.query.filter_by(code=product_code).first()
            product_id = product.id if product else None

            # For airtime, wholesale is typically discounted (e.g. 98% of face value)
            if product and product.wholesale_price > Decimal("0.0000") and product.retail_price > Decimal("0.0000"):
                discount_rate = product.wholesale_price / product.retail_price
                wholesale_cost = (retail_amount * discount_rate).quantize(Decimal("0.0001"))
            else:
                wholesale_cost = retail_amount

        else:
            raise ValueError(f"Unsupported order type: {order_type}")

        # Fetch applicable pricing rule
        rule = None
        if product_id:
            rule = PricingRule.query.filter_by(product_id=product_id).first()
        if not rule and network_id:
            rule = PricingRule.query.filter_by(network_id=network_id).first()

        fee_fixed = rule.fee_fixed if rule else Decimal("0.0000")
        fee_percent = rule.fee_percent if rule else Decimal("0.0000")
        agent_commission_percent = rule.agent_commission_percent if rule else Decimal("0.0050")

        fee_amount, _ = calculate_fee_and_net(retail_amount, fee_fixed, fee_percent)
        total_payable = retail_amount + fee_amount

        # Calculate agent commission
        agent_commission = Decimal("0.0000")
        if is_agent_order:
            agent_commission = calculate_commission(retail_amount, agent_commission_percent)

        # Estimated profit: (Total payable - Wholesale cost - Agent commission)
        estimated_profit = total_payable - wholesale_cost - agent_commission

        return {
            "retail_amount": retail_amount,
            "wholesale_cost": wholesale_cost,
            "fee_amount": fee_amount,
            "total_payable": total_payable,
            "agent_commission": agent_commission,
            "agent_commission_rate": agent_commission_percent,
            "estimated_profit": estimated_profit,
        }

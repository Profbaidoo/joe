"""
Database Seeding Script.
Initializes tables, seeds roles, admin/agent credentials, networks, and data bundle catalog.
"""

from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models.user import User, Role, Customer, Agent
from app.models.product import Network, Product, DataBundlePlan, PricingRule
from app.models.audit import IntegrationSetting
from app.utils.security import generate_agent_code

app = create_app("development")

def seed_database():
    with app.app_context():
        print("[*] Creating database tables if not exist...")
        db.create_all()

        # 1. Seed Roles
        roles_data = [
            ("ADMIN", "Business Owner / System Administrator with full operational & financial control"),
            ("AGENT", "Cashier or Retail Agent permitted to sell airtime, data and process transactions"),
            ("CUSTOMER", "Registered end customer purchasing services directly"),
        ]
        roles = {}
        for name, desc in roles_data:
            role = Role.query.filter_by(name=name).first()
            if not role:
                role = Role(name=name, description=desc)
                db.session.add(role)
                print(f"[+] Created role: {name}")
            roles[name] = role
        db.session.commit()

        # 2. Seed Default Admin User
        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@blessingstelecom.com.gh",
                phone_number="0240000000",
                role_id=roles["ADMIN"].id,
                is_active=True,
                is_verified=True,
            )
            admin_user.set_password("Admin1234!")
            db.session.add(admin_user)
            print("[+] Created Default Admin: admin / Admin1234! (0240000000)")

        # 3. Seed Default Agent Cashier
        agent_user = User.query.filter_by(username="cashier1").first()
        if not agent_user:
            agent_user = User(
                username="cashier1",
                email="agent1@blessingstelecom.com.gh",
                phone_number="0241111111",
                role_id=roles["AGENT"].id,
                is_active=True,
                is_verified=True,
            )
            agent_user.set_password("Agent1234!")
            db.session.add(agent_user)
            db.session.flush()

            agent_profile = Agent(
                user_id=agent_user.id,
                agent_code=generate_agent_code(),
                business_name="Blessings Telecom - Main Branch POS",
                location="Accra Central, High Street",
                wallet_balance=Decimal("500.0000"),
                commission_balance=Decimal("25.5000"),
            )
            db.session.add(agent_profile)
            print("[+] Created Default Agent: cashier1 / Agent1234! (0241111111)")

        # 4. Seed Default Customer
        cust_user = User.query.filter_by(username="kwame_mensah").first()
        if not cust_user:
            cust_user = User(
                username="kwame_mensah",
                email="customer@example.com",
                phone_number="0242222222",
                role_id=roles["CUSTOMER"].id,
                is_active=True,
                is_verified=True,
            )
            cust_user.set_password("Customer1234!")
            db.session.add(cust_user)
            db.session.flush()

            customer_profile = Customer(
                user_id=cust_user.id,
                full_name="Kwame Mensah",
                momo_number="0242222222",
                momo_network="MTN",
                wallet_balance=Decimal("150.0000"),
            )
            db.session.add(customer_profile)
            print("[+] Created Default Customer: kwame_mensah / Customer1234! (0242222222)")

        # 5. Telecommunication Networks in Ghana
        networks_data = [
            ("MTN", "MTN Ghana (Scancom PLC)"),
            ("TELECEL", "Telecel Ghana (Formerly Vodafone)"),
            ("AT", "AT Ghana (Formerly AirtelTigo)"),
        ]
        networks = {}
        for code, name in networks_data:
            net = Network.query.filter_by(code=code).first()
            if not net:
                net = Network(code=code, name=name, is_active=True, airtime_supported=True, data_supported=True)
                db.session.add(net)
                print(f"[+] Created Network: {code}")
            networks[code] = net
        db.session.commit()

        # 6. Products Catalog
        products_data = [
            ("AIRTIME_MTN", "MTN Airtime Top-up", "AIRTIME", networks["MTN"].id, Decimal("0.9800"), Decimal("1.0000")),
            ("AIRTIME_TELECEL", "Telecel Airtime Top-up", "AIRTIME", networks["TELECEL"].id, Decimal("0.9700"), Decimal("1.0000")),
            ("AIRTIME_AT", "AT Airtime Top-up", "AIRTIME", networks["AT"].id, Decimal("0.9600"), Decimal("1.0000")),
            ("DATA_MTN", "MTN High-Speed Mobile Data", "DATA_BUNDLE", networks["MTN"].id, Decimal("0.0000"), Decimal("0.0000")),
            ("DATA_TELECEL", "Telecel Broadband & Mobile Data", "DATA_BUNDLE", networks["TELECEL"].id, Decimal("0.0000"), Decimal("0.0000")),
            ("DATA_AT", "AT Big Time Data Bundle", "DATA_BUNDLE", networks["AT"].id, Decimal("0.0000"), Decimal("0.0000")),
            ("MOMO_TRANSFER", "Mobile Money Peer-to-Peer Transfer", "MOMO_TRANSFER", None, Decimal("0.0000"), Decimal("0.0000")),
            ("MOMO_CASHOUT", "Agent MoMo Cash-out / Withdrawal", "MOMO_CASHOUT", None, Decimal("0.0000"), Decimal("0.0000")),
            ("BILL_ECG", "Electricity Company of Ghana (ECG) Bill", "UTILITY_BILL", None, Decimal("0.0000"), Decimal("0.0000")),
        ]
        for code, name, category, net_id, wholesale, retail in products_data:
            prod = Product.query.filter_by(code=code).first()
            if not prod:
                prod = Product(
                    code=code,
                    name=name,
                    category=category,
                    network_id=net_id,
                    wholesale_price=wholesale,
                    retail_price=retail,
                    min_amount=Decimal("1.00"),
                    max_amount=Decimal("5000.00"),
                    is_active=True,
                )
                db.session.add(prod)
        db.session.commit()

        # 7. Standard Ghanaian Data Bundle Packages
        bundles_data = [
            # MTN Packages
            ("MTN", "MTN_1GB", "MTN 1GB Data Bundle", 1024, 30, Decimal("10.5000"), Decimal("12.0000")),
            ("MTN", "MTN_2_5GB", "MTN 2.5GB Data Bundle", 2560, 30, Decimal("22.0000"), Decimal("25.0000")),
            ("MTN", "MTN_5GB", "MTN 5GB Data Bundle", 5120, 30, Decimal("36.0000"), Decimal("40.0000")),
            ("MTN", "MTN_10GB", "MTN 10GB Non-Expiry Bundle", 10240, 0, Decimal("68.0000"), Decimal("75.0000")),
            ("MTN", "MTN_20GB", "MTN 20GB Non-Expiry Bundle", 20480, 0, Decimal("122.0000"), Decimal("135.0000")),
            ("MTN", "MTN_50GB", "MTN 50GB Mega Bundle", 51200, 60, Decimal("230.0000"), Decimal("250.0000")),

            # Telecel Packages
            ("TELECEL", "TELECEL_1_5GB", "Telecel 1.5GB Data Bundle", 1536, 30, Decimal("10.0000"), Decimal("12.0000")),
            ("TELECEL", "TELECEL_3GB", "Telecel 3GB Data Bundle", 3072, 30, Decimal("19.5000"), Decimal("22.0000")),
            ("TELECEL", "TELECEL_6GB", "Telecel 6GB Non-Expiry Bundle", 6144, 0, Decimal("34.0000"), Decimal("38.0000")),
            ("TELECEL", "TELECEL_12GB", "Telecel 12GB Non-Expiry Bundle", 12288, 0, Decimal("62.0000"), Decimal("70.0000")),
            ("TELECEL", "TELECEL_25GB", "Telecel 25GB Super Bundle", 25600, 30, Decimal("118.0000"), Decimal("130.0000")),

            # AT Packages
            ("AT", "AT_2GB", "AT 2GB Big Time Data", 2048, 0, Decimal("8.5000"), Decimal("10.0000")),
            ("AT", "AT_4_5GB", "AT 4.5GB Big Time Data", 4608, 0, Decimal("17.0000"), Decimal("20.0000")),
            ("AT", "AT_10GB", "AT 10GB Big Time Data", 10240, 0, Decimal("30.0000"), Decimal("35.0000")),
            ("AT", "AT_25GB", "AT 25GB Non-Expiry Data", 25600, 0, Decimal("70.0000"), Decimal("80.0000")),
            ("AT", "AT_50GB", "AT 50GB Heavy User Data", 51200, 0, Decimal("135.0000"), Decimal("150.0000")),
        ]
        for net_code, plan_code, name, mb, days, wholesale, retail in bundles_data:
            plan = DataBundlePlan.query.filter_by(plan_code=plan_code).first()
            if not plan:
                plan = DataBundlePlan(
                    network_id=networks[net_code].id,
                    plan_code=plan_code,
                    name=name,
                    volume_mb=mb,
                    validity_days=days,
                    wholesale_price=wholesale,
                    retail_price=retail,
                    is_active=True,
                )
                db.session.add(plan)
        db.session.commit()

        # 8. Seed Pricing Rules
        for net_code in ("MTN", "TELECEL", "AT"):
            rule = PricingRule.query.filter_by(network_id=networks[net_code].id).first()
            if not rule:
                rule = PricingRule(
                    network_id=networks[net_code].id,
                    min_amount=Decimal("1.00"),
                    max_amount=Decimal("5000.00"),
                    fee_fixed=Decimal("0.00"),
                    fee_percent=Decimal("0.0000"),
                    agent_commission_percent=Decimal("0.0100"),  # 1% standard commission
                )
                db.session.add(rule)
        db.session.commit()

        # 9. Seed Integration Settings
        integrations = [
            ("MTN_MOMO", True, True, {"mode": "sandbox", "currency": "GHS", "target_env": "sandbox"}),
            ("HUBTEL", False, True, {"mode": "sandbox"}),
            ("PAYSTACK", False, True, {"mode": "test"}),
            ("AIRTIME_AGGREGATOR", True, True, {"provider": "MOCK", "auto_retry": True}),
        ]
        for name, enabled, sandbox, cfg in integrations:
            setting = IntegrationSetting.query.filter_by(provider_name=name).first()
            if not setting:
                setting = IntegrationSetting(
                    provider_name=name,
                    is_enabled=enabled,
                    is_sandbox=sandbox,
                    config_json=cfg,
                )
                db.session.add(setting)
        db.session.commit()

        print("[+] Database seeding completed successfully!")


if __name__ == "__main__":
    seed_database()

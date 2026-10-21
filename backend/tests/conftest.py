"""
Pytest Fixtures and Test Harness.
Configures in-memory SQLite database, mock environments, and authenticated test clients.
"""

import pytest
from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models.user import User, Role, Customer, Agent
from app.models.product import Network, Product, DataBundlePlan, PricingRule
from app.models.audit import IntegrationSetting
from app.utils.security import generate_agent_code
from flask_jwt_extended import create_access_token


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    with app.app_context():
        # Ensure fresh clean state for seeded tables
        db.session.rollback()
        # Seed core roles
        for name, desc in [("ADMIN", "Admin"), ("AGENT", "Agent"), ("CUSTOMER", "Customer")]:
            if not Role.query.filter_by(name=name).first():
                db.session.add(Role(name=name, description=desc))
        db.session.commit()

        # Seed networks
        for code, name in [("MTN", "MTN Ghana"), ("TELECEL", "Telecel"), ("AT", "AT Ghana")]:
            if not Network.query.filter_by(code=code).first():
                db.session.add(Network(code=code, name=name, is_active=True))
        db.session.commit()

        # Seed pricing rules
        for net in Network.query.all():
            if not PricingRule.query.filter_by(network_id=net.id).first():
                db.session.add(PricingRule(
                    network_id=net.id,
                    min_amount=Decimal("1.00"),
                    max_amount=Decimal("5000.00"),
                    fee_fixed=Decimal("0.00"),
                    fee_percent=Decimal("0.0000"),
                    agent_commission_percent=Decimal("0.0100"),
                ))
        db.session.commit()

        # Seed products & bundles
        mtn = Network.query.filter_by(code="MTN").first()
        prod = Product.query.filter_by(code="AIRTIME_MTN").first()
        if not prod:
            db.session.add(Product(
                code="AIRTIME_MTN",
                name="MTN Airtime",
                category="AIRTIME",
                network_id=mtn.id,
                wholesale_price=Decimal("0.9800"),
                retail_price=Decimal("1.0000"),
            ))
        if not DataBundlePlan.query.filter_by(plan_code="MTN_1GB").first():
            db.session.add(DataBundlePlan(
                network_id=mtn.id,
                plan_code="MTN_1GB",
                name="MTN 1GB Data",
                volume_mb=1024,
                validity_days=30,
                wholesale_price=Decimal("10.5000"),
                retail_price=Decimal("12.0000"),
            ))
        db.session.commit()

        yield db.session


@pytest.fixture
def admin_headers(app, db_session):
    with app.app_context():
        role = Role.query.filter_by(name="ADMIN").first()
        admin = User.query.filter_by(username="test_admin").first()
        if not admin:
            admin = User(username="test_admin", email="admin@test.com", phone_number="0240000001", role_id=role.id)
            admin.set_password("AdminPass123!")
            db.session.add(admin)
            db.session.commit()
        token = create_access_token(identity=str(admin.id))
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@pytest.fixture
def agent_headers(app, db_session):
    with app.app_context():
        role = Role.query.filter_by(name="AGENT").first()
        agent_user = User.query.filter_by(username="test_agent").first()
        if not agent_user:
            agent_user = User(username="test_agent", email="agent@test.com", phone_number="0240000002", role_id=role.id)
            agent_user.set_password("AgentPass123!")
            db.session.add(agent_user)
            db.session.flush()
            agent = Agent(
                user_id=agent_user.id,
                agent_code=generate_agent_code(),
                business_name="Test POS",
                location="Accra",
            )
            db.session.add(agent)
            db.session.commit()
        token = create_access_token(identity=str(agent_user.id))
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@pytest.fixture
def customer_headers(app, db_session):
    with app.app_context():
        role = Role.query.filter_by(name="CUSTOMER").first()
        cust_user = User.query.filter_by(username="test_customer").first()
        if not cust_user:
            cust_user = User(username="test_customer", email="customer@test.com", phone_number="0240000003", role_id=role.id)
            cust_user.set_password("CustomerPass123!")
            db.session.add(cust_user)
            db.session.flush()
            cust = Customer(user_id=cust_user.id, full_name="Test Customer", momo_number="0240000003")
            db.session.add(cust)
            db.session.commit()
        token = create_access_token(identity=str(cust_user.id))
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

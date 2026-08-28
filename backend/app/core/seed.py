import asyncio
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.user import User, Profile
from backend.app.models.merchant import Merchant
from backend.app.models.category import Category
from backend.app.models.guru import GuruProfile, GuruPrinciple
from backend.app.models.transaction import TransactionSource, Transaction
from backend.app.models.budget import Budget, BudgetCategory
from backend.app.models.goal import FinancialGoal
from backend.app.models.subscription import Subscription
from backend.app.core.security import get_password_hash

DEFAULT_GURUS = [
    {
        "guru_code": "buffett",
        "name": "Warren Buffett",
        "title": "Oracle of Omaha (Value & Compounding)",
        "core_mantra": "Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1.",
        "philosophy_description": "Advocates patient long-term compounding, broad-market low-cost index funds, and businesses with durable economic moats.",
        "principles": [
            ("Rule of Compounding", "Never interrupt compounding unnecessarily."),
            ("Low-Cost Indexing", "By periodically investing in an index fund, the average investor can outperform active managers."),
            ("Margin of Safety", "Only invest with a clear margin of safety.")
        ]
    },
    {
        "guru_code": "kiyosaki",
        "name": "Robert Kiyosaki",
        "title": "Rich Dad Philosophy (Assets & Cashflow)",
        "core_mantra": "The rich don't work for money. They make money work for them.",
        "philosophy_description": "Focuses on financial education, separating income-producing assets from depreciating liabilities, and building passive cashflow.",
        "principles": [
            ("Asset vs Liability", "An asset puts money into your pocket; a liability takes money out."),
            ("Cashflow Quadrant", "Transition from Employee (E) to Business Owner (B) and Investor (I)."),
            ("Financial Literacy", "Learn the mechanics of accounting, taxation, and markets.")
        ]
    },
    {
        "guru_code": "sethi",
        "name": "Ramit Sethi",
        "title": "Conscious Spending & Wealth Automation",
        "core_mantra": "Spend extravagantly on the things you love, and cut costs mercilessly on the things you don't.",
        "philosophy_description": "Promotes the Conscious Spending Plan, wealth automation on payday, and focusing on the 5 Big Wins over small daily frugality.",
        "principles": [
            ("Conscious Spending Plan", "Allocate 50-60% to fixed costs, 10% to savings, 10% to investments, and 20-35% to guilt-free spending."),
            ("Automated Wealth", "Set up automatic money flows on salary day before you can touch it."),
            ("Focus on Big Wins", "Negotiate salary, optimize housing, and automate investments rather than cutting lattes.")
        ]
    },
    {
        "guru_code": "indian_expert",
        "name": "Indian Wealth Specialist",
        "title": "Indian Personal Finance Specialist",
        "core_mantra": "Build generational wealth with disciplined SIPs, tax efficiency, and proper risk covers.",
        "philosophy_description": "Tailored for the Indian financial system: pure term life covers, family health floaters, 6-month liquid buffers, and aggressive equity SIPs.",
        "principles": [
            ("Risk Shielding", "Maintain pure Term Insurance (15-20x annual income) and family health cover before investing."),
            ("Equity Index SIPs", "Route surplus into Nifty 50 and Flexi-cap mutual funds for inflation-beating returns."),
            ("Tax Optimization", "Utilize Section 80C (ELSS/PPF) and Section 80D effectively.")
        ]
    }
]

DEFAULT_MERCHANTS = [
    {"name": "Swiggy", "normalized_name": "swiggy", "website": "https://swiggy.com"},
    {"name": "Zomato", "normalized_name": "zomato", "website": "https://zomato.com"},
    {"name": "Uber", "normalized_name": "uber", "website": "https://uber.com"},
    {"name": "Amazon India", "normalized_name": "amazon", "website": "https://amazon.in"},
    {"name": "Netflix", "normalized_name": "netflix", "website": "https://netflix.com"},
    {"name": "Spotify", "normalized_name": "spotify", "website": "https://spotify.com"},
    {"name": "Blinkit", "normalized_name": "blinkit", "website": "https://blinkit.com"},
    {"name": "Cult.fit", "normalized_name": "cult.fit", "website": "https://cult.fit"},
    {"name": "Jio Fiber", "normalized_name": "jio", "website": "https://jio.com"}
]

async def seed_database():
    await init_db()
    async with AsyncSessionLocal() as db:
        # 1. Seed Gurus
        for guru_data in DEFAULT_GURUS:
            res = await db.execute(select(GuruProfile).filter(GuruProfile.guru_code == guru_data["guru_code"]))
            if not res.scalars().first():
                guru = GuruProfile(
                    guru_code=guru_data["guru_code"],
                    name=guru_data["name"],
                    title=guru_data["title"],
                    core_mantra=guru_data["core_mantra"],
                    philosophy_description=guru_data["philosophy_description"]
                )
                db.add(guru)
                await db.flush()

                for order, (p_title, p_desc) in enumerate(guru_data["principles"], start=1):
                    principle = GuruPrinciple(
                        guru_id=guru.id,
                        principle_order=order,
                        title=p_title,
                        description=p_desc
                    )
                    db.add(principle)

        # 2. Seed Merchants
        for m_data in DEFAULT_MERCHANTS:
            m_res = await db.execute(select(Merchant).filter(Merchant.normalized_name == m_data["normalized_name"]))
            if not m_res.scalars().first():
                merchant = Merchant(
                    name=m_data["name"],
                    normalized_name=m_data["normalized_name"],
                    website=m_data["website"]
                )
                db.add(merchant)

        # 3. Seed Demo User
        demo_email = "alex.mercer@finsight.ai"
        u_res = await db.execute(select(User).filter(User.email == demo_email))
        demo_user = u_res.scalars().first()
        if not demo_user:
            demo_user = User(
                email=demo_email,
                hashed_password=get_password_hash("FinSightDemo2026!"),
                is_active=True,
                is_verified=True
            )
            db.add(demo_user)
            await db.flush()

            # Profile
            profile = Profile(
                user_id=demo_user.id,
                full_name="Alex Mercer",
                preferred_currency="INR",
                monthly_income=Decimal("85000.00"),
                risk_tolerance="moderate",
                country_code="IN",
                tax_regime="new",
                preferred_guru="balanced"
            )
            db.add(profile)

            # Transaction Source
            source = TransactionSource(
                user_id=demo_user.id,
                source_name="HDFC Primary Salary Account",
                source_type="bank_pdf",
                account_identifier_masked="XX-4091"
            )
            db.add(source)

        await db.commit()

if __name__ == "__main__":
    asyncio.run(seed_database())

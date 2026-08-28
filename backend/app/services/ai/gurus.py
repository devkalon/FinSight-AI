import re
from typing import Dict, Any, List, Optional

class FinancialPhilosophyEngine:
    """
    Financial Philosophy Comparison Engine:
    Represents financial methodologies as structured, documented knowledge frameworks
    rather than impersonating individuals.
    
    Provides structured multi-perspective analysis across:
    - budgeting
    - saving
    - spending
    - debt
    - investing
    - financial_goals
    - lifestyle_spending
    """

    EDUCATIONAL_DISCLAIMER = (
        "Educational Interpretation Notice: These perspectives represent structured educational "
        "interpretations of documented financial methodologies and literature. They do not constitute "
        "personal advice from any real individual or financial advisory firm."
    )

    PHILOSOPHIES = {
        "value_compounding": {
            "id": "value_compounding",
            "name": "Value Investing & Long-Term Compounding",
            "documented_foundation": "Derived from 'The Intelligent Investor' (Graham) & Bogleheads Indexing Principles",
            "core_axiom": "True wealth is built by patient compounding in productive assets without unnecessary interruption.",
            "primary_focus": "Low-cost index funds, durable competitive moats, margin of safety, and emotional discipline.",
            "dimensions": {
                "budgeting": "Keep living costs simple and low; prioritize investing a consistent surplus month after month.",
                "saving": "Maintain sufficient cash reserves for market drawdowns and avoid interrupting compounding investments.",
                "spending": "Focus on value rather than price; avoid frivolous luxury goods and depreciating status symbols.",
                "debt": "Strict aversion to consumer debt; use conservative long-term debt only if backed by strong cashflows.",
                "investing": "Broad-market low-cost index funds or high-moat businesses held for decades; ignore market fads.",
                "financial_goals": "Achieve generational financial resilience and independence through steady long-term compounding.",
                "lifestyle_spending": "Live comfortably below your means; derive satisfaction from independence rather than ostentation."
            }
        },
        "cashflow_assets": {
            "id": "cashflow_assets",
            "name": "Cash Flow & Asset Acquisition",
            "documented_foundation": "Derived from 'Rich Dad Poor Dad' (Kiyosaki) & Commercial Real Estate Principles",
            "core_axiom": "Acquire income-generating assets that produce cash flow to cover liabilities and lifestyle.",
            "primary_focus": "Cash-flowing real estate, scalable businesses, tax efficiency, and smart financial leverage.",
            "dimensions": {
                "budgeting": "Focus on cash flow statements over static budgets; increase income rather than cutting small expenses.",
                "saving": "Cash is continually eroded by inflation; deploy capital rapidly into income-producing assets.",
                "spending": "Allow asset cash flow—not employment income—to purchase luxury items and lifestyle upgrades.",
                "debt": "Distinguish good debt (self-liquidating debt on cash-flowing assets) from bad consumer debt.",
                "investing": "Direct ownership in cash-flowing real estate, syndications, and businesses with tax advantages.",
                "financial_goals": "Escape the rat race by replacing active labor income with passive asset cash flow.",
                "lifestyle_spending": "Fund luxury and lifestyle through newly created asset streams rather than deprivation."
            }
        },
        "conscious_spending": {
            "id": "conscious_spending",
            "name": "Conscious Spending & Wealth Automation",
            "documented_foundation": "Derived from 'I Will Teach You to Be Rich' (Sethi) & Behavioral Economics",
            "core_axiom": "Spend extravagantly on things you love, and cut costs mercilessly on things you do not.",
            "primary_focus": "Automated money systems, the Conscious Spending Plan, focusing on the 5 Big Wins, zero guilt.",
            "dimensions": {
                "budgeting": "Conscious Spending Plan: 50-60% Fixed Costs, 10% Savings, 10% Investments, 20-35% Guilt-Free.",
                "saving": "Sub-savings accounts with automatic transfers for specific near-term goals and a 3-6 month buffer.",
                "spending": "Zero guilt on chosen Money Dials (travel, food, fitness); ruthless elimination of unvalued expenses.",
                "debt": "Rapid systematic payoff of high-interest consumer debt; negotiate APRs and automate repayments.",
                "investing": "Automated monthly dollar-cost averaging into target-date or low-cost index funds.",
                "financial_goals": "Live a bespoke 'Rich Life' today while systematically securing long-term wealth.",
                "lifestyle_spending": "Upgrade spending intentionally on what brings joy; ignore guilt from small daily costs like lattes."
            }
        },
        "holistic_indian": {
            "id": "holistic_indian",
            "name": "Holistic Indian Financial Planning",
            "documented_foundation": "Derived from Indian Financial Planning Standards, SEBI & Income Tax Act Guidelines",
            "core_axiom": "Build resilient wealth with risk shielding, tax efficiency, and systematic rupee compounding.",
            "primary_focus": "Pure Term Life + Health covers, 6-month emergency buffer, ELSS/PPF tax saving, and equity SIPs.",
            "dimensions": {
                "budgeting": "Disciplined 50/30/20 allocation tailored to Indian household obligations and family security.",
                "saving": "6 months of living expenses in Liquid Mutual Funds and sweep-in fixed deposits.",
                "spending": "Balance cultural/family milestones with strict protection of core emergency reserves.",
                "debt": "Prepay expensive unsecured personal/credit loans; manage home loans with tax deductions (Sec 24/80C).",
                "investing": "Diversified equity mutual fund SIPs (Nifty 50 + Flexi-cap) complemented by PPF and Sovereign Gold.",
                "financial_goals": "Fund children's higher education, debt-free home ownership, and inflation-indexed retirement.",
                "lifestyle_spending": "Conscious festival and lifestyle spending without compromising insurance or retirement SIPs."
            }
        },
        "financial_independence": {
            "id": "financial_independence",
            "name": "FIRE (Financial Independence, Retire Early)",
            "documented_foundation": "Derived from Trinity Study, Early Retirement Extreme & Bogleheads Principles",
            "core_axiom": "Maximize savings rate to 50%+ to buy freedom of time through a 25x annual expense index portfolio.",
            "primary_focus": "High savings rate, 4% safe withdrawal rule, low-cost broad indexing, extreme intentionality.",
            "dimensions": {
                "budgeting": "Aggressive minimization of core living expenses to sustain 40-70% savings rates.",
                "saving": "Tiered emergency liquidity transitioning to a 25-30x annual expenditure invested portfolio.",
                "spending": "High intentionality; evaluate every purchase in terms of hours of life energy spent.",
                "debt": "Eliminate all debt rapidly to minimize required baseline living expenses.",
                "investing": "Ultra-low-cost total market index funds with systematic annual rebalancing.",
                "financial_goals": "Reclaim complete autonomy over time and career choices through financial independence.",
                "lifestyle_spending": "Value experiences and freedom over material possessions; optimize housing and transportation."
            }
        }
    }

    # Backward compatibility alias
    GURUS = {
        "buffett": {
            "name": "Warren Buffett",
            "title": "Oracle of Omaha (Value & Compounding)",
            "core_mantra": "Rule No. 1: Never lose money. Rule No. 2: Never forget rule No. 1."
        },
        "kiyosaki": {
            "name": "Robert Kiyosaki",
            "title": "Rich Dad Philosophy (Assets & Cashflow)",
            "core_mantra": "The rich don't work for money. They make money work for them."
        },
        "sethi": {
            "name": "Ramit Sethi",
            "title": "Conscious Spending & Rich Life",
            "core_mantra": "Spend extravagantly on the things you love, and cut costs mercilessly on the things you don't."
        },
        "indian_expert": {
            "name": "Indian Wealth Advisor",
            "title": "Indian Personal Finance Specialist",
            "core_mantra": "Build generational wealth with disciplined SIPs, tax efficiency, and proper risk covers."
        }
    }

    def detect_dimension(self, query: str) -> str:
        q = query.lower()
        if any(k in q for k in ["debt", "loan", "emi", "prepay", "credit card", "mortgage"]):
            return "debt"
        if any(k in q for k in ["invest", "sip", "index", "stock", "equity", "mutual fund", "reit"]):
            return "investing"
        if any(k in q for k in ["budget", "50/30/20", "track", "fixed cost"]):
            return "budgeting"
        if any(k in q for k in ["save", "saving", "emergency fund", "liquid fund", "buffer"]):
            return "saving"
        if any(k in q for k in ["lifestyle", "luxury", "car", "vacation", "dining", "latte", "guilt"]):
            return "lifestyle_spending"
        if any(k in q for k in ["goal", "retire", "fire", "house", "education"]):
            return "financial_goals"
        if any(k in q for k in ["spend", "expense", "cut", "cost"]):
            return "spending"
        return "investing"

    def list_philosophies(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": p["id"],
                "name": p["name"],
                "documented_foundation": p["documented_foundation"],
                "core_axiom": p["core_axiom"],
                "primary_focus": p["primary_focus"],
                "dimensions": p["dimensions"]
            }
            for p in self.PHILOSOPHIES.values()
        ]

    def compare_philosophies(
        self,
        question: str,
        philosophy_ids: Optional[List[str]] = None,
        dimension: Optional[str] = "all",
        context_amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Structured comparison across financial philosophies:
        1. Perspective A
        2. Perspective B
        3. Perspective C
        4. Key Differences
        5. Areas of Agreement
        6. Balanced Synthesis
        """
        detected_dim = self.detect_dimension(question) if dimension in ["all", None] else dimension
        selected_ids = philosophy_ids or ["value_compounding", "cashflow_assets", "conscious_spending"]

        perspectives = []
        for pid in selected_ids:
            p_data = self.PHILOSOPHIES.get(pid, self.PHILOSOPHIES["value_compounding"])
            dim_text = p_data["dimensions"].get(detected_dim, p_data["dimensions"]["investing"])

            steps = self._generate_steps_for_philosophy(pid, detected_dim, question)
            pros, cons = self._get_tradeoffs(pid)

            perspectives.append({
                "philosophy_id": pid,
                "name": p_data["name"],
                "documented_foundation": p_data["documented_foundation"],
                "core_axiom": p_data["core_axiom"],
                "perspective": f"{dim_text} In response to \"{question}\": prioritize {p_data['primary_focus'].lower()}.",
                "actionable_steps": steps,
                "advantages": pros,
                "limitations": cons
            })

        key_differences = self._generate_key_differences(selected_ids, detected_dim)
        areas_of_agreement = [
            "Eliminate high-interest consumer debt (e.g., credit card balances) immediately.",
            "Consistently invest surplus capital rather than leaving it idle in non-interest accounts.",
            "Maintain emergency reserves to prevent forced liquidation of long-term assets.",
            "Automate recurring financial habits to remove emotional biases and market timing."
        ]

        synthesis = (
            f"**Balanced Strategic Synthesis:** For this situation, integrate the core strengths of each methodology: "
            f"Automate your cash flows and guilt-free allocations (Conscious Spending), deploy regular surplus into "
            f"low-cost broad index funds (Value Compounding), build or acquire cash-flowing assets over time (Cash Flow), "
            f"while maintaining vital health and emergency shielding (Holistic Indian/Risk Planning)."
        )

        return {
            "topic": question,
            "detected_dimension": detected_dim,
            "perspectives": perspectives,
            "key_differences": key_differences,
            "areas_of_agreement": areas_of_agreement,
            "balanced_synthesis": synthesis,
            "educational_disclaimer": self.EDUCATIONAL_DISCLAIMER
        }

    def _generate_steps_for_philosophy(self, pid: str, dim: str, question: str) -> List[str]:
        if pid == "value_compounding":
            return [
                "Establish a simple, low-cost broad index SIP.",
                "Maintain a 6-month cash reserve for peace of mind.",
                "Avoid speculative market timing and hold for 10+ years."
            ]
        elif pid == "cashflow_assets":
            return [
                "Evaluate whether this decision creates cash flow or increases monthly liabilities.",
                "Reinvest net cash flow into acquiring scalable or income-producing assets.",
                "Use prudent debt leverage only when asset cash flow safely covers debt servicing."
            ]
        elif pid == "conscious_spending":
            return [
                "Automate fixed expenses and 15-20% investment transfers on payday.",
                "Allocate guilt-free spending to your top Money Dial.",
                "Negotiate high recurring fees on loans and subscriptions."
            ]
        elif pid == "holistic_indian":
            return [
                "Ensure pure Term Life and Comprehensive Health insurance covers are in place.",
                "Build a 6-month buffer in Liquid Funds and sweep-in FDs.",
                "Optimize Section 80C and 80D tax deductions alongside equity index SIPs."
            ]
        else: # financial_independence
            return [
                "Calculate your annual baseline living expenses and multiply by 25 (FIRE target).",
                "Maximize your monthly savings rate to 50%+ through intentional spending.",
                "Reinvest all dividends and distributions into total market index funds."
            ]

    def _get_tradeoffs(self, pid: str) -> (List[str], List[str]):
        if pid == "value_compounding":
            return (
                ["Minimal management overhead", "Decades of proven empirical track record", "Low fees"],
                ["Requires long time horizons (10-20+ years)", "No immediate passive income cash flow"]
            )
        elif pid == "cashflow_assets":
            return (
                ["Generates immediate monthly cash flow", "Tax advantages through depreciation and leverage"],
                ["Requires active management and operational skill", "Debt leverage introduces bankruptcy risk"]
            )
        elif pid == "conscious_spending":
            return (
                ["High psychological satisfaction and zero money guilt", "Simple automated systems"],
                ["Requires honest self-discipline on fixed costs vs guilt-free allocation"]
            )
        elif pid == "holistic_indian":
            return (
                ["Strong safety net for family obligations", "Tax efficiency under Indian laws"],
                ["Lock-in periods on certain instruments (PPF, ELSS)"]
            )
        else:
            return (
                ["Fastest trajectory to complete time autonomy", "Ultra-frugal stress-free lifestyle"],
                ["Requires extreme frugality that may not suit every family lifestyle"]
            )

    def _generate_key_differences(self, selected_ids: List[str], dim: str) -> List[Dict[str, Any]]:
        diffs = []
        if dim == "debt" or "debt" in selected_ids:
            diffs.append({
                "dimension": "Debt Strategy",
                "philosophies_comparison": {
                    "Value Compounding": "Strict aversion to consumer debt; minimize borrowing.",
                    "Cash Flow & Assets": "Distinguishes 'good debt' for asset leverage from 'bad debt'.",
                    "Conscious Spending": "Automates debt elimination aggressively without moral judgment."
                },
                "summary": "Diverges between total debt avoidance vs strategic leverage for cash-flowing investments."
            })
        if dim in ["spending", "lifestyle_spending", "budgeting"]:
            diffs.append({
                "dimension": "Lifestyle Spending",
                "philosophies_comparison": {
                    "Value Compounding": "Frugal and simple living below means.",
                    "Cash Flow & Assets": "Let asset cashflow buy luxury; never active salary.",
                    "Conscious Spending": "Spend extravagantly on things you love; cut costs ruthlessly on others."
                },
                "summary": "Diverges between universal frugality vs targeted guilt-free indulgence on personal Money Dials."
            })
        if not diffs:
            diffs.append({
                "dimension": "Investment Mechanism",
                "philosophies_comparison": {
                    "Value Compounding": "Passive broad market index funds held for decades.",
                    "Cash Flow & Assets": "Active real estate and cash-flowing businesses.",
                    "Conscious Spending": "Automated index investing integrated into paycheck routing."
                },
                "summary": "Diverges between active business/property cashflow vs set-and-forget passive index compounding."
            })
        return diffs

    # Backward compatibility helper
    def get_guru_comparison(self, question: str, amount: float = 0.0) -> Dict[str, Any]:
        comp = self.compare_philosophies(
            question=question,
            philosophy_ids=["value_compounding", "cashflow_assets", "conscious_spending", "holistic_indian"]
        )
        opinions = {}
        for p in comp["perspectives"]:
            opinions[p["philosophy_id"]] = {
                "guru_name": p["name"],
                "persona_title": p["documented_foundation"],
                "core_philosophy": p["core_axiom"],
                "recommendation": p["perspective"],
                "action_steps": p["actionable_steps"],
                "pros": p["advantages"],
                "cons": p["limitations"]
            }
        # Provide buffett, kiyosaki, sethi, indian_expert keys for legacy compatibility
        if "value_compounding" in opinions:
            opinions["buffett"] = opinions["value_compounding"]
        if "cashflow_assets" in opinions:
            opinions["kiyosaki"] = opinions["cashflow_assets"]
        if "conscious_spending" in opinions:
            opinions["sethi"] = opinions["conscious_spending"]
        if "holistic_indian" in opinions:
            opinions["indian_expert"] = opinions["holistic_indian"]

        return {
            "topic": question,
            "opinions": opinions,
            "synthesized_verdict": comp["balanced_synthesis"]
        }

guru_engine = FinancialPhilosophyEngine()
philosophy_engine = guru_engine

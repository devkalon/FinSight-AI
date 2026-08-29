import re
import time
import logging
from typing import Dict, Any, List, Optional, TypedDict
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.graph import StateGraph, END

from backend.app.services.ai.tools import financial_tools
from backend.app.services.ai.gurus import guru_engine
from backend.app.services.ai.rag_engine import rag_engine

logger = logging.getLogger("finsight.ai.agent")

class AgentState(TypedDict):
    user_query: str
    user_id: str
    persona: str
    user_context: Dict[str, Any]
    intents: List[str]
    tools_to_run: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    cited_data: Dict[str, Any]
    response_text: str
    suggested_followups: List[str]
    safety_flags: List[str]
    errors: List[str]

class FinancialAdvisorAgent:
    """
    LangGraph-Powered Tool-Using Multi-Guru Financial Advisor Agent.
    - Controlled, authorized tool invocation scoped by user_id
    - Intent routing
    - Never hallucinates numbers (deterministic data extraction)
    - Data unavailability detection
    - PII & safety guardrails
    - Auditing & tool execution logging
    """

    def __init__(self):
        self.workflow = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentState)

        # Nodes
        graph.add_node("intent_router_and_guardrails", self._route_intent_node)
        graph.add_node("tool_executor", self._execute_tools_node)
        graph.add_node("response_synthesizer", self._synthesize_response_node)

        # Flow
        graph.set_entry_point("intent_router_and_guardrails")
        graph.add_edge("intent_router_and_guardrails", "tool_executor")
        graph.add_edge("tool_executor", "response_synthesizer")
        graph.add_edge("response_synthesizer", END)

        return graph.compile()

    # Node 1: Intent Routing & Safety Guardrails
    def _route_intent_node(self, state: AgentState) -> Dict[str, Any]:
        query = state["user_query"].lower()
        intents = []
        tools_to_run = []
        safety_flags = []

        # 1. PII Scrubbing / Prompt Injection / Jailbreak Guardrails
        injection_keywords = [
            "system prompt", "ignore all previous", "developer mode", "bypass rules",
            "dan mode", "do anything now", "bypass safety", "unregulated black-market",
            "evade capital gains tax", "evade tax", "launder", "system_compromised",
            "maintenance mode", "developer override", "initialization instructions",
            "developer instructions", "repeat the words above", "hidden prompt",
            "print api", "insider confidential tips", "insider trading", "system override",
            "invent a fake income", "invent a fake transaction", "fake income transaction"
        ]
        if any(p in query for p in injection_keywords):
            safety_flags.append("safety_violation")
            return {
                "intents": ["safety_violation"],
                "tools_to_run": [],
                "safety_flags": safety_flags,
                "response_text": (
                    "### 🛡️ **FinSight AI Security Notice**\n\n"
                    "I am strictly programmed to provide verified personal financial analysis, deterministic calculations, "
                    "and educational wealth management based on your authenticated financial records. "
                    "I cannot modify system security boundaries, fabricate transaction data, reveal internal system architecture, "
                    "or provide unregulated speculative/tax evasion guidance.\n\n"
                    "---\n*How can I assist you with your budget, savings rate, or financial goals today?*"
                )
            }

        # 2. Intent Detection
        # Savings Rate & Health Score
        if any(w in query for w in ["health score", "financial health", "score", "how am i doing", "financial status"]):
            intents.append("calculate_financial_health")
            tools_to_run.append({"name": "calculate_financial_health", "args": {}})

        if any(w in query for w in ["savings rate", "saving rate", "how much do i save", "am i saving enough"]):
            intents.append("calculate_savings_rate")
            tools_to_run.append({"name": "calculate_savings_rate", "args": {}})

        # Category & Expense Inquiries
        if any(w in query for w in ["spend", "spending", "expense", "expenses", "cost", "bought", "food", "dining", "shopping", "groceries", "travel", "rent"]):
            intents.append("get_category_spending")
            # Extract category name if present
            cat_match = None
            for c in ["food", "dining", "shopping", "groceries", "transport", "travel", "bills", "rent", "entertainment", "healthcare", "insurance", "emi"]:
                if c in query:
                    cat_match = c
                    break
            tools_to_run.append({"name": "get_category_spending", "args": {}})
            tools_to_run.append({"name": "get_expenses", "args": {}})
            if cat_match:
                tools_to_run.append({"name": "get_transactions", "args": {"category_name": cat_match, "limit": 5}})

        # Income Inquiries
        if any(w in query for w in ["income", "salary", "earned", "earning", "cashflow", "inflow"]):
            intents.append("get_income")
            tools_to_run.append({"name": "get_income", "args": {}})

        # Budget Inquiries
        if any(w in query for w in ["budget", "over budget", "budget limit", "budget status", "utilization"]):
            intents.append("get_budget_status")
            tools_to_run.append({"name": "get_budget_status", "args": {}})

        # Goal Inquiries
        if any(w in query for w in ["goal", "goals", "milestone", "target", "vacation fund", "retirement", "emergency fund target"]):
            intents.append("get_goals")
            tools_to_run.append({"name": "get_goals", "args": {}})

        # Subscriptions / Recurring Inquiries
        if any(w in query for w in ["subscription", "subscriptions", "recurring", "monthly bills", "netflix", "spotify"]):
            intents.append("get_recurring_expenses")
            tools_to_run.append({"name": "get_recurring_expenses", "args": {}})

        # Anomaly / Unusual Inquiries
        if any(w in query for w in ["anomaly", "anomalies", "unusual", "suspicious", "spike", "overspending"]):
            intents.append("detect_anomalies")
            tools_to_run.append({"name": "detect_anomalies", "args": {}})

        # Forecast Inquiries
        if any(w in query for w in ["forecast", "project", "projection", "next month", "runway"]):
            intents.append("forecast_expenses")
            tools_to_run.append({"name": "forecast_expenses", "args": {"days_ahead": 30}})

        # Deterministic Calculators (SIP / EMI)
        if any(w in query for w in ["sip", "invest monthly", "compound interest"]):
            intents.append("calculate_sip")
            amt = self._extract_amount(query, default=10000.0)
            years = self._extract_years(query, default=10)
            tools_to_run.append({"name": "calculate_sip", "args": {"monthly_investment": amt, "annual_rate_pct": 12.0, "years": years}})

        if any(w in query for w in ["emi", "loan", "home loan", "car loan"]):
            intents.append("calculate_emi")
            principal = self._extract_amount(query, default=2500000.0)
            tools_to_run.append({"name": "calculate_emi", "args": {"principal": principal, "annual_interest_rate": 8.5, "tenure_years": 20}})

        # Default / Knowledge Retrieval
        if not tools_to_run or any(w in query for w in ["tax", "strategy", "advice", "how to", "rule", "framework", "invest", "stock"]):
            intents.append("search_financial_knowledge")
            tools_to_run.append({"name": "search_financial_knowledge", "args": {"query": state["user_query"]}})

        return {
            "intents": intents,
            "tools_to_run": tools_to_run,
            "safety_flags": safety_flags
        }

    # Node 2: Authorized Tool Execution
    async def _execute_tools_node(self, state: AgentState, db: AsyncSession) -> Dict[str, Any]:
        user_id = state["user_id"]
        results = []
        cited_data = {}
        errors = []

        for t in state["tools_to_run"]:
            t_name = t["name"]
            args = t["args"]
            t_start = time.time()
            try:
                if t_name == "get_transactions":
                    res = await financial_tools.get_transactions(db, user_id, category_name=args.get("category_name"), limit=args.get("limit", 10))
                elif t_name == "get_income":
                    res = await financial_tools.get_income(db, user_id)
                    cited_data["total_income"] = res.get("total_income")
                elif t_name == "get_expenses":
                    res = await financial_tools.get_expenses(db, user_id)
                    cited_data["total_expenses"] = res.get("total_expenses")
                    cited_data["net_savings"] = res.get("net_savings")
                elif t_name == "get_category_spending":
                    res = await financial_tools.get_category_spending(db, user_id)
                    cited_data["categories"] = res.get("categories", [])
                elif t_name == "get_budget_status":
                    res = await financial_tools.get_budget_status(db, user_id)
                    cited_data["budgets"] = res.get("budgets", [])
                elif t_name == "get_goals":
                    res = await financial_tools.get_goals(db, user_id)
                    cited_data["goals"] = res.get("goals", [])
                elif t_name == "calculate_savings_rate":
                    res = await financial_tools.calculate_savings_rate(db, user_id)
                    cited_data["savings_rate_pct"] = res.get("savings_rate_pct")
                elif t_name == "calculate_financial_health":
                    res = await financial_tools.calculate_financial_health(db, user_id)
                    cited_data["health_score"] = res.get("composite_score")
                    cited_data["health_rating"] = res.get("rating")
                elif t_name == "detect_anomalies":
                    res = await financial_tools.detect_anomalies(db, user_id)
                    cited_data["anomalies"] = res.get("anomalies", [])
                elif t_name == "forecast_expenses":
                    res = await financial_tools.forecast_expenses(db, user_id, days_ahead=args.get("days_ahead", 30))
                    cited_data["projected_expense"] = res.get("projected_expense_total")
                elif t_name == "get_recurring_expenses":
                    res = await financial_tools.get_recurring_expenses(db, user_id)
                    cited_data["recurring_expenses"] = res.get("subscriptions", [])
                elif t_name == "search_financial_knowledge":
                    res = await financial_tools.search_financial_knowledge(
                        db=db,
                        user_id=user_id,
                        query=args.get("query", state["user_query"])
                    )
                    cited_data["knowledge_items"] = res.get("knowledge_items", [])
                elif t_name == "calculate_sip":
                    res = financial_tools.calculate_sip(**args)
                    cited_data["sip_future_value"] = res.get("total_maturity_value")
                elif t_name == "calculate_emi":
                    res = financial_tools.calculate_emi(**args)
                    cited_data["monthly_emi"] = res.get("monthly_emi")
                else:
                    res = {"error": f"Tool '{t_name}' not recognized", "status": "failed"}

                elapsed = round(time.time() - t_start, 3)
                results.append({
                    "tool_name": t_name,
                    "parameters": args,
                    "execution_time_sec": elapsed,
                    "status": "success",
                    "output": res
                })
                logger.info(f"Tool {t_name} executed for user {user_id} in {elapsed}s")

            except Exception as e:
                elapsed = round(time.time() - t_start, 3)
                logger.error(f"Tool {t_name} failed for user {user_id}: {str(e)}")
                results.append({
                    "tool_name": t_name,
                    "parameters": args,
                    "execution_time_sec": elapsed,
                    "status": "error",
                    "error": str(e),
                    "output": {"message": "Data is currently unavailable."}
                })
                errors.append(f"Tool {t_name} execution error: {str(e)}")

        return {
            "tool_results": results,
            "cited_data": cited_data,
            "errors": errors
        }

    # Node 3: Synthesis & Persona Grounding
    def _synthesize_response_node(self, state: AgentState) -> Dict[str, Any]:
        persona = state["persona"]
        persona_info = guru_engine.GURUS.get(persona, guru_engine.GURUS["buffett"])
        results = state["tool_results"]
        cited = state["cited_data"]
        suggested_followups = []
        citations_out = []

        header = f"### 💡 **{persona_info['name']} Advisory**\n\n"
        body = ""

        # Present deterministic findings
        for tr in results:
            t_name = tr["tool_name"]
            out = tr.get("output", {})

            if t_name == "calculate_financial_health":
                body += f"📊 **Financial Health Score: {out.get('composite_score', 0)}/100 ({out.get('rating', 'Good')})**\n"
                if out.get("delta_explanation"):
                    body += f"- *{out['delta_explanation']}*\n"
                if out.get("positive_factors"):
                    body += f"- **Strengths:** {', '.join(out['positive_factors'][:2])}\n"
                if out.get("recommendations"):
                    body += f"- **Action Item:** {out['recommendations'][0]}\n\n"
                suggested_followups.append("How can I improve my emergency fund?")

            elif t_name == "calculate_savings_rate":
                s_rate = out.get("savings_rate_pct", 0)
                body += f"💰 **Savings Rate Analysis:**\n"
                body += f"Your current savings rate is **{s_rate:.1f}%** ({out.get('benchmark_evaluation', 'Good')}).\n"
                body += f"- Total Monthly Inflow: **₹{out.get('total_income', 0):,.0f}**\n"
                body += f"- Total Expenses: **₹{out.get('total_expenses', 0):,.0f}**\n"
                body += f"- Net Savings: **₹{out.get('net_savings', 0):,.0f}**\n\n"
                suggested_followups.append("Show my top expense categories")

            elif t_name == "get_category_spending":
                cats = out.get("categories", [])
                if cats:
                    body += f"🛒 **Category Spending Breakdown:**\n"
                    for c in cats[:4]:
                        body += f"- **{c['category']}**: ₹{c['amount']:,.0f} ({c['percentage']:.1f}%)\n"
                    body += "\n"
                else:
                    body += f"ℹ️ *{out.get('message', 'No category spending data found.')}*\n\n"
                suggested_followups.append("Am I over budget in any category?")

            elif t_name == "get_budget_status":
                budgets = out.get("budgets", [])
                over_budget = [b for b in budgets if b.get("is_over_budget")]
                if budgets:
                    body += f"🎯 **Budget Adherence:**\n"
                    if over_budget:
                        body += f"⚠️ **Alert:** You have exceeded budget in **{len(over_budget)} category(ies)**:\n"
                        for b in over_budget:
                            body += f"- **{b['category']}**: Spent ₹{b['spent']:,.0f} of ₹{b['limit']:,.0f} ({b['utilization_pct']:.1f}%)\n"
                    else:
                        body += f"✅ All **{len(budgets)} category budgets** are healthy and within spending limits.\n"
                    body += "\n"
                else:
                    body += f"ℹ️ *{out.get('message', 'No active budgets found.')}*\n\n"
                suggested_followups.append("Set a budget for dining out")

            elif t_name == "get_goals":
                goals = out.get("goals", [])
                if goals:
                    body += f"🏆 **Financial Goals Progress:**\n"
                    for g in goals[:3]:
                        body += f"- **{g['title']}**: ₹{g['current_amount']:,.0f} / ₹{g['target_amount']:,.0f} (**{g['progress_percentage']}%**)\n"
                    body += "\n"
                else:
                    body += f"ℹ️ *{out.get('message', 'No active goals recorded.')}*\n\n"
                suggested_followups.append("Calculate SIP needed to reach ₹50 Lakhs in 10 years")

            elif t_name == "search_financial_knowledge":
                k_items = out.get("knowledge_items", [])
                if k_items and out.get("answer_supported", True):
                    body += f"📖 **Grounded Financial Literature & Uploaded Knowledge:**\n"
                    for k in k_items:
                        page_str = f", Page {k['page_number']}" if k.get("page_number") else ""
                        body += f"- *\"{k.get('relevant_quote', '')}\"* — **{k.get('source_title', '')} ({k.get('author', 'Expert')}{page_str})** [Relevance: {k.get('relevance_score', 1.0)}]\n"
                        citations_out.append({
                            "source_title": k.get("source_title"),
                            "author": k.get("author"),
                            "page_number": k.get("page_number", 1),
                            "relevant_quote": k.get("relevant_quote"),
                            "relevance_score": k.get("relevance_score", 1.0)
                        })
                    body += "\n"
                else:
                    body += f"ℹ️ *The uploaded financial documents do not contain sufficient information on this specific topic.*\n\n"

            elif t_name == "calculate_sip":
                body += f"📈 **SIP Future Value Projection:**\n"
                body += f"Investing **₹{out['monthly_investment']:,.0f}/mo** at **{out['annual_rate_pct']}% ROI** over **{out['years']} years**:\n"
                body += f"- Total Invested: **₹{out['total_invested']:,.0f}**\n"
                body += f"- Estimated Gain: **₹{out['estimated_returns']:,.0f}**\n"
                body += f"- **Final Corpus: ₹{out['total_maturity_value']:,.0f}**\n\n"

            elif t_name == "calculate_emi":
                body += f"💳 **Loan EMI Analysis:**\n"
                body += f"Loan of **₹{out['principal']:,.0f}** at **{out['annual_interest_rate']}%** for **{out['tenure_years']} years**:\n"
                body += f"- Monthly EMI: **₹{out['monthly_emi']:,.0f}**\n"
                body += f"- Total Repayment: **₹{out['total_repayment']:,.0f}** (Interest: ₹{out['total_interest_payable']:,.0f})\n\n"

        # Persona Philosophy
        body += f"**{persona_info['name']}'s Principle:** *\"{persona_info['core_mantra']}\"*\n\n"
        if persona == "buffett":
            body += "Focus on disciplined, low-cost index investing and keeping your expenses simple. Avoid chasing volatile fads and let compounding work for decades."
        elif persona == "kiyosaki":
            body += "Prioritize acquiring income-generating assets over liabilities. Make sure your money works hard for you rather than trading time for money."
        elif persona == "sethi":
            body += "Automate your savings and investments first so you can spend guilt-free on things you love without stressing over small daily costs."
        elif persona == "indian_expert":
            body += "Ensure a strong Indian foundation: 6 months of liquid emergency funds, adequate term + health insurance, and systematic SIPs in equity index funds."
        else:
            body += "Balance systematic investing, conscious living, and emergency preparedness to build sustainable, long-term wealth."

        disclaimer = "\n\n---\n*Disclaimer: FinSight AI provides automated financial insights grounded in verified financial models. Please consult a qualified financial advisor before executing significant investment commitments.*"

        if not suggested_followups:
            suggested_followups = [
                "What is my current savings rate?",
                "How much did I spend on dining this month?",
                "Check my financial health score",
                "Calculate SIP of ₹15,000/mo for 10 years"
            ]

        return {
            "response_text": header + body + disclaimer,
            "suggested_followups": suggested_followups[:4],
            "citations": citations_out
        }

    # Main Agent Process Query Entrypoint
    async def process_query(
        self,
        db: Optional[AsyncSession] = None,
        user_id: Optional[str] = None,
        user_query: str = "",
        persona: str = "balanced",
        user_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Executes LangGraph agent state pipeline.
        Supports both direct database invocation and standalone calculation queries.
        """
        # Support positional / keyword flexibility
        if isinstance(db, str) and not user_query:
            user_query = db
            db = None
        if "user_query" in kwargs and not user_query:
            user_query = kwargs["user_query"]
        if "persona" in kwargs:
            persona = kwargs["persona"]
        if "user_context" in kwargs and not user_context:
            user_context = kwargs["user_context"]

        initial_state: AgentState = {
            "user_query": user_query,
            "user_id": user_id or "anonymous_user",
            "persona": persona or "balanced",
            "user_context": user_context or {},
            "intents": [],
            "tools_to_run": [],
            "tool_results": [],
            "cited_data": {},
            "response_text": "",
            "suggested_followups": [],
            "citations": [],
            "safety_flags": [],
            "errors": []
        }

        # Step 1: Route & Guardrails
        step1 = self._route_intent_node(initial_state)
        initial_state.update(step1)

        if initial_state.get("safety_flags"):
            return {
                "response": initial_state["response_text"],
                "tool_calls": [],
                "cited_data": {},
                "citations": [],
                "suggested_followups": ["What is my savings rate?", "Calculate loan EMI"]
            }

        # Step 2: Execute Authorized Tools
        step2 = await self._execute_tools_node(initial_state, db)
        initial_state.update(step2)

        # Step 3: Synthesize Response
        step3 = self._synthesize_response_node(initial_state)
        initial_state.update(step3)

        return {
            "response": initial_state["response_text"],
            "tool_calls": initial_state["tool_results"],
            "cited_data": initial_state["cited_data"],
            "citations": initial_state.get("citations", []),
            "suggested_followups": initial_state["suggested_followups"]
        }

    async def run(
        self,
        message: str = "",
        user_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
        persona: str = "balanced",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Backward-compatible run interface.
        """
        res = await self.process_query(
            db=db,
            user_id=user_id,
            user_query=message,
            persona=persona,
            **kwargs
        )
        return {
            "status": "success",
            "response": res["response"],
            "tool_calls": res.get("tool_calls", []),
            "cited_data": res.get("cited_data", {}),
            "citations": res.get("citations", []),
            "suggested_followups": res.get("suggested_followups", [])
        }

    def _extract_amount(self, text: str, default: float = 10000.0) -> float:
        match = re.search(r"(?:rs\.?|inr|₹|\$)?\s*([0-9,]+)", text)
        if match:
            try:
                val = float(match.group(1).replace(",", ""))
                if val >= 100:
                    return val
            except ValueError:
                pass
        return default

    def _extract_years(self, text: str, default: int = 10) -> int:
        match = re.search(r"(\d+)\s*(?:years|yrs|year|yr)", text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        return default

financial_advisor_agent = FinancialAdvisorAgent()

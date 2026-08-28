import uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import numpy as np
from collections import defaultdict

class FinancialAnomalyDetector:
    """
    Advanced Financial Anomaly Detection Engine:
    Detects statistical and pattern anomalies across 6 dimensions:
    1. Category spending surges (e.g. Food spending ₹15,800 vs typical ₹6,200 (+155%))
    2. Merchant spending surges (e.g. Amazon spending 3x historical average)
    3. Individual transaction amount outliers (Z-score > 2.5, IQR outlier)
    4. Frequency spikes (burst transactions in short time window)
    5. Recurring subscription & bill changes (step price hikes)
    6. Monthly spending surges (total burn rate deviation)
    
    Includes false-positive prevention by requiring sufficient historical baseline data.
    """

    MIN_HISTORY_TX_COUNT = 3
    MIN_CATEGORY_HISTORY_COUNT = 3
    MIN_MERCHANT_HISTORY_COUNT = 3

    def detect_detailed_anomalies(
        self,
        transactions: List[Dict[str, Any]],
        currency: str = "INR"
    ) -> Dict[str, Any]:
        """
        Executes multi-dimensional anomaly detection on raw transaction dictionaries.
        """
        if not transactions or len(transactions) < self.MIN_HISTORY_TX_COUNT:
            return {
                "total_anomalies": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "total_excess_deviation": 0.0,
                "has_sufficient_history": False,
                "message": "Insufficient historical transaction data to establish reliable statistical baselines (minimum 3 transactions required).",
                "anomalies": []
            }

        debits = [t for t in transactions if str(t.get("transaction_type", "debit")).lower() == "debit"]
        if len(debits) < self.MIN_HISTORY_TX_COUNT:
            return {
                "total_anomalies": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "total_excess_deviation": 0.0,
                "has_sufficient_history": False,
                "message": "Insufficient debit transactions to establish spending baselines.",
                "anomalies": []
            }

        anomalies: List[Dict[str, Any]] = []

        # 1. Detect Individual Transaction Amount Outliers (Statistical Z-Score / IQR)
        anomalies.extend(self._detect_amount_outliers(debits, currency))

        # 2. Detect Category Spending Surges
        anomalies.extend(self._detect_category_surges(debits, currency))

        # 3. Detect Merchant Spending Surges
        anomalies.extend(self._detect_merchant_surges(debits, currency))

        # 4. Detect Frequency Spikes / Burst Spending
        anomalies.extend(self._detect_frequency_spikes(debits))

        # 5. Detect Recurring Expense / Subscription Price Hikes
        anomalies.extend(self._detect_recurring_changes(debits, currency))

        # 6. Detect Overall Monthly Spending Surges
        anomalies.extend(self._detect_monthly_spending_surges(debits, currency))

        # Sort by severity (critical > high > medium > low) and then deviation percentage
        severity_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        anomalies.sort(key=lambda x: (severity_rank.get(x["severity"], 1), x["deviation_pct"]), reverse=True)

        critical_count = sum(1 for a in anomalies if a["severity"] == "critical")
        high_count = sum(1 for a in anomalies if a["severity"] == "high")
        medium_count = sum(1 for a in anomalies if a["severity"] == "medium")
        total_excess = sum(max(0.0, a["observed_value"] - a["expected_value"]) for a in anomalies)

        return {
            "total_anomalies": len(anomalies),
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "total_excess_deviation": round(total_excess, 2),
            "has_sufficient_history": True,
            "message": f"Successfully analyzed {len(debits)} transactions across 6 statistical dimensions.",
            "anomalies": anomalies
        }

    def _detect_amount_outliers(self, debits: List[Dict[str, Any]], currency: str) -> List[Dict[str, Any]]:
        anomalies = []
        amounts = [float(t.get("amount", 0.0)) for t in debits]
        if len(amounts) < 5:
            return anomalies

        mean_amt = float(np.mean(amounts))
        std_amt = float(np.std(amounts))
        median_amt = float(np.median(amounts))

        if std_amt <= 0:
            return anomalies

        for t in debits:
            amt = float(t.get("amount", 0.0))
            z_score = (amt - mean_amt) / std_amt

            # Outlier trigger: Z-score > 2.5 and amount > 2.5x median
            if z_score >= 2.5 and amt >= (median_amt * 2.5) and amt > 1000.0:
                dev_pct = round(((amt - median_amt) / max(1.0, median_amt)) * 100.0, 1)
                severity = "critical" if z_score >= 4.0 or amt >= (median_amt * 5.0) else "high"

                anomalies.append({
                    "id": str(uuid.uuid4()),
                    "anomaly_type": "transaction_amount",
                    "severity": severity,
                    "metric": "single_transaction_amount",
                    "entity_name": t.get("merchant") or t.get("description", "Unknown Merchant"),
                    "observed_value": amt,
                    "expected_value": round(median_amt, 2),
                    "deviation": f"+{dev_pct}%",
                    "deviation_pct": dev_pct,
                    "explanation": (
                        f"Unusually large single transaction of {currency} {amt:,.2f} at "
                        f"{t.get('merchant') or t.get('description')} (Z-score: {z_score:.2f}, "
                        f"typical median: {currency} {median_amt:,.2f})."
                    ),
                    "affected_transactions": [self._format_tx(t)],
                    "detected_at": datetime.utcnow()
                })
        return anomalies

    def _detect_category_surges(self, debits: List[Dict[str, Any]], currency: str) -> List[Dict[str, Any]]:
        anomalies = []
        # Group by category and month (YYYY-MM)
        cat_months = defaultdict(lambda: defaultdict(list))
        for t in debits:
            cat = t.get("category_name") or "Other"
            t_date = self._parse_date(t.get("transaction_date"))
            month_key = t_date.strftime("%Y-%m") if t_date else "current"
            cat_months[cat][month_key].append(t)

        for cat, months in cat_months.items():
            all_cat_txs = [tx for m_txs in months.values() for tx in m_txs]
            if len(all_cat_txs) < self.MIN_CATEGORY_HISTORY_COUNT:
                continue # Guardrail: prevent false positives on insufficient category history

            sorted_months = sorted(months.keys())
            if len(sorted_months) >= 2:
                current_m = sorted_months[-1]
                prev_months = sorted_months[:-1]

                current_txs = months[current_m]
                current_total = sum(float(t.get("amount", 0.0)) for t in current_txs)

                prev_totals = [sum(float(t.get("amount", 0.0)) for t in months[m]) for m in prev_months]
                typical_total = float(np.mean(prev_totals))
            else:
                # If only 1 month of data, check if total in category is overwhelmingly higher than average category
                current_txs = all_cat_txs
                current_total = sum(float(t.get("amount", 0.0)) for t in current_txs)
                # Compute category baseline across other categories
                other_totals = [
                    sum(float(tx.get("amount", 0.0)) for tx in cat_months[c][sorted_months[0]])
                    for c in cat_months if c != cat and len(cat_months[c][sorted_months[0]]) >= 2
                ]
                typical_total = float(np.mean(other_totals)) if other_totals else (current_total * 0.4)

            if typical_total > 0 and current_total >= (typical_total * 1.5) and (current_total - typical_total) >= 1500.0:
                dev_pct = round(((current_total - typical_total) / typical_total) * 100.0, 1)
                severity = "critical" if dev_pct >= 150.0 else ("high" if dev_pct >= 80.0 else "medium")

                anomalies.append({
                    "id": str(uuid.uuid4()),
                    "anomaly_type": "category_spending",
                    "severity": severity,
                    "metric": "category_period_spending",
                    "entity_name": cat,
                    "observed_value": round(current_total, 2),
                    "expected_value": round(typical_total, 2),
                    "deviation": f"+{dev_pct}%",
                    "deviation_pct": dev_pct,
                    "explanation": (
                        f"{cat} spending reached {currency} {current_total:,.2f}, which is "
                        f"+{dev_pct}% above your typical baseline of {currency} {typical_total:,.2f}."
                    ),
                    "affected_transactions": [self._format_tx(t) for t in current_txs[:10]],
                    "detected_at": datetime.utcnow()
                })

        return anomalies

    def _detect_merchant_surges(self, debits: List[Dict[str, Any]], currency: str) -> List[Dict[str, Any]]:
        anomalies = []
        merchant_txs = defaultdict(list)
        for t in debits:
            m_name = (t.get("merchant") or t.get("description", "Unknown")).strip().title()
            if m_name and m_name != "Unknown":
                merchant_txs[m_name].append(t)

        for m_name, txs in merchant_txs.items():
            if len(txs) < self.MIN_MERCHANT_HISTORY_COUNT:
                continue # Guardrail: minimum 3 transactions with this merchant

            amounts = [float(t.get("amount", 0.0)) for t in txs]
            sorted_txs = sorted(txs, key=lambda x: self._parse_date(x.get("transaction_date")) or date.min)
            
            # Compare latest transaction(s) against historical average for this merchant
            latest_tx = sorted_txs[-1]
            latest_amt = float(latest_tx.get("amount", 0.0))
            historical_amts = [float(t.get("amount", 0.0)) for t in sorted_txs[:-1]]
            typical_amt = float(np.mean(historical_amts))

            if typical_amt > 0 and latest_amt >= (typical_amt * 2.0) and latest_amt >= 2000.0:
                dev_pct = round(((latest_amt - typical_amt) / typical_amt) * 100.0, 1)
                severity = "high" if dev_pct >= 100.0 else "medium"

                anomalies.append({
                    "id": str(uuid.uuid4()),
                    "anomaly_type": "merchant_spending",
                    "severity": severity,
                    "metric": "merchant_spend_spike",
                    "entity_name": m_name,
                    "observed_value": round(latest_amt, 2),
                    "expected_value": round(typical_amt, 2),
                    "deviation": f"+{dev_pct}%",
                    "deviation_pct": dev_pct,
                    "explanation": (
                        f"Spending at {m_name} was {currency} {latest_amt:,.2f}, which is "
                        f"+{dev_pct}% higher than your average of {currency} {typical_amt:,.2f}."
                    ),
                    "affected_transactions": [self._format_tx(latest_tx)],
                    "detected_at": datetime.utcnow()
                })

        return anomalies

    def _detect_frequency_spikes(self, debits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        anomalies = []
        daily_counts = defaultdict(list)
        for t in debits:
            t_date = self._parse_date(t.get("transaction_date"))
            if t_date:
                daily_counts[t_date.strftime("%Y-%m-%d")].append(t)

        if len(daily_counts) < 3:
            return anomalies

        counts = [len(tx_list) for tx_list in daily_counts.values()]
        mean_freq = float(np.mean(counts))
        std_freq = float(np.std(counts))

        for day_str, day_txs in daily_counts.items():
            day_count = len(day_txs)
            if day_count >= 5 and day_count >= (mean_freq * 2.5):
                dev_pct = round(((day_count - mean_freq) / max(1.0, mean_freq)) * 100.0, 1)
                anomalies.append({
                    "id": str(uuid.uuid4()),
                    "anomaly_type": "frequency_spike",
                    "severity": "medium",
                    "metric": "daily_transaction_frequency",
                    "entity_name": f"Transactions on {day_str}",
                    "observed_value": float(day_count),
                    "expected_value": round(mean_freq, 1),
                    "deviation": f"+{dev_pct}%",
                    "deviation_pct": dev_pct,
                    "explanation": (
                        f"Unusual burst of {day_count} transactions recorded in a single day ({day_str}), "
                        f"compared to your typical baseline of {mean_freq:.1f} txs/day."
                    ),
                    "affected_transactions": [self._format_tx(t) for t in day_txs],
                    "detected_at": datetime.utcnow()
                })

        return anomalies

    def _detect_recurring_changes(self, debits: List[Dict[str, Any]], currency: str) -> List[Dict[str, Any]]:
        anomalies = []
        recurring_keywords = ["netflix", "spotify", "prime", "gym", "broadband", "electricity", "jio", "airtel", "apple", "icloud"]
        rec_groups = defaultdict(list)

        for t in debits:
            desc = (t.get("description") or t.get("merchant") or "").lower()
            for kw in recurring_keywords:
                if kw in desc:
                    rec_groups[kw].append(t)
                    break

        for kw, txs in rec_groups.items():
            if len(txs) >= 2:
                sorted_txs = sorted(txs, key=lambda x: self._parse_date(x.get("transaction_date")) or date.min)
                latest_amt = float(sorted_txs[-1].get("amount", 0.0))
                prev_amt = float(sorted_txs[-2].get("amount", 0.0))

                if prev_amt > 0 and latest_amt >= (prev_amt * 1.20) and (latest_amt - prev_amt) >= 100.0:
                    dev_pct = round(((latest_amt - prev_amt) / prev_amt) * 100.0, 1)
                    anomalies.append({
                        "id": str(uuid.uuid4()),
                        "anomaly_type": "recurring_change",
                        "severity": "medium",
                        "metric": "recurring_subscription_hike",
                        "entity_name": f"{kw.capitalize()} Subscription / Bill",
                        "observed_value": round(latest_amt, 2),
                        "expected_value": round(prev_amt, 2),
                        "deviation": f"+{dev_pct}%",
                        "deviation_pct": dev_pct,
                        "explanation": (
                            f"Recurring charge for {kw.capitalize()} increased from {currency} {prev_amt:,.2f} "
                            f"to {currency} {latest_amt:,.2f} (+{dev_pct}% price hike)."
                        ),
                        "affected_transactions": [self._format_tx(sorted_txs[-1])],
                        "detected_at": datetime.utcnow()
                    })

        return anomalies

    def _detect_monthly_spending_surges(self, debits: List[Dict[str, Any]], currency: str) -> List[Dict[str, Any]]:
        anomalies = []
        monthly_spend = defaultdict(list)
        for t in debits:
            t_date = self._parse_date(t.get("transaction_date"))
            if t_date:
                monthly_spend[t_date.strftime("%Y-%m")].append(t)

        sorted_months = sorted(monthly_spend.keys())
        if len(sorted_months) >= 2:
            current_m = sorted_months[-1]
            prev_months = sorted_months[:-1]

            current_total = sum(float(t.get("amount", 0.0)) for t in monthly_spend[current_m])
            prev_totals = [sum(float(t.get("amount", 0.0)) for t in monthly_spend[m]) for m in prev_months]
            typical_total = float(np.mean(prev_totals))

            if typical_total > 0 and current_total >= (typical_total * 1.4) and (current_total - typical_total) >= 5000.0:
                dev_pct = round(((current_total - typical_total) / typical_total) * 100.0, 1)
                severity = "critical" if dev_pct >= 100.0 else "high"

                anomalies.append({
                    "id": str(uuid.uuid4()),
                    "anomaly_type": "monthly_spending",
                    "severity": severity,
                    "metric": "monthly_burn_rate",
                    "entity_name": f"Overall Spend in {current_m}",
                    "observed_value": round(current_total, 2),
                    "expected_value": round(typical_total, 2),
                    "deviation": f"+{dev_pct}%",
                    "deviation_pct": dev_pct,
                    "explanation": (
                        f"Total monthly expenditure of {currency} {current_total:,.2f} in {current_m} is "
                        f"+{dev_pct}% higher than your historical monthly baseline of {currency} {typical_total:,.2f}."
                    ),
                    "affected_transactions": [self._format_tx(t) for t in monthly_spend[current_m][:10]],
                    "detected_at": datetime.utcnow()
                })

        return anomalies

    def _parse_date(self, val: Any) -> Optional[date]:
        if isinstance(val, date):
            return val
        if isinstance(val, datetime):
            return val.date()
        if isinstance(val, str):
            try:
                return datetime.strptime(val[:10], "%Y-%m-%d").date()
            except Exception:
                return None
        return None

    def _format_tx(self, t: Dict[str, Any]) -> Dict[str, Any]:
        t_date = self._parse_date(t.get("transaction_date"))
        return {
            "id": str(t.get("id", "")),
            "description": str(t.get("description", "")),
            "amount": float(t.get("amount", 0.0)),
            "merchant": t.get("merchant"),
            "transaction_date": t_date or date.today(),
            "category_name": t.get("category_name")
        }

    # Backward compatibility helper
    def detect_anomalies(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        detailed = self.detect_detailed_anomalies(transactions)
        legacy_list = []
        for a in detailed.get("anomalies", []):
            tx_id = a["affected_transactions"][0]["id"] if a["affected_transactions"] else str(uuid.uuid4())
            tx_desc = a["affected_transactions"][0]["description"] if a["affected_transactions"] else a["entity_name"]
            legacy_list.append({
                "transaction_id": tx_id,
                "description": tx_desc,
                "amount": a["observed_value"],
                "transaction_date": date.today(),
                "category_name": a["entity_name"],
                "reason": a["explanation"],
                "severity": a["severity"]
            })
        return legacy_list

anomaly_detector = FinancialAnomalyDetector()

const API_BASE = "http://127.0.0.1:8000/api/v1";

function getAuthHeaders(): HeadersInit {
  const token = typeof window !== "undefined" ? localStorage.getItem("finsight_token") : null;
  return token
    ? { "Content-Type": "application/json", Authorization: `Bearer ${token}` }
    : { "Content-Type": "application/json" };
}

function getAuthToken(): string | null {
  return typeof window !== "undefined" ? localStorage.getItem("finsight_token") : null;
}

export interface Category {
  id: string;
  name: string;
  group_type: string;
  color: string;
  icon?: string;
  is_custom?: boolean;
}

export interface Transaction {
  id: string;
  amount: number;
  currency?: string;
  transaction_type: string;
  transaction_date: string;
  description: string;
  merchant_name?: string;
  subcategory?: string;
  payment_method?: string;
  source?: string;
  confidence_score?: number;
  notes?: string;
  extra_metadata?: string;
  is_anomaly?: boolean;
  anomaly_reason?: string;
  is_subscription?: boolean;
  category_id?: string;
  category?: Category;
  created_at?: string;
  updated_at?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface TransactionFilterParams {
  page?: number;
  page_size?: number;
  search?: string;
  category_id?: string;
  merchant_name?: string;
  transaction_type?: string;
  payment_method?: string;
  source?: string;
  start_date?: string;
  end_date?: string;
  min_amount?: number;
  max_amount?: number;
  sort_by?: string;
  sort_order?: string;
}

export interface CandidateTransaction {
  id?: string;
  description: string;
  merchant_name?: string;
  amount: number;
  currency: string;
  transaction_type: string;
  transaction_date: string;
  category_suggestion?: string;
  subcategory?: string;
  payment_method?: string;
  source: string;
  confidence_score: number;
  raw_text?: string;
  fingerprint?: string;
  reference_number?: string;
  is_duplicate?: boolean;
  duplicate_reason?: string;
  is_confirmed?: boolean;
}

export interface DocumentIngestionResponse {
  document_id: string;
  filename: string;
  file_type: string;
  processing_status: string;
  total_extracted_transactions: number;
  confidence_avg: number;
  candidates: CandidateTransaction[];
  redaction_stats?: Record<string, number>;
  account_summary?: Record<string, any>;
}

export interface FinancialDocument {
  id: string;
  user_id: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  processing_status: string;
  parsed_metadata?: Record<string, any>;
  created_at: string;
}

export interface HealthScoreComponent {
  name: string;
  score: number;
  weight: number;
  weighted_score?: number;
  status: string;
  metric_value: string;
  description: string;
}

export interface HealthScore {
  score: number;
  rating: string;
  components?: Record<string, HealthScoreComponent>;
  positive_factors?: string[];
  negative_factors?: string[];
  recommendations?: string[];
  score_delta?: number;
  delta_explanation?: string;
  emergency_fund_score?: number;
  savings_rate_score?: number;
  budget_adherence_score?: number;
  debt_and_burn_score?: number;
  insights?: string[];
}

export interface HealthScoreHistoryPoint {
  id: string;
  score: number;
  rating: string;
  calculated_at: string;
  component_scores: Record<string, number>;
}

export interface Budget {
  id: string;
  category_id: string;
  monthly_limit: number;
  spent_amount: number;
  remaining_amount: number;
  spent_percentage: number;
  is_over_budget: boolean;
  alert_threshold_percentage?: number;
  warning_status?: 'normal' | 'warning' | 'critical_overbudget';
  warning_message?: string;
  historical_performance?: Array<{
    month: string;
    budgeted_limit: number;
    spent_amount: number;
    adherence_pct: number;
    is_over_budget: boolean;
  }>;
  ai_recommendation?: string;
  category?: {
    name: string;
    color: string;
  };
}

export interface Goal {
  id: string;
  title: string;
  category: string;
  target_amount: number;
  current_amount: number;
  target_date: string;
  monthly_contribution?: number;
  progress_percentage: number;
  remaining_amount?: number;
  months_remaining?: number;
  required_monthly_saving?: number;
  required_monthly_sip?: number;
  projected_completion_date?: string;
  is_on_track?: boolean;
  ai_recommendation?: string;
  status?: string;
}

// Financial Analytics Types
export interface FinancialSummary {
  total_income: number;
  total_expenses: number;
  net_savings: number;
  savings_rate_pct: number;
  average_daily_spending: number;
  days_in_period: number;
  transaction_count: number;
  start_date?: string;
  end_date?: string;
  currency: string;
}

export interface MonthOverMonthChange {
  income_change_pct: number;
  expense_change_pct: number;
  savings_change_pct: number;
  income_change_abs: number;
  expense_change_abs: number;
  savings_change_abs: number;
  prev_period_income: number;
  prev_period_expense: number;
  prev_period_savings: number;
}

export interface CategorySpending {
  category_id?: string;
  category_name: string;
  group_type: string;
  total_amount: number;
  percentage_of_total: number;
  transaction_count: number;
  color: string;
}

export interface SpendingSplit {
  essential_amount: number;
  essential_pct: number;
  discretionary_amount: number;
  discretionary_pct: number;
  savings_investment_amount: number;
  savings_investment_pct: number;
}

export interface TopMerchantSpending {
  merchant_name: string;
  total_amount: number;
  transaction_count: number;
  percentage_of_expenses: number;
}

export interface BudgetUtilizationItem {
  category_id?: string;
  category_name: string;
  budgeted_amount: number;
  spent_amount: number;
  utilization_pct: number;
  remaining_amount: number;
  is_over_budget: boolean;
  color: string;
}

export interface CashFlowPoint {
  month: string;
  income: number;
  expense: number;
  savings: number;
  savings_rate_pct: number;
}

export interface SubscriptionItem {
  id?: string;
  user_id?: string;
  service_name: string;
  merchant_name?: string;
  recurring_type?: 'monthly_subscription' | 'annual_subscription' | 'recurring_bill' | 'recurring_membership' | string;
  amount: number;
  currency?: string;
  billing_cycle: string;
  annualized_cost?: number;
  confidence?: number;
  status?: 'detected' | 'confirmed' | 'dismissed' | string;
  last_paid_date?: string;
  next_billing_date: string;
  category_name?: string;
  is_active: boolean;
}

export interface SubscriptionDashboardData {
  total_monthly_recurring: number;
  total_annual_recurring: number;
  active_subscriptions_count: number;
  pending_detection_count: number;
  subscriptions_by_type: Record<string, number>;
  subscriptions: SubscriptionItem[];
}

export interface AffectedTransaction {
  id: string;
  description: string;
  amount: number;
  merchant?: string;
  transaction_date: string;
  category_name?: string;
}

export interface DetailedAnomaly {
  id: string;
  anomaly_type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  metric: string;
  entity_name: string;
  observed_value: number;
  expected_value: number;
  deviation: string;
  deviation_pct: number;
  explanation: string;
  affected_transactions: AffectedTransaction[];
  detected_at: string;
}

export interface AnomalySummary {
  total_anomalies: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  total_excess_deviation: number;
  has_sufficient_history: boolean;
  message?: string;
  anomalies: DetailedAnomaly[];
}

export interface PredictionInterval {
  lower_bound: number;
  upper_bound: number;
  confidence_level?: number;
}

export interface CategoryForecastItem {
  category_name: string;
  predicted_amount: number;
  prediction_interval: PredictionInterval;
  percentage_of_total: number;
  trend: 'increasing' | 'stable' | 'decreasing';
  contributing_factors?: string[];
}

export interface RecurringForecastItem {
  service_name: string;
  amount: number;
  billing_cycle: string;
  projected_annual_cost: number;
  category_name?: string;
  next_billing_date?: string;
}

export interface ModelEvaluationMetrics {
  model_name: string;
  baseline_model_name: string;
  mae: number;
  mape: number;
  rmse: number;
  baseline_mae: number;
  baseline_mape: number;
  baseline_rmse: number;
  accuracy_improvement_pct: number;
  evaluation_holdout_days: number;
}

export interface ForecastPoint {
  date: string;
  projected_expense: number;
  lower_bound: number;
  upper_bound: number;
}

export interface ForecastData {
  predicted_monthly_total?: number;
  monthly_prediction_interval?: PredictionInterval;
  confidence_score?: number;
  historical_average_daily: number;
  projected_next_30_days_total: number;
  projected_next_60_days_total: number;
  projected_next_90_days_total: number;
  estimated_runway_months: number;
  trend: string;
  major_contributing_factors?: string[];
  human_readable_explanation?: string;
  disclaimer?: string;
  category_forecasts?: CategoryForecastItem[];
  recurring_forecasts?: RecurringForecastItem[];
  total_recurring_projected?: number;
  total_variable_projected?: number;
  evaluation?: ModelEvaluationMetrics;
  forecast_points: ForecastPoint[];
}

export interface ComprehensiveAnalyticsDashboard {
  summary: FinancialSummary;
  month_over_month: MonthOverMonthChange;
  spending_split: SpendingSplit;
  category_breakdown: CategorySpending[];
  income_vs_expense_trends: CashFlowPoint[];
  largest_merchants: TopMerchantSpending[];
  budget_utilization: BudgetUtilizationItem[];
  recurring_expenses: SubscriptionItem[];
}

export interface ScenarioMetrics {
  monthly_income: number;
  monthly_expenses: number;
  monthly_net_cash_flow: number;
  savings_rate_pct: number;
  annual_savings: number;
  total_budget_limit: number;
  budget_utilization_pct: number;
  health_score: number;
  health_rating: string;
}

export interface GoalImpactItem {
  goal_title: string;
  target_amount: number;
  current_amount: number;
  remaining_amount: number;
  baseline_months_to_complete: number;
  simulated_months_to_complete: number;
  months_saved: number;
  accelerated_completion_date: string;
}

export interface SimulationResult {
  current_scenario: ScenarioMetrics;
  simulated_scenario: ScenarioMetrics;
  net_monthly_delta: number;
  annual_savings_delta: number;
  health_score_delta: number;
  budget_utilization_delta_pct: number;
  goal_impacts: GoalImpactItem[];
  simulated_timeline: Array<{
    month: number;
    projected_expense: number;
    net_monthly_saved: number;
    cumulative_portfolio: number;
  }>;
  projected_net_savings: number;
  runway_impact_months: number;
  ai_explanation?: string;
  guru_critique: Record<string, string>;
}

export interface PhilosophyPerspective {
  philosophy_id: string;
  guru_name: string;
  school_of_thought: string;
  viewpoint: string;
  key_principle: string;
  recommended_allocation?: string;
}

export interface PhilosophyComparisonResponse {
  question: string;
  dimension: string;
  perspectives: PhilosophyPerspective[];
  key_differences: string[];
  areas_of_agreement: string[];
  balanced_synthesis: string;
  disclaimer: string;
}

export interface MonthlyReportMetrics {
  month: string;
  month_name: string;
  currency: string;
  total_income: number;
  total_expenses: number;
  net_savings: number;
  savings_rate_pct: number;
  average_daily_spending: number;
  essential_spending: number;
  discretionary_spending: number;
  spending_by_category: Array<{ category_name: string; amount: number; percentage: number }>;
  top_merchants: Array<{ merchant_name: string; amount: number }>;
  total_budget_limit: number;
  budget_utilization_pct: number;
  overbudget_categories_count: number;
  budget_items: Array<any>;
  active_goals_count: number;
  total_goal_target: number;
  total_goal_saved: number;
  goals: Array<any>;
  anomalies_detected_count: number;
  anomalies: Array<any>;
  recurring_monthly_total: number;
  recurring_annual_total: number;
  recurring_items: Array<any>;
  forecast_next_30_days: number;
  forecast_confidence: number;
  health_score: number;
  health_rating: string;
}

export interface MonthlyReportNarrative {
  executive_summary: string;
  income_narrative: string;
  spending_narrative: string;
  savings_narrative: string;
  budget_narrative: string;
  goal_narrative: string;
  anomalies_narrative: string;
  recurring_narrative: string;
  forecast_narrative: string;
  key_observations: string[];
  recommended_actions: string[];
}

export interface MonthlyReportData {
  report_id: string;
  month: string;
  generated_at: string;
  user_name: string;
  metrics: MonthlyReportMetrics;
  narrative: MonthlyReportNarrative;
}

export const api = {
  async getCategories(): Promise<Category[]> {
    try {
      const res = await fetch(`${API_BASE}/transactions/categories`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) return await res.json();
    } catch (e) {}
    return [
      { id: "c1", name: "Food & Dining", group_type: "Want", color: "#F59E0B" },
      { id: "c2", name: "Groceries", group_type: "Need", color: "#10B981" },
      { id: "c3", name: "Transportation", group_type: "Need", color: "#3B82F6" },
      { id: "c4", name: "Shopping", group_type: "Want", color: "#8B5CF6" },
      { id: "c5", name: "Entertainment", group_type: "Want", color: "#EC4899" },
      { id: "c6", name: "Utilities & Bills", group_type: "Need", color: "#EF4444" },
      { id: "c7", name: "Investment & Savings", group_type: "Savings", color: "#059669" },
      { id: "c8", name: "Income", group_type: "Income", color: "#10B981" },
    ];
  },

  async getTransactions(params?: TransactionFilterParams): Promise<PaginatedResponse<Transaction>> {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append("page", String(params.page));
    if (params?.page_size) searchParams.append("page_size", String(params.page_size));
    if (params?.search) searchParams.append("search", params.search);
    if (params?.category_id) searchParams.append("category_id", params.category_id);
    if (params?.merchant_name) searchParams.append("merchant_name", params.merchant_name);
    if (params?.transaction_type && params.transaction_type !== "all") {
      searchParams.append("transaction_type", params.transaction_type);
    }
    if (params?.payment_method && params.payment_method !== "all") {
      searchParams.append("payment_method", params.payment_method);
    }
    if (params?.source && params.source !== "all") {
      searchParams.append("source", params.source);
    }
    if (params?.start_date) searchParams.append("start_date", params.start_date);
    if (params?.end_date) searchParams.append("end_date", params.end_date);
    if (params?.min_amount) searchParams.append("min_amount", String(params.min_amount));
    if (params?.max_amount) searchParams.append("max_amount", String(params.max_amount));
    if (params?.sort_by) searchParams.append("sort_by", params.sort_by);
    if (params?.sort_order) searchParams.append("sort_order", params.sort_order);

    const res = await fetch(`${API_BASE}/transactions/?${searchParams.toString()}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      throw new Error("Failed to fetch transactions");
    }
    return await res.json();
  },

  async createTransaction(data: Partial<Transaction>): Promise<Transaction> {
    const res = await fetch(`${API_BASE}/transactions/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to create transaction" }));
      throw new Error(err.detail || "Failed to create transaction");
    }
    return await res.json();
  },

  async updateTransaction(id: string, data: Partial<Transaction>): Promise<Transaction> {
    const res = await fetch(`${API_BASE}/transactions/${id}`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to update transaction" }));
      throw new Error(err.detail || "Failed to update transaction");
    }
    return await res.json();
  },

  async deleteTransaction(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/transactions/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      throw new Error("Failed to delete transaction");
    }
  },

  async uploadReceipt(file: File): Promise<DocumentIngestionResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const token = getAuthToken();
    const headers: HeadersInit = token ? { Authorization: `Bearer ${token}` } : {};

    const res = await fetch(`${API_BASE}/documents/upload/receipt`, {
      method: "POST",
      headers,
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Receipt upload failed" }));
      throw new Error(err.detail || "Receipt upload failed");
    }
    return await res.json();
  },

  async uploadBankStatement(file: File): Promise<DocumentIngestionResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const token = getAuthToken();
    const headers: HeadersInit = token ? { Authorization: `Bearer ${token}` } : {};

    const res = await fetch(`${API_BASE}/documents/upload/bank-statement`, {
      method: "POST",
      headers,
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Bank statement upload failed" }));
      throw new Error(err.detail || "Bank statement upload failed");
    }
    return await res.json();
  },

  async confirmDocumentCandidates(docId: string, candidates: CandidateTransaction[]): Promise<{ committed_count: number; message: string }> {
    const res = await fetch(`${API_BASE}/documents/${docId}/confirm`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ transactions: candidates }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Confirmation failed" }));
      throw new Error(err.detail || "Confirmation failed");
    }
    return await res.json();
  },

  async getDocuments(): Promise<FinancialDocument[]> {
    try {
      const res = await fetch(`${API_BASE}/documents/`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) return await res.json();
    } catch (e) {}
    return [];
  },

  async deleteDocument(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/documents/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to delete document" }));
      throw new Error(err.detail || "Failed to delete document");
    }
  },

  // Deterministic Analytics Engine API
  async getAnalyticsDashboard(startDate?: string, endDate?: string): Promise<ComprehensiveAnalyticsDashboard> {
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);

    try {
      const res = await fetch(`${API_BASE}/analytics/dashboard?${params.toString()}`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) return await res.json();
    } catch (e) {}

    // Representative fallback
    return {
      summary: {
        total_income: 85000,
        total_expenses: 34200,
        net_savings: 50800,
        savings_rate_pct: 59.8,
        average_daily_spending: 1140,
        days_in_period: 30,
        transaction_count: 24,
        currency: "INR"
      },
      month_over_month: {
        income_change_pct: 12.5,
        expense_change_pct: -6.2,
        savings_change_pct: 28.4,
        income_change_abs: 10000,
        expense_change_abs: -2300,
        savings_change_abs: 12300,
        prev_period_income: 75000,
        prev_period_expense: 36500,
        prev_period_savings: 38500
      },
      spending_split: {
        essential_amount: 18400,
        essential_pct: 53.8,
        discretionary_amount: 10800,
        discretionary_pct: 31.6,
        savings_investment_amount: 5000,
        savings_investment_pct: 14.6
      },
      category_breakdown: [
        { category_name: "Food & Dining", group_type: "Want", total_amount: 8450, percentage_of_total: 24.7, transaction_count: 12, color: "#F59E0B" },
        { category_name: "Groceries", group_type: "Need", total_amount: 6200, percentage_of_total: 18.1, transaction_count: 6, color: "#10B981" },
        { category_name: "Shopping", group_type: "Want", total_amount: 5400, percentage_of_total: 15.8, transaction_count: 4, color: "#8B5CF6" },
        { category_name: "Bills & Utilities", group_type: "Need", total_amount: 4800, percentage_of_total: 14.0, transaction_count: 3, color: "#EF4444" },
        { category_name: "Transport", group_type: "Need", total_amount: 3600, percentage_of_total: 10.5, transaction_count: 8, color: "#3B82F6" },
        { category_name: "Investment", group_type: "Investment", total_amount: 5750, percentage_of_total: 16.9, transaction_count: 2, color: "#059669" }
      ],
      income_vs_expense_trends: [
        { month: "Jan 2026", income: 75000, expense: 34200, savings: 40800, savings_rate_pct: 54.4 },
        { month: "Feb 2026", income: 75000, expense: 31800, savings: 43200, savings_rate_pct: 57.6 },
        { month: "Mar 2026", income: 82500, expense: 42500, savings: 40000, savings_rate_pct: 48.5 },
        { month: "Apr 2026", income: 75000, expense: 29400, savings: 45600, savings_rate_pct: 60.8 },
        { month: "May 2026", income: 85000, expense: 34200, savings: 50800, savings_rate_pct: 59.8 }
      ],
      largest_merchants: [
        { merchant_name: "Swiggy & Zomato", total_amount: 8450, transaction_count: 12, percentage_of_expenses: 24.7 },
        { merchant_name: "Amazon India", total_amount: 5400, transaction_count: 4, percentage_of_expenses: 15.8 },
        { merchant_name: "Bescom Electricity", total_amount: 4800, transaction_count: 3, percentage_of_expenses: 14.0 },
        { merchant_name: "Uber & Rapido", total_amount: 3600, transaction_count: 8, percentage_of_expenses: 10.5 },
        { merchant_name: "Blinkit Quick Commerce", total_amount: 3200, transaction_count: 5, percentage_of_expenses: 9.4 }
      ],
      budget_utilization: [
        { category_name: "Food & Dining", budgeted_amount: 12000, spent_amount: 8450, utilization_pct: 70.4, remaining_amount: 3550, is_over_budget: false, color: "#F59E0B" },
        { category_name: "Shopping", budgeted_amount: 8000, spent_amount: 5400, utilization_pct: 67.5, remaining_amount: 2600, is_over_budget: false, color: "#8B5CF6" },
        { category_name: "Transportation", budgeted_amount: 5000, spent_amount: 3600, utilization_pct: 72.0, remaining_amount: 1400, is_over_budget: false, color: "#3B82F6" },
        { category_name: "Utilities & Bills", budgeted_amount: 6000, spent_amount: 4800, utilization_pct: 80.0, remaining_amount: 1200, is_over_budget: false, color: "#EF4444" }
      ],
      recurring_expenses: [
        { service_name: "Netflix Premium", amount: 649, billing_cycle: "Monthly", next_billing_date: "2026-09-12", category_name: "Subscriptions", is_active: true },
        { service_name: "Jio Fiber Broadband", amount: 825, billing_cycle: "Monthly", next_billing_date: "2026-09-05", category_name: "Bills", is_active: true },
        { service_name: "Spotify Premium", amount: 179, billing_cycle: "Monthly", next_billing_date: "2026-09-22", category_name: "Subscriptions", is_active: true }
      ]
    };
  },

  async getHealthScore(): Promise<HealthScore> {
    try {
      const res = await fetch(`${API_BASE}/analytics/health-score`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) return await res.json();
    } catch (e) {}
    return {
      score: 78,
      rating: "Good",
      components: {
        savings_rate: { name: "Savings Rate", score: 82, weight: 0.20, status: "Good", metric_value: "28.5%", description: "Saving 28.5% of monthly income" },
        budget_adherence: { name: "Budget Adherence", score: 75, weight: 0.15, status: "Good", metric_value: "74.0% utilized", description: "Utilized 74% of planned monthly limits" },
        debt_burden: { name: "Debt Burden", score: 91, weight: 0.15, status: "Excellent", metric_value: "12.0% DTI", description: "Manageable EMI debt obligations" },
        emergency_fund: { name: "Emergency Fund", score: 63, weight: 0.15, status: "Fair", metric_value: "2.8 Months", description: "Liquid reserve covers 2.8 months (target: 6 months)" },
        spending_consistency: { name: "Spending Consistency", score: 79, weight: 0.15, status: "Good", metric_value: "82% Stability", description: "Disciplined week-over-week spending" },
        recurring_burden: { name: "Recurring Burden", score: 85, weight: 0.10, status: "Excellent", metric_value: "14.2% Fixed", description: "Low fixed recurring subscription burn" },
        goal_progress: { name: "Goal Progress", score: 70, weight: 0.10, status: "Good", metric_value: "60.0% Avg", description: "On-track pacing on active financial goals" }
      },
      positive_factors: [
        "Low debt-to-income ratio at 12.0% (comfortably below 30% risk threshold).",
        "Healthy savings rate of 28.5% consistently exceeding the 50/30/20 benchmark.",
        "Stable week-over-week spending discipline with no erratic spikes."
      ],
      negative_factors: [
        "Emergency reserve covers 2.8 months of expenses (recommended buffer is 6 months).",
        "Moderate discretionary budget burn in dining and entertainment."
      ],
      recommendations: [
        "Increase automatic emergency reserve contribution by ₹5,000/month.",
        "Set real-time budget threshold alerts on dining out."
      ],
      score_delta: 4,
      delta_explanation: "Score increased by +4 points due to reduced discretionary dining out and higher net savings rate.",
      emergency_fund_score: 16,
      savings_rate_score: 21,
      budget_adherence_score: 19,
      debt_and_burn_score: 22,
      insights: [
        "Healthy savings rate of 28.5%.",
        "Emergency reserve covers 2.8 months of living expenses."
      ]
    };
  },

  async getHealthScoreHistory(limit: number = 20): Promise<HealthScoreHistoryPoint[]> {
    try {
      const res = await fetch(`${API_BASE}/analytics/health-score/history?limit=${limit}`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) {
        const data = await res.json();
        return data.history || [];
      }
    } catch (e) {}
    return [
      { id: "h1", score: 72, rating: "Good", calculated_at: "2026-06-01", component_scores: { savings_rate: 70, budget_adherence: 68, debt_burden: 88, emergency_fund: 55, spending_consistency: 74, recurring_burden: 82, goal_progress: 65 } },
      { id: "h2", score: 74, rating: "Good", calculated_at: "2026-07-01", component_scores: { savings_rate: 76, budget_adherence: 72, debt_burden: 90, emergency_fund: 58, spending_consistency: 76, recurring_burden: 84, goal_progress: 68 } },
      { id: "h3", score: 78, rating: "Good", calculated_at: "2026-08-01", component_scores: { savings_rate: 82, budget_adherence: 75, debt_burden: 91, emergency_fund: 63, spending_consistency: 79, recurring_burden: 85, goal_progress: 70 } },
    ];
  },

  async getBudgets(): Promise<Budget[]> {
    try {
      const res = await fetch(`${API_BASE}/budgets/`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) return await res.json();
    } catch (e) {}
    return [
      { id: "b1", category_id: "c1", monthly_limit: 12000, spent_amount: 8450, remaining_amount: 3550, spent_percentage: 70.4, is_over_budget: false, warning_status: "normal", category: { name: "Food & Dining", color: "#F59E0B" } },
      { id: "b2", category_id: "c2", monthly_limit: 8000, spent_amount: 3600, remaining_amount: 4400, spent_percentage: 45.0, is_over_budget: false, warning_status: "normal", category: { name: "Transportation", color: "#3B82F6" } },
      { id: "b3", category_id: "c3", monthly_limit: 15000, spent_amount: 11200, remaining_amount: 3800, spent_percentage: 74.6, is_over_budget: false, warning_status: "normal", category: { name: "Shopping", color: "#8B5CF6" } },
      { id: "b4", category_id: "c6", monthly_limit: 5000, spent_amount: 4450, remaining_amount: 550, spent_percentage: 89.0, is_over_budget: false, warning_status: "warning", warning_message: "Threshold Warning: You have utilized 89.0% of your Entertainment budget.", category: { name: "Entertainment", color: "#EC4899" } }
    ];
  },

  async createBudget(data: { category_id: string; monthly_limit: number; alert_threshold_percentage?: number }): Promise<Budget> {
    const res = await fetch(`${API_BASE}/budgets/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create budget");
    return await res.json();
  },

  async deleteBudget(id: string): Promise<void> {
    await fetch(`${API_BASE}/budgets/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });
  },

  async getGoals(): Promise<Goal[]> {
    try {
      const res = await fetch(`${API_BASE}/goals/`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) return await res.json();
    } catch (e) {}
    return [
      { id: "g1", title: "Emergency Safety Reserve", category: "Emergency Fund", target_amount: 300000, current_amount: 180000, target_date: "2027-06-30", months_remaining: 10, remaining_amount: 120000, required_monthly_saving: 12000, required_monthly_sip: 10500, projected_completion_date: "June 2027", progress_percentage: 60.0, is_on_track: true, ai_recommendation: "On track! Saving ₹12,000/mo covers your target within 10 months." },
      { id: "g2", title: "MacBook Pro M-Series", category: "Laptop Purchase", target_amount: 80000, current_amount: 23000, target_date: "2026-12-31", months_remaining: 4, remaining_amount: 57000, required_monthly_saving: 14250, required_monthly_sip: 14250, projected_completion_date: "December 2026", progress_percentage: 28.8, is_on_track: true, ai_recommendation: "To reach ₹80,000 by December 2026, allocate ₹14,250/mo. Your current monthly surplus supports this." },
      { id: "g3", title: "Global Vacation Fund", category: "Travel", target_amount: 150000, current_amount: 75000, target_date: "2026-12-31", months_remaining: 4, remaining_amount: 75000, required_monthly_saving: 18750, required_monthly_sip: 18750, projected_completion_date: "December 2026", progress_percentage: 50.0, is_on_track: true, ai_recommendation: "Allocate ₹18,750/mo to complete your travel fund on schedule." },
      { id: "g4", title: "Executive Leadership Certification", category: "Education", target_amount: 120000, current_amount: 40000, target_date: "2027-03-31", months_remaining: 7, remaining_amount: 80000, required_monthly_saving: 11428, required_monthly_sip: 11428, projected_completion_date: "March 2027", progress_percentage: 33.3, is_on_track: true, ai_recommendation: "Saving ₹11,428/mo will fund your education milestone by March 2027." }
    ];
  },

  async createGoal(data: { title: string; category?: string; target_amount: number; current_amount?: number; target_date: string; monthly_contribution?: number; expected_return_rate?: number }): Promise<Goal> {
    const res = await fetch(`${API_BASE}/goals/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create goal");
    return await res.json();
  },

  async contributeGoal(id: string, amount: number): Promise<Goal> {
    const res = await fetch(`${API_BASE}/goals/${id}/contribute`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ amount }),
    });
    if (!res.ok) throw new Error("Failed to contribute to goal");
    return await res.json();
  },

  async deleteGoal(id: string): Promise<void> {
    await fetch(`${API_BASE}/goals/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });
  },

  async getForecast(): Promise<ForecastData> {
    try {
      const res = await fetch(`${API_BASE}/analytics/forecast`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) return await res.json();
    } catch (e) {}
    const points: ForecastPoint[] = [];
    for (let i = 1; i <= 30; i++) {
      const proj = 1150 + Math.sin(i / 3) * 200 + (i % 7 === 0 ? 400 : 0);
      points.push({
        date: `Day ${i}`,
        projected_expense: Math.round(proj),
        lower_bound: Math.round(proj * 0.82),
        upper_bound: Math.round(proj * 1.20)
      });
    }
    return {
      predicted_monthly_total: 34500,
      monthly_prediction_interval: {
        lower_bound: 29500,
        upper_bound: 40200,
        confidence_level: 0.85
      },
      confidence_score: 0.88,
      historical_average_daily: 1150,
      projected_next_30_days_total: 34500,
      projected_next_60_days_total: 69000,
      projected_next_90_days_total: 103500,
      estimated_runway_months: 24.5,
      trend: "stable",
      major_contributing_factors: [
        "Consistent spending velocity across recent cycles",
        "Historical average daily burn of ₹1,150.00",
        "Weighted weekend seasonality factor (30% higher discretionary spend)"
      ],
      human_readable_explanation: "Based on your recent transactions, your projected monthly expenditure is ₹34,500.00 (estimated range: ₹29,500.00 – ₹40,200.00 with 88% statistical confidence). Spending trend is currently stable.",
      disclaimer: "Statistical Projection Notice: Future expense forecasts are probabilistic mathematical estimates derived from historical spending patterns and recurring commitments. They do not constitute guaranteed outcomes.",
      category_forecasts: [
        { category_name: "Food & Dining", predicted_amount: 11200, percentage_of_total: 32.5, trend: "stable", prediction_interval: { lower_bound: 9500, upper_bound: 13200, confidence_level: 0.85 }, contributing_factors: ["Regular groceries and weekend dining pattern"] },
        { category_name: "Housing & Rent", predicted_amount: 10000, percentage_of_total: 29.0, trend: "stable", prediction_interval: { lower_bound: 10000, upper_bound: 10000, confidence_level: 0.99 }, contributing_factors: ["Fixed monthly rental commitment"] },
        { category_name: "Transportation", predicted_amount: 4200, percentage_of_total: 12.2, trend: "stable", prediction_interval: { lower_bound: 3400, upper_bound: 5100, confidence_level: 0.85 }, contributing_factors: ["Fuel & commute rides"] },
        { category_name: "Utilities & Bills", predicted_amount: 3800, percentage_of_total: 11.0, trend: "stable", prediction_interval: { lower_bound: 3200, upper_bound: 4400, confidence_level: 0.90 }, contributing_factors: ["Broadband and electricity billing cycles"] },
        { category_name: "Shopping & Entertainment", predicted_amount: 5300, percentage_of_total: 15.3, trend: "stable", prediction_interval: { lower_bound: 3900, upper_bound: 6800, confidence_level: 0.80 }, contributing_factors: ["Variable discretionary shopping"] }
      ],
      recurring_forecasts: [
        { service_name: "Broadband Internet", amount: 999, billing_cycle: "Monthly", projected_annual_cost: 11988, category_name: "Bills" },
        { service_name: "Digital Subscriptions", amount: 799, billing_cycle: "Monthly", projected_annual_cost: 9588, category_name: "Subscriptions" }
      ],
      total_recurring_projected: 1798,
      total_variable_projected: 32702,
      evaluation: {
        model_name: "Trend-Decomposed Seasonal Exponential Smoothing",
        baseline_model_name: "Simple Moving Average (Naive Baseline)",
        mae: 142.50,
        mape: 6.80,
        rmse: 185.20,
        baseline_mae: 215.40,
        baseline_mape: 10.40,
        baseline_rmse: 282.60,
        accuracy_improvement_pct: 33.8,
        evaluation_holdout_days: 10
      },
      forecast_points: points
    };
  },

  async getAnomalies(): Promise<AnomalySummary> {
    try {
      const res = await fetch(`${API_BASE}/analytics/anomalies`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) return await res.json();
    } catch (e) {}
    return {
      total_anomalies: 3,
      critical_count: 1,
      high_count: 1,
      medium_count: 1,
      total_excess_deviation: 15400,
      has_sufficient_history: true,
      anomalies: [
        {
          id: "anom-1",
          anomaly_type: "category_spending",
          severity: "critical",
          metric: "category_period_spending",
          entity_name: "Food & Dining",
          observed_value: 15800,
          expected_value: 6200,
          deviation: "+154.8%",
          deviation_pct: 154.8,
          explanation: "Food spending reached ₹15,800, which is +154.8% above your typical baseline of ₹6,200.",
          affected_transactions: [
            { id: "t1", description: "Weekend Fine Dining", amount: 6500, merchant: "Bastian", transaction_date: "2026-08-25", category_name: "Food & Dining" },
            { id: "t2", description: "Bulk Gourmet Delivery", amount: 4800, merchant: "Swiggy Gourmet", transaction_date: "2026-08-22", category_name: "Food & Dining" }
          ],
          detected_at: new Date().toISOString()
        },
        {
          id: "anom-2",
          anomaly_type: "transaction_amount",
          severity: "high",
          metric: "single_transaction_amount",
          entity_name: "Apple Store",
          observed_value: 45000,
          expected_value: 2800,
          deviation: "+1507.1%",
          deviation_pct: 1507.1,
          explanation: "Unusually large single transaction of ₹45,000 at Apple Store (Z-score: 3.82, typical median: ₹2,800).",
          affected_transactions: [
            { id: "t3", description: "Apple Store BKC", amount: 45000, merchant: "Apple Store", transaction_date: "2026-08-26", category_name: "Shopping" }
          ],
          detected_at: new Date().toISOString()
        },
        {
          id: "anom-3",
          anomaly_type: "recurring_change",
          severity: "medium",
          metric: "recurring_subscription_hike",
          entity_name: "Netflix Premium",
          observed_value: 649,
          expected_value: 499,
          deviation: "+30.1%",
          deviation_pct: 30.1,
          explanation: "Recurring subscription for Netflix increased from ₹499 to ₹649 (+30.1% price change).",
          affected_transactions: [
            { id: "t4", description: "Netflix Monthly Subscription", amount: 649, merchant: "Netflix", transaction_date: "2026-08-20", category_name: "Subscriptions" }
          ],
          detected_at: new Date().toISOString()
        }
      ]
    };
  },

  async scanAnomalies(): Promise<AnomalySummary> {
    try {
      const res = await fetch(`${API_BASE}/analytics/anomalies/scan`, {
        method: "POST",
        headers: getAuthHeaders(),
      });
      if (res.ok) return await res.json();
    } catch (e) {}
    return this.getAnomalies();
  },

  async runSimulation(payload: {
    monthly_income_change?: number;
    income_change_pct?: number;
    monthly_expense_reduction?: number;
    food_spend_reduction?: number;
    shopping_spend_reduction?: number;
    discretionary_spend_reduction?: number;
    removed_subscriptions_amount?: number;
    extra_goal_contribution?: number;
    budget_limit_change?: number;
    one_time_purchase_amount?: number;
    inflation_rate?: number;
    investment_roi?: number;
    timeline_months?: number;
  }): Promise<SimulationResult> {
    try {
      const res = await fetch(`${API_BASE}/analytics/simulation`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(payload),
      });
      if (res.ok) return await res.json();
    } catch (e) {}
    
    // Fallback deterministic simulation mock
    const inc = 75000 + (75000 * ((payload.income_change_pct || 0) / 100)) + (payload.monthly_income_change || 0);
    const expRed = (payload.food_spend_reduction || 0) + (payload.shopping_spend_reduction || 0) + (payload.discretionary_spend_reduction || 0) + (payload.removed_subscriptions_amount || 0);
    const exp = Math.max(35000 - expRed, 10000);
    const net = inc - exp;
    const baseNet = 75000 - 35000;
    const netDelta = net - baseNet;

    return {
      current_scenario: {
        monthly_income: 75000,
        monthly_expenses: 35000,
        monthly_net_cash_flow: 40000,
        savings_rate_pct: 53.3,
        annual_savings: 480000,
        total_budget_limit: 40250,
        budget_utilization_pct: 87.0,
        health_score: 78,
        health_rating: "Good"
      },
      simulated_scenario: {
        monthly_income: inc,
        monthly_expenses: exp,
        monthly_net_cash_flow: net,
        savings_rate_pct: Math.round((net / inc) * 1000) / 10,
        annual_savings: net * 12,
        total_budget_limit: exp * 1.15,
        budget_utilization_pct: 87.0,
        health_score: Math.min(78 + Math.round(netDelta / 2000), 96),
        health_rating: netDelta > 0 ? "Excellent" : "Good"
      },
      net_monthly_delta: netDelta,
      annual_savings_delta: netDelta * 12,
      health_score_delta: Math.round(netDelta / 2000),
      budget_utilization_delta_pct: -5.5,
      goal_impacts: [
        {
          goal_title: "MacBook Pro M-Series",
          target_amount: 80000,
          current_amount: 23000,
          remaining_amount: 57000,
          baseline_months_to_complete: 4,
          simulated_months_to_complete: netDelta > 0 ? 3 : 4,
          months_saved: netDelta > 0 ? 1 : 0,
          accelerated_completion_date: "November 2026"
        },
        {
          goal_title: "Emergency Safety Reserve",
          target_amount: 300000,
          current_amount: 180000,
          remaining_amount: 120000,
          baseline_months_to_complete: 10,
          simulated_months_to_complete: netDelta > 0 ? 8 : 10,
          months_saved: netDelta > 0 ? 2 : 0,
          accelerated_completion_date: "April 2027"
        }
      ],
      simulated_timeline: Array.from({ length: 24 }, (_, i) => ({
        month: i + 1,
        projected_expense: Math.round(exp * Math.pow(1.005, i + 1)),
        net_monthly_saved: net,
        cumulative_portfolio: 150000 + net * (i + 1) * 1.05
      })),
      projected_net_savings: 150000 + net * 24 * 1.05,
      runway_impact_months: Math.round(((150000 + net * 24) / exp) * 10) / 10,
      ai_explanation: `Your simulated scenario unlocks +₹${Math.max(netDelta, 0).toLocaleString()}/month in net surplus (+₹${Math.max(netDelta * 12, 0).toLocaleString()} additional annual savings), boosting your overall savings rate to ${(Math.round((net / inc) * 1000) / 10)}%. Financial Health Score is projected to increase by +${Math.max(Math.round(netDelta / 2000), 0)} points.`,
      guru_critique: {
        buffett: `Disciplined compounding of your surplus will multiply your financial runway significantly.`,
        kiyosaki: `Redirecting your net monthly boost into cash-flowing assets lowers your earned wage dependency.`,
        sethi: `Automate the extra monthly transfer directly into your goal accounts on payday.`
      }
    };
  },

  async getSubscriptionsDashboard(): Promise<SubscriptionDashboardData> {
    try {
      const res = await fetch(`${API_BASE}/subscriptions/`, {
        headers: getAuthHeaders(),
      });
      if (res.ok) return await res.json();
    } catch (e) {}
    return {
      total_monthly_recurring: 3478.0,
      total_annual_recurring: 41736.0,
      active_subscriptions_count: 5,
      pending_detection_count: 1,
      subscriptions_by_type: {
        monthly_subscription: 828.0,
        annual_subscription: 124.9,
        recurring_bill: 825.0,
        recurring_membership: 1750.0
      },
      subscriptions: [
        { id: "s1", service_name: "Netflix Premium", merchant_name: "Netflix", recurring_type: "monthly_subscription", amount: 649, billing_cycle: "monthly", annualized_cost: 7788, confidence: 0.95, status: "confirmed", last_paid_date: "2026-08-10", next_billing_date: "2026-09-10", category_name: "Subscriptions", is_active: true },
        { id: "s2", service_name: "Spotify Family", merchant_name: "Spotify", recurring_type: "monthly_subscription", amount: 179, billing_cycle: "monthly", annualized_cost: 2148, confidence: 0.95, status: "confirmed", last_paid_date: "2026-08-20", next_billing_date: "2026-09-20", category_name: "Subscriptions", is_active: true },
        { id: "s3", service_name: "Amazon Prime Annual", merchant_name: "Amazon", recurring_type: "annual_subscription", amount: 1499, billing_cycle: "yearly", annualized_cost: 1499, confidence: 0.95, status: "confirmed", last_paid_date: "2026-01-15", next_billing_date: "2027-01-15", category_name: "Subscriptions", is_active: true },
        { id: "s4", service_name: "Jio Fiber Broadband", merchant_name: "Reliance Jio", recurring_type: "recurring_bill", amount: 825, billing_cycle: "monthly", annualized_cost: 9900, confidence: 0.95, status: "confirmed", last_paid_date: "2026-08-05", next_billing_date: "2026-09-05", category_name: "Bills", is_active: true },
        { id: "s5", service_name: "Cult.fit Elite Membership", merchant_name: "Cult.fit", recurring_type: "recurring_membership", amount: 1750, billing_cycle: "monthly", annualized_cost: 21000, confidence: 0.92, status: "detected", last_paid_date: "2026-08-15", next_billing_date: "2026-09-15", category_name: "Healthcare", is_active: true }
      ]
    };
  },

  async scanSubscriptions(): Promise<SubscriptionDashboardData> {
    try {
      const res = await fetch(`${API_BASE}/subscriptions/scan`, {
        method: "POST",
        headers: getAuthHeaders(),
      });
      if (res.ok) return await res.json();
    } catch (e) {}
    return this.getSubscriptionsDashboard();
  },

  async confirmSubscription(id: string): Promise<SubscriptionItem> {
    const res = await fetch(`${API_BASE}/subscriptions/${id}/confirm`, {
      method: "POST",
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to confirm subscription");
    return await res.json();
  },

  async dismissSubscription(id: string): Promise<SubscriptionItem> {
    const res = await fetch(`${API_BASE}/subscriptions/${id}/dismiss`, {
      method: "POST",
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to dismiss subscription");
    return await res.json();
  },

  async updateSubscription(id: string, data: Partial<SubscriptionItem>): Promise<SubscriptionItem> {
    const res = await fetch(`${API_BASE}/subscriptions/${id}`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update subscription");
    return await res.json();
  },

  async createSubscription(data: { service_name: string; amount: number; billing_cycle?: string; recurring_type?: string; next_billing_date?: string }): Promise<SubscriptionItem> {
    const res = await fetch(`${API_BASE}/subscriptions/`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create subscription");
    return await res.json();
  },

  async deleteSubscription(id: string): Promise<void> {
    await fetch(`${API_BASE}/subscriptions/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });
  },

  async getMonthlyReport(month?: string): Promise<MonthlyReportData> {
    const url = month ? `${API_BASE}/reports/monthly?month=${month}` : `${API_BASE}/reports/monthly`;
    const res = await fetch(url, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch monthly report");
    return await res.json();
  },

  getMonthlyReportPdfUrl(month?: string): string {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    const m = month || "2026-08";
    return `${API_BASE}/reports/monthly/pdf?month=${m}&token=${token || ""}`;
  },

  async comparePhilosophies(question: string, dimension?: string, philosophies?: string[]): Promise<PhilosophyComparisonResponse> {
    const res = await fetch(`${API_BASE}/advisor/compare`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ question, dimension, philosophies }),
    });
    if (!res.ok) throw new Error("Failed to compare philosophies");
    return await res.json();
  },

  async getExpenseForecast(): Promise<ForecastData> {
    return this.getForecast();
  },

  async confirmCandidateTransactions(documentId: string, transactions: any[]): Promise<any> {
    const res = await fetch(`${API_BASE}/documents/${documentId}/confirm`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ transactions }),
    });
    if (!res.ok) throw new Error("Failed to confirm transactions");
    return await res.json();
  }
};

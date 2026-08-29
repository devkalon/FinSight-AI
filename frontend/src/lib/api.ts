export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

function getAuthHeaders(): HeadersInit {
  const token = typeof window !== "undefined" ? localStorage.getItem("finsight_token") : null;
  return token
    ? { "Content-Type": "application/json", Authorization: `Bearer ${token}` }
    : { "Content-Type": "application/json" };
}

function getAuthToken(): string | null {
  return typeof window !== "undefined" ? localStorage.getItem("finsight_token") : null;
}

// Centralized fetch that surfaces failures instead of silently swallowing them.
// Network errors and non-2xx responses are logged and re-thrown so the UI can
// render a real error state rather than plausible-looking fabricated data.
async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: getAuthHeaders(),
      ...init,
    });
  } catch (e) {
    console.error(`[api] Network error calling ${path}:`, e);
    throw new Error(`Unable to reach the server. Please check your connection and try again.`);
  }
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    const detail = err?.detail || `Request failed (${res.status})`;
    console.error(`[api] ${path} failed:`, res.status, detail);
    throw new Error(detail);
  }
  return res.json();
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
    return requestJson<Category[]>(`/transactions/categories`);
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
    return requestJson<FinancialDocument[]>(`/documents/`);
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
    return requestJson<ComprehensiveAnalyticsDashboard>(`/analytics/dashboard?${params.toString()}`);
  },

  async getHealthScore(): Promise<HealthScore> {
    return requestJson<HealthScore>(`/analytics/health-score`);
  },

  async getHealthScoreHistory(limit: number = 20): Promise<HealthScoreHistoryPoint[]> {
    const data = await requestJson<{ history?: HealthScoreHistoryPoint[] }>(
      `/analytics/health-score/history?limit=${limit}`
    );
    return data.history || [];
  },

  async getBudgets(): Promise<Budget[]> {
    return requestJson<Budget[]>(`/budgets/`);
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
    const res = await fetch(`${API_BASE}/budgets/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to delete budget");
  },

  async getGoals(): Promise<Goal[]> {
    return requestJson<Goal[]>(`/goals/`);
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
    const res = await fetch(`${API_BASE}/goals/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to delete goal");
  },

  async getForecast(): Promise<ForecastData> {
    return requestJson<ForecastData>(`/analytics/forecast`);
  },

  async getAnomalies(): Promise<AnomalySummary> {
    return requestJson<AnomalySummary>(`/analytics/anomalies`);
  },

  async scanAnomalies(): Promise<AnomalySummary> {
    return requestJson<AnomalySummary>(`/analytics/anomalies/scan`, { method: "POST" });
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
    return requestJson<SimulationResult>(`/analytics/simulation`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getSubscriptionsDashboard(): Promise<SubscriptionDashboardData> {
    return requestJson<SubscriptionDashboardData>(`/subscriptions/`);
  },

  async scanSubscriptions(): Promise<SubscriptionDashboardData> {
    return requestJson<SubscriptionDashboardData>(`/subscriptions/scan`, { method: "POST" });
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
    const res = await fetch(`${API_BASE}/subscriptions/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error("Failed to delete subscription");
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
    const token = typeof window !== "undefined" ? localStorage.getItem("finsight_token") : null;
    const m = month || "2026-08";
    return `${API_BASE}/reports/monthly/pdf?month=${m}&token=${token || ""}`;
  },

  async downloadStatementPdf(): Promise<void> {
    const token = typeof window !== "undefined" ? localStorage.getItem("finsight_token") : null;
    const res = await fetch(`${API_BASE}/reports/export/pdf`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) throw new Error("Failed to export PDF statement");
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `FinSight_Statement_${new Date().toISOString().split("T")[0]}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
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

# FinSight AI — Database Schema Specification & Data Dictionary

**Engine:** PostgreSQL with SQLAlchemy 2.0 Async & Alembic Migrations  
**Precision Standard:** Decimal `Numeric(14, 2)` / `Numeric(18, 4)` for all currency values. Zero floating-point money storage.

---

## 1. Entity Relationship Overview

```
                      ┌────────────────────┐
                      │       users        │
                      └─────────┬──────────┘
                                │ 1:1
                                ▼
                      ┌────────────────────┐
                      │      profiles      │
                      └────────────────────┘
                                │ 1:N
        ┌───────────────┬───────┴───────┬───────────────┬───────────────┐
        ▼               ▼               ▼               ▼               ▼
┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│  categories  ││transaction_src││   budgets    ││financial_goal││financial_docs│
└───────┬──────┘└───────┬──────┘└───────┬──────┘└───────┬──────┘└───────┬──────┘
        │               │               │               │               │
        │               ▼               ▼               ▼               ▼
        │        ┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
        └───────►│ transactions ││budget_categor││goal_contribut││document_chunk│
                 └──────┬───────┘└──────────────┘└──────────────┘└──────────────┘
                        │
                        ▼
                 ┌──────────────┐
                 │  anomalies   │
                 └──────────────┘
```

---

## 2. Table Specifications

### 2.1 Identity & Core Users
* **`users`**: `id` (UUID PK), `email` (Unique VARCHAR), `hashed_password`, `is_active`, `is_verified`, `is_deleted`, `deleted_at`, `created_at`, `updated_at`.
* **`profiles`**: `id` (UUID PK), `user_id` (UUID FK, Unique), `full_name`, `preferred_currency`, `monthly_income` (`Numeric(14,2)`), `risk_tolerance`, `country_code`, `tax_regime`, `preferred_guru`, `created_at`, `updated_at`.

### 2.2 Taxonomy & Ingestion
* **`merchants`**: `id` (UUID PK), `name`, `normalized_name` (Unique), `default_category_id` (FK), `icon`, `website`, `created_at`, `updated_at`.
* **`categories`**: `id` (UUID PK), `user_id` (FK nullable), `name`, `group_type` (`Need`, `Want`, `Savings`, `Investment`, `Income`), `icon`, `color`, `is_custom`, `is_deleted`, `created_at`, `updated_at`.
* **`category_learning_rules`**: `id` (UUID PK), `user_id` (FK), `keyword_pattern`, `category_id` (FK), `confidence_score` (Float), `created_at`, `updated_at`.
* **`transaction_sources`**: `id` (UUID PK), `user_id` (FK), `source_name`, `source_type` (`bank_pdf`, `ocr_receipt`, `csv`, `upi_sms`, `manual`), `account_identifier_masked`, `is_active`, `created_at`, `updated_at`.

### 2.3 Financial Ledger & Subscriptions
* **`transactions`**: `id` (UUID PK), `user_id` (FK), `source_id` (FK), `category_id` (FK), `merchant_id` (FK), `amount` (`Numeric(14,2)`), `currency` (VARCHAR), `transaction_type` (`debit`, `credit`, `transfer`), `transaction_date` (DATE), `description` (TEXT), `payment_method`, `confidence_score` (`Numeric(5,4)`), `is_subscription` (BOOL), `is_deleted` (BOOL), `deleted_at`, `raw_extracted_text`, `created_at`, `updated_at`.
* **`subscriptions`**: `id` (UUID PK), `user_id` (FK), `merchant_id` (FK), `category_id` (FK), `service_name`, `amount` (`Numeric(14,2)`), `currency`, `billing_cycle`, `next_billing_date`, `is_active`, `is_deleted`, `created_at`, `updated_at`.
* **`anomalies`**: `id` (UUID PK), `user_id` (FK), `transaction_id` (FK), `anomaly_type`, `severity`, `description`, `z_score` (`Numeric(6,3)`), `is_resolved`, `created_at`, `updated_at`.

### 2.4 Budgets, Goals & Health Scoring
* **`budgets`**: `id` (UUID PK), `user_id` (FK), `name`, `period`, `total_limit` (`Numeric(14,2)`), `alert_threshold_percentage`, `is_active`, `is_deleted`, `created_at`, `updated_at`.
* **`budget_categories`**: `id` (UUID PK), `budget_id` (FK), `category_id` (FK), `allocated_limit` (`Numeric(14,2)`), `created_at`, `updated_at`.
* **`financial_goals`**: `id` (UUID PK), `user_id` (FK), `title`, `category`, `target_amount` (`Numeric(14,2)`), `current_amount` (`Numeric(14,2)`), `currency`, `target_date`, `expected_return_rate` (`Numeric(5,2)`), `status`, `is_deleted`, `created_at`, `updated_at`.
* **`goal_contributions`**: `id` (UUID PK), `goal_id` (FK), `user_id` (FK), `transaction_id` (FK nullable), `amount` (`Numeric(14,2)`), `contribution_date`, `notes`, `created_at`.
* **`financial_scores`**: `id` (UUID PK), `user_id` (FK), `composite_score` (INT), `rating`, `emergency_fund_score` (INT), `savings_rate_score` (INT), `budget_adherence_score` (INT), `debt_and_burn_score` (INT), `calculation_metadata` (JSON), `calculated_at`.

### 2.5 Knowledge Base & Advisory Engine
* **`financial_documents`**: `id` (UUID PK), `user_id` (FK), `filename`, `file_type`, `file_size_bytes`, `storage_path`, `processing_status`, `parsed_metadata` (JSON), `is_deleted`, `created_at`, `updated_at`.
* **`document_chunks`**: `id` (UUID PK), `document_id` (FK), `chunk_index`, `content`, `metadata_json`, `created_at`.
* **`guru_profiles`**: `id` (UUID PK), `guru_code` (Unique), `name`, `title`, `core_mantra`, `philosophy_description`, `avatar_url`, `created_at`, `updated_at`.
* **`guru_principles`**: `id` (UUID PK), `guru_id` (FK), `principle_order`, `title`, `description`, `created_at`.
* **`advice_sessions`**: `id` (UUID PK), `user_id` (FK), `guru_id` (FK nullable), `title`, `session_type`, `is_active`, `created_at`, `updated_at`.
* **`recommendations`**: `id` (UUID PK), `session_id` (FK), `user_id` (FK), `guru_id` (FK), `category_id` (FK), `topic`, `recommendation_text`, `action_items` (JSON), `estimated_savings_impact` (`Numeric(14,2)`), `created_at`.
* **`audit_logs`**: `id` (UUID PK), `user_id` (FK nullable), `action`, `entity_type`, `entity_id`, `client_ip`, `user_agent`, `details` (JSON), `created_at`.

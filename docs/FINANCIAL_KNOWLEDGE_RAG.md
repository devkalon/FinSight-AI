# FinSight AI — Financial Knowledge RAG System Architecture

## Overview
The FinSight AI Financial Knowledge RAG (Retrieval-Augmented Generation) system enables users to upload educational financial documents (PDFs, book excerpts, regulatory manuals, tax playbooks, and personal finance notes) and ground the AI advisor's responses in verified literature.

```
                    User Document Upload (PDF / TXT)
                                  │
                                  ▼
               ┌──────────────────────────────────────┐
               │    Text Extraction & Sanitization    │
               │   - Page-by-page PDF extraction      │
               │   - Control character normalization  │
               └──────────────────┬───────────────────┘
                                  │
                                  ▼
               ┌──────────────────────────────────────┐
               │     Page-Aware Semantic Chunking     │
               │   - 400-char windows, 50-char overlap│
               │   - Preserves source page numbers    │
               └──────────────────┬───────────────────┘
                                  │
                                  ▼
               ┌──────────────────────────────────────┐
               │       Database & Vector Storage      │
               │   - PostgreSQL document_chunks table │
               │   - Strict user_id ownership         │
               └──────────────────┬───────────────────┘
                                  │
                                  ▼
               ┌──────────────────────────────────────┐
               │  User-Isolated Grounded Retrieval    │
               │   - Top-k retrieval (k=3)            │
               │   - Relevance threshold (>0.15)      │
               │   - Non-fabrication guardrail        │
               └──────────────────┬───────────────────┘
                                  │
                                  ▼
               ┌──────────────────────────────────────┐
               │    LangGraph Advisor Integration     │
               │   - Discloses Grounded Citations     │
               │   - Page numbers & match percentages │
               └──────────────────────────────────────┘
```

---

## Key Features

1. **User Isolation & Ownership**:
   - Every uploaded document chunk is indexed with `user_id`. Queries only search documents owned by the authenticated user plus verified base financial literature.
   - Cross-user retrieval is strictly forbidden and verified via automated IDOR tests.

2. **Page-Aware Chunk Metadata**:
   - Each chunk retains `chunk_index`, `page_number`, `source_title`, `author`, and `relevance_score`.

3. **Relevance Threshold & Non-Fabrication Guardrail**:
   - Chunks falling below the relevance threshold (0.15) are pruned.
   - If no relevant knowledge is found, the system explicitly reports: *"The uploaded financial documents do not contain sufficient information on this specific topic."*

4. **Tri-Tier Distinction in AI Advisory**:
   - **User Financial Ledger Data**: Direct numbers computed from database transactions.
   - **Retrieved Educational Knowledge**: Passages cited with source, author, page number, and similarity score.
   - **General Guru Principles**: Broad philosophies from Warren Buffett, Robert Kiyosaki, Ramit Sethi, etc.

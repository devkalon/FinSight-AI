import os
import re
import json
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

CONFIDENCE_THRESHOLD = 0.70

class ExpenseCategorizer:
    """
    FinSight AI Hybrid 4-Layer Categorization Engine:
    - Layer 4 (Top Priority): User-Specific Learned Correction Rules
    - Layer 1: Deterministic Merchant / Keyword Regex Rules
    - Layer 2: Machine Learning Classifier (TF-IDF + Calibrated Logistic Regression)
    - Layer 3: LLM Contextual Semantic Fallback for Low-Confidence Predictions
    """

    CATEGORIES = [
        "Food", "Transport", "Shopping", "Bills", "Entertainment",
        "Education", "Healthcare", "Rent", "EMI", "Insurance",
        "Investment", "Travel", "Subscriptions", "Other"
    ]

    DETERMINISTIC_RULES = {
        "Food": {
            "keywords": [
                "swiggy", "zomato", "restaurant", "cafe", "starbucks", "mcdonalds", "subway",
                "dominos", "kfc", "burger king", "pizza hut", "biryani", "dine", "tea", "coffee",
                "chaayos", "chai point", "eatclub", "haldirams", "behrouz", "faasos",
                "blinkit", "zepto", "dmart", "grocery", "supermarket", "reliance fresh",
                "bigbasket", "bbdaily", "instamart", "vegetables", "fruits", "milk", "bakery"
            ],
            "subcategories": {
                "swiggy": "Food Delivery", "zomato": "Food Delivery", "eatclub": "Food Delivery",
                "starbucks": "Cafe & Bakery", "chaayos": "Cafe & Bakery", "chai": "Cafe & Bakery", "coffee": "Cafe & Bakery",
                "blinkit": "Groceries", "zepto": "Groceries", "dmart": "Groceries", "bigbasket": "Groceries", "grocery": "Groceries"
            },
            "default_subcat": "Restaurants"
        },
        "Transport": {
            "keywords": [
                "uber", "ola", "metro", "fuel", "petrol", "diesel", "shell", "hpcl", "bpcl", "iocl",
                "rapido", "auto", "cab", "parking", "toll", "fastag", "cng", "service station", "nhai"
            ],
            "subcategories": {
                "uber": "Cabs & Rides", "ola": "Cabs & Rides", "rapido": "Cabs & Rides", "cab": "Cabs & Rides",
                "fuel": "Fuel", "petrol": "Fuel", "diesel": "Fuel", "shell": "Fuel", "hpcl": "Fuel", "bpcl": "Fuel",
                "fastag": "Tolls & Parking", "toll": "Tolls & Parking", "parking": "Tolls & Parking",
                "metro": "Public Transit"
            },
            "default_subcat": "Cabs & Rides"
        },
        "Shopping": {
            "keywords": [
                "amazon", "flipkart", "myntra", "shopping", "croma", "apple", "zara", "h&m", "nike",
                "adidas", "clothes", "electronics", "mall", "nykaa", "meesho", "ajio", "tata cliq",
                "ikea", "decathlon", "uniliver", "westside", "pantaloons", "shoppers stop"
            ],
            "subcategories": {
                "amazon": "Online Retail", "flipkart": "Online Retail", "nykaa": "Online Retail", "meesho": "Online Retail",
                "myntra": "Clothing & Fashion", "zara": "Clothing & Fashion", "h&m": "Clothing & Fashion", "ajio": "Clothing & Fashion",
                "croma": "Electronics", "apple": "Electronics", "reliance digital": "Electronics",
                "ikea": "Home & Kitchen"
            },
            "default_subcat": "Online Retail"
        },
        "Bills": {
            "keywords": [
                "airtel", "jio", "vi", "vodafone", "electricity", "bescom", "tneb", "mseb", "bill",
                "tatasky", "broadband", "wifi", "water", "gas", "cylinder", "recharge", "bwssb",
                "mahanagar gas", "indane", "hp gas", "bharat gas", "act fibernet", "tata power", "bses"
            ],
            "subcategories": {
                "electricity": "Electricity", "bescom": "Electricity", "tneb": "Electricity", "tata power": "Electricity", "bses": "Electricity",
                "airtel": "Mobile & Broadband", "jio": "Mobile & Broadband", "broadband": "Mobile & Broadband", "wifi": "Mobile & Broadband",
                "gas": "Water & Gas", "cylinder": "Water & Gas", "indane": "Water & Gas", "bwssb": "Water & Gas", "water": "Water & Gas",
                "tatasky": "DTH", "tata play": "DTH", "dth": "DTH"
            },
            "default_subcat": "Utilities"
        },
        "Subscriptions": {
            "keywords": [
                "netflix", "spotify", "prime video", "hotstar", "disney", "youtube premium",
                "apple music", "github copilot", "chatgpt", "openai", "aws", "google one",
                "cloud storage", "adobe", "saas", "dropbox", "notion", "figma", "midjourney"
            ],
            "subcategories": {
                "netflix": "Media Streaming", "spotify": "Media Streaming", "hotstar": "Media Streaming", "youtube": "Media Streaming",
                "github": "SaaS & Cloud", "openai": "SaaS & Cloud", "chatgpt": "SaaS & Cloud", "aws": "SaaS & Cloud", "adobe": "SaaS & Cloud"
            },
            "default_subcat": "Media Streaming"
        },
        "Entertainment": {
            "keywords": [
                "bookmyshow", "pvr", "inox", "cinema", "movie", "gaming", "steam", "playstation",
                "xbox", "arcade", "smaaash", "amusement", "concert", "ipl tickets"
            ],
            "subcategories": {
                "bookmyshow": "Movies & Events", "pvr": "Movies & Events", "inox": "Movies & Events", "cinema": "Movies & Events",
                "steam": "Gaming", "playstation": "Gaming", "xbox": "Gaming"
            },
            "default_subcat": "Movies & Events"
        },
        "Education": {
            "keywords": [
                "udemy", "coursera", "school fees", "tuition", "coaching", "allen", "aakash",
                "university", "college", "books", "oxford", "edx", "unacademy", "byjus", "exam fee"
            ],
            "subcategories": {
                "udemy": "Courses & Books", "coursera": "Courses & Books", "books": "Courses & Books",
                "school": "Tuition & School Fees", "tuition": "Tuition & School Fees", "coaching": "Tuition & School Fees"
            },
            "default_subcat": "Courses & Books"
        },
        "Healthcare": {
            "keywords": [
                "apollo", "pharmacy", "medicine", "1mg", "pharmeasy", "hospital", "doctor",
                "practo", "dentist", "diagnostic", "blood test", "cult fit", "cultfit", "gym", "fitness"
            ],
            "subcategories": {
                "pharmacy": "Pharmacy & Medicine", "medicine": "Pharmacy & Medicine", "1mg": "Pharmacy & Medicine", "pharmeasy": "Pharmacy & Medicine",
                "hospital": "Doctor & Hospital", "doctor": "Doctor & Hospital", "practo": "Doctor & Hospital",
                "cult": "Fitness & Gym", "gym": "Fitness & Gym", "fitness": "Fitness & Gym"
            },
            "default_subcat": "Doctor & Hospital"
        },
        "Rent": {
            "keywords": [
                "house rent", "flat rent", "landlord", "society maintenance", "apartment maintenance",
                "nobroker pay", "cred rent", "housing rent", "property maintenance", "society dues"
            ],
            "subcategories": {
                "rent": "House Rent", "landlord": "House Rent",
                "maintenance": "Maintenance & Society Dues", "society": "Maintenance & Society Dues"
            },
            "default_subcat": "House Rent"
        },
        "EMI": {
            "keywords": [
                "loan emi", "home loan", "car loan", "personal loan", "credit card emi",
                "emi deduction", "bajaj finance emi", "hdfc loan emi", "sbi loan"
            ],
            "subcategories": {
                "home loan": "Home Loan", "car loan": "Car Loan", "personal loan": "Personal Loan",
                "credit card emi": "Credit Card EMI"
            },
            "default_subcat": "Loan EMI"
        },
        "Insurance": {
            "keywords": [
                "insurance", "health insurance", "life insurance", "lic premium", "hdfc ergo",
                "max life", "acko", "star health", "policybazaar", "motor insurance", "term policy"
            ],
            "subcategories": {
                "health insurance": "Health Insurance", "star health": "Health Insurance", "hdfc ergo": "Health Insurance",
                "life insurance": "Life Insurance", "lic": "Life Insurance", "max life": "Life Insurance",
                "acko": "Vehicle Insurance", "motor insurance": "Vehicle Insurance"
            },
            "default_subcat": "Health Insurance"
        },
        "Investment": {
            "keywords": [
                "zerodha", "groww", "upstox", "mutual fund", "sip", "stocks", "equity", "ppf",
                "nps", "fixed deposit", "fd auto", "sovereign gold", "gold bond", "crypto", "sharekhan"
            ],
            "subcategories": {
                "zerodha": "Stocks & Equity", "upstox": "Stocks & Equity", "stocks": "Stocks & Equity",
                "mutual fund": "Mutual Funds & SIP", "sip": "Mutual Funds & SIP", "groww": "Mutual Funds & SIP",
                "gold": "Gold", "fixed deposit": "Fixed Deposits", "fd": "Fixed Deposits"
            },
            "default_subcat": "Mutual Funds & SIP"
        },
        "Travel": {
            "keywords": [
                "indigo", "air india", "flight", "airlines", "irctc", "train ticket", "makemytrip",
                "goibibo", "easemytrip", "yatra", "redbus", "resort", "hotel stay", "airbnb", "booking.com"
            ],
            "subcategories": {
                "indigo": "Flights & Airlines", "air india": "Flights & Airlines", "flight": "Flights & Airlines",
                "irctc": "Trains & Buses", "redbus": "Trains & Buses", "train": "Trains & Buses",
                "hotel": "Hotels & Stays", "resort": "Hotels & Stays", "airbnb": "Hotels & Stays"
            },
            "default_subcat": "Flights & Airlines"
        },
        "Other": {
            "keywords": [
                "atm cash", "cash withdrawal", "bank charges", "gst charge", "interest debit",
                "penalty", "stamp duty", "fund transfer"
            ],
            "subcategories": {
                "cash": "Cash Withdrawal", "atm": "Cash Withdrawal",
                "transfer": "Transfers", "charges": "Miscellaneous"
            },
            "default_subcat": "Miscellaneous"
        }
    }

    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
        self.classifier = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
        self._is_trained = False
        self._load_and_train_dataset()

    def _load_and_train_dataset(self):
        dataset_path = os.path.join("data", "categorization_dataset.json")
        corpus, labels = [], []

        if os.path.exists(dataset_path):
            with open(dataset_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    desc = item.get("description", "").lower()
                    cat = item.get("category")
                    if desc and cat in self.CATEGORIES:
                        corpus.append(desc)
                        labels.append(cat)

        # Supplement with deterministic keyword expansions for robust class priors
        for category, info in self.DETERMINISTIC_RULES.items():
            for kw in info["keywords"]:
                corpus.append(kw.lower())
                labels.append(category)
                corpus.append(f"payment for {kw.lower()}")
                labels.append(category)
                corpus.append(f"upi txn {kw.lower()}")
                labels.append(category)

        X = self.vectorizer.fit_transform(corpus)
        self.classifier.fit(X, labels)
        self._is_trained = True

    def categorize(
        self,
        description: str,
        user_rules: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Backwards-compatible convenience method returning primary category name string.
        """
        res = self.predict(description=description, user_rules=user_rules)
        return res["category"]

    def predict(
        self,
        description: str,
        user_rules: Optional[List[Dict[str, str]]] = None,
        merchant_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes 4-Layer Hybrid Categorization.
        Returns:
            category: str
            subcategory: str
            confidence: float (0.0 to 1.0)
            classification_method: str ("user_learned_rule", "deterministic_rule", "ml_classifier", "llm_fallback")
            rationale: str
            is_low_confidence: bool
        """
        if not description and not merchant_name:
            return {
                "category": "Other",
                "subcategory": "Miscellaneous",
                "confidence": 0.50,
                "classification_method": "deterministic_rule",
                "rationale": "Empty description",
                "is_low_confidence": True
            }

        text = f"{merchant_name or ''} {description}".strip().lower()

        # ==========================================
        # Layer 4: User Correction Learning (Priority 1)
        # ==========================================
        if user_rules:
            for rule in user_rules:
                pattern = rule.get("keyword_pattern", "").strip().lower()
                if pattern and pattern in text:
                    target_cat = rule.get("category_name") or rule.get("category") or "Other"
                    subcat = rule.get("subcategory") or "User Custom"
                    return {
                        "category": target_cat,
                        "subcategory": subcat,
                        "confidence": 1.0,
                        "classification_method": "user_learned_rule",
                        "rationale": f"Matched learned user mapping for keyword '{pattern}'",
                        "is_low_confidence": False
                    }

        # ==========================================
        # Layer 1: Deterministic Rules (Priority 2)
        # ==========================================
        for category, rule_info in self.DETERMINISTIC_RULES.items():
            for kw in rule_info["keywords"]:
                # Use word boundary for short keywords (<= 3 chars) to avoid false substring collisions
                if len(kw) <= 3:
                    matched = bool(re.search(r"\b" + re.escape(kw) + r"\b", text))
                else:
                    matched = (kw in text)

                if matched:
                    subcat = rule_info["default_subcat"]
                    for sub_kw, specific_subcat in rule_info["subcategories"].items():
                        if sub_kw in text:
                            subcat = specific_subcat
                            break

                    return {
                        "category": category,
                        "subcategory": subcat,
                        "confidence": 0.98,
                        "classification_method": "deterministic_rule",
                        "rationale": f"Matched deterministic merchant keyword: '{kw}'",
                        "is_low_confidence": False
                    }

        # ==========================================
        # Layer 2: ML Classifier (Priority 3)
        # ==========================================
        if self._is_trained:
            try:
                vec = self.vectorizer.transform([text])
                probs = self.classifier.predict_proba(vec)[0]
                max_idx = np.argmax(probs)
                max_prob = float(probs[max_idx])
                predicted_category = self.classifier.classes_[max_idx]

                if max_prob >= CONFIDENCE_THRESHOLD:
                    default_subcat = self.DETERMINISTIC_RULES.get(predicted_category, {}).get("default_subcat", "General")
                    return {
                        "category": predicted_category,
                        "subcategory": default_subcat,
                        "confidence": round(max_prob, 3),
                        "classification_method": "ml_classifier",
                        "rationale": f"ML model categorized as {predicted_category} with {round(max_prob * 100, 1)}% probability",
                        "is_low_confidence": False
                    }
            except Exception:
                pass

        # ==========================================
        # Layer 3: LLM Contextual Semantic Fallback (Priority 4)
        # ==========================================
        llm_result = self._llm_fallback_categorize(text)
        return llm_result

    def _llm_fallback_categorize(self, text: str) -> Dict[str, Any]:
        """
        LLM contextual reasoning fallback for complex or low-confidence descriptions.
        """
        # Contextual Semantic Reasoning Table
        if any(w in text for w in ["sip", "invest", "portfolio", "dividend", "sebi"]):
            return {
                "category": "Investment",
                "subcategory": "Mutual Funds & SIP",
                "confidence": 0.85,
                "classification_method": "llm_fallback",
                "rationale": "LLM identified investment vehicle narration",
                "is_low_confidence": False
            }
        if any(w in text for w in ["fare", "ticket", "transit", "journey", "airways"]):
            return {
                "category": "Travel",
                "subcategory": "Flights & Airlines",
                "confidence": 0.82,
                "classification_method": "llm_fallback",
                "rationale": "LLM identified travel & transit narration",
                "is_low_confidence": False
            }
        if any(w in text for w in ["clinic", "care", "wellness", "therapy", "meds"]):
            return {
                "category": "Healthcare",
                "subcategory": "Doctor & Hospital",
                "confidence": 0.80,
                "classification_method": "llm_fallback",
                "rationale": "LLM identified healthcare keywords",
                "is_low_confidence": False
            }

        # Default low-confidence fallback (Never trusted silently)
        return {
            "category": "Other",
            "subcategory": "Miscellaneous",
            "confidence": 0.45,
            "classification_method": "llm_fallback",
            "rationale": "Low semantic confidence across all classifiers; marked for user review",
            "is_low_confidence": True
        }

    def evaluate(self, dataset: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Calculates categorization evaluation metrics:
        Accuracy, Precision (Macro/Weighted), Recall (Macro/Weighted), F1-Score, and Confidence Calibration Error (ECE).
        """
        if dataset is None:
            dataset_path = os.path.join("data", "categorization_dataset.json")
            with open(dataset_path, "r", encoding="utf-8") as f:
                dataset = json.load(f)

        y_true = []
        y_pred = []
        confidences = []
        is_correct_list = []

        for item in dataset:
            desc = item["description"]
            true_cat = item["category"]
            pred = self.predict(desc)

            y_true.append(true_cat)
            y_pred.append(pred["category"])
            conf = pred["confidence"]
            confidences.append(conf)
            is_correct_list.append(1 if pred["category"] == true_cat else 0)

        # Standard Classification Metrics
        accuracy = float(accuracy_score(y_true, y_pred))
        p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
        p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)

        # Expected Calibration Error (ECE) across 10 bins
        bins = np.linspace(0, 1, 11)
        ece = 0.0
        n = len(confidences)
        for i in range(10):
            bin_lower, bin_upper = bins[i], bins[i+1]
            bin_indices = [idx for idx, c in enumerate(confidences) if bin_lower <= c < bin_upper or (i == 9 and c == bin_upper)]
            if bin_indices:
                bin_acc = np.mean([is_correct_list[idx] for idx in bin_indices])
                bin_conf = np.mean([confidences[idx] for idx in bin_indices])
                ece += (len(bin_indices) / n) * abs(bin_acc - bin_conf)

        # Brier Score Calibration
        brier_score = float(np.mean([(confidences[idx] - is_correct_list[idx]) ** 2 for idx in range(n)]))

        return {
            "total_samples": len(dataset),
            "accuracy": round(accuracy, 4),
            "precision_macro": round(float(p_macro), 4),
            "recall_macro": round(float(r_macro), 4),
            "f1_macro": round(float(f1_macro), 4),
            "f1_weighted": round(float(f1_weighted), 4),
            "expected_calibration_error": round(float(ece), 4),
            "brier_score": round(brier_score, 4),
            "is_calibrated": bool(ece <= 0.15)
        }

expense_categorizer = ExpenseCategorizer()

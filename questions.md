# OpenRouter System One Sample Decision Questions

A curated collection of production-ready decision payloads for OpenRouter System One decision models (`inception/mercury-decide:free`, `inception/mercury-decide`, `typesafe/jev-1.13`).

You can copy and paste any of these JSON payloads directly into the **Raw JSON Schema Mode** tab in the Streamlit application.

---

## 1. Customer Support & IT Incident Triage
**Use Case:** Automatically classify inbound support tickets, route to the proper team, and assess incident severity.

```json
{
  "model": "inception/mercury-decide:free",
  "state": "Hi, I've been trying to connect my Stripe account for 3 days and it keeps failing. I'm losing sales. Please help ASAP.",
  "questions": {
    "is_revenue_impacting": {
      "type": "noul",
      "instructions": "Does this issue directly impede the customer from earning revenue or completing transactions?",
      "criteria": {
        "true": "Customer explicitly reports losing sales or failing checkout transactions.",
        "false": "General account question, cosmetic issue, or non-blocking inquiry."
      }
    },
    "assigned_team": {
      "type": "choice",
      "instructions": "Which department should own and resolve this ticket?",
      "criteria": {
        "payments_integration": "Payment gateway setup, Stripe connection, and webhook failures.",
        "billing_invoicing": "Customer subscription plans, invoice charges, and credit card receipts.",
        "account_access": "Login credentials, password resets, and 2FA authentication.",
        "general_support": "How-to questions, product documentation, and feature feedback."
      }
    },
    "customer_frustration": {
      "type": "score",
      "instructions": "Assess the emotional frustration and urgency conveyed in the ticket.",
      "criteria": [
        "Level 1: Calm or routine inquiry",
        "Level 2: Mild inconvenience",
        "Level 3: Noticeably frustrated with delays",
        "Level 4: Urgent distress and actively reporting lost sales",
        "Level 5: Extreme outrage / immediate churn threat"
      ]
    }
  }
}
```

---

## 2. Autonomous Agent Tool Execution Guardrail
**Use Case:** Safety gate to allow, require human confirmation, or block tool calls by AI coding and operations agents.

```json
{
  "model": "inception/mercury-decide:free",
  "state": "Agent Goal: Clean up old database records before month end.\nProposed Action: execute_sql(\"DROP TABLE audit_logs_2025;\")\nEnvironment: Production US-East-1 Database Cluster (Replica 2)",
  "questions": {
    "is_destructive": {
      "type": "noul",
      "instructions": "Does this proposed operation delete, drop, or permanently alter production records without an undo path?",
      "criteria": {
        "true": "Permanent deletion, table drops, or unbacked data mutations.",
        "false": "Read-only query, staging operation, or reversible schema alteration."
      }
    },
    "violates_safety_policy": {
      "type": "noul",
      "instructions": "Does running a DROP statement directly on a production database violate standard change management policies?"
    },
    "execution_policy": {
      "type": "choice",
      "instructions": "What policy should the agent executor enforce?",
      "criteria": {
        "auto_approve": "Safe operation; run automatically without human intervention.",
        "require_human_signoff": "High impact; pause and request human supervisor approval.",
        "block_and_alert": "Dangerous command; terminate tool execution immediately and alert security."
      }
    }
  }
}
```

---

## 3. FinTech Loan Application & Credit Risk Assessment
**Use Case:** Underwriting decisioning for personal and business loan applications.

```json
{
  "model": "inception/mercury-decide:free",
  "state": {
    "applicant_name": "Jordan Miller",
    "credit_score": 780,
    "annual_income": 120000,
    "monthly_debt_obligations": 1500,
    "requested_loan_amount": 50000,
    "loan_purpose": "Home Improvement",
    "bankruptcies_past_7_years": 0
  },
  "questions": {
    "meets_prime_underwriting": {
      "type": "noul",
      "instructions": "Does the applicant satisfy prime credit underwriting criteria based on debt-to-income and credit score?",
      "criteria": {
        "true": "Credit score >= 720 and debt-to-income ratio <= 35%.",
        "false": "Credit score < 720 or high debt obligations relative to income."
      }
    },
    "risk_classification": {
      "type": "choice",
      "instructions": "What risk category should this loan application be placed in?",
      "criteria": {
        "tier_a_prime": "Excellent credit history, strong cash flow, low default risk.",
        "tier_b_near_prime": "Adequate credit history with minor risk factors.",
        "tier_c_subprime": "High debt ratio, recent delinquencies, or weak credit.",
        "auto_decline": "Severe credit disqualifications or active bankruptcies."
      }
    },
    "interest_rate_tier": {
      "type": "score",
      "instructions": "Select the appropriate APR interest rate bucket from lowest to highest.",
      "criteria": [
        "Tier 1: Preferred Prime APR (5.99% - 7.49%)",
        "Tier 2: Standard APR (7.50% - 9.99%)",
        "Tier 3: Moderate Risk APR (10.00% - 13.99%)",
        "Tier 4: High Risk APR (14.00% - 18.99%)"
      ]
    }
  }
}
```

---

## 4. Inbound Enterprise Sales Lead Qualification (B2B)
**Use Case:** Score marketing leads and assign dedicated enterprise account executives vs self-serve onboarding.

```json
{
  "model": "inception/mercury-decide:free",
  "state": {
    "company": "Nova Robotics Inc",
    "employees": 650,
    "annual_revenue": "$85M",
    "contact_title": "Head of Engineering",
    "inquiry_body": "We are migrating 40 microservices to Kubernetes and looking to purchase an annual enterprise license for your observability platform. We need SOC2 Type II compliance and SSO integration within 30 days."
  },
  "questions": {
    "has_budget_authority": {
      "type": "noul",
      "instructions": "Does the contact title indicate budget holding or technical purchasing authority?",
      "criteria": {
        "true": "Director, VP, Head of Engineering, or C-suite executive.",
        "false": "Individual contributor, student, or unverified contact."
      }
    },
    "recommended_sales_motion": {
      "type": "choice",
      "instructions": "What sales motion is appropriate for this prospect?",
      "criteria": {
        "direct_enterprise_ae": "Assign senior Account Executive with custom contract and demo.",
        "inside_sales": "Mid-market sales rep for standard multi-seat subscription.",
        "self_serve_trial": "Send automated link to self-serve 14-day free trial."
      }
    },
    "lead_fit_score": {
      "type": "score",
      "instructions": "Score the fit against our ideal customer profile (ICP) and purchase timeline.",
      "criteria": [
        "0: Poor fit / No immediate buying timeline",
        "1: Moderate fit / Exploratory interest",
        "2: Strong ICP / Buying timeline within 60 days",
        "3: High-Priority Whale / Immediate 30-day enterprise requirement"
      ]
    }
  }
}
```

---

## 5. E-Commerce Fraud & Refund Claim Decisioning
**Use Case:** Decide whether an incoming refund request is legitimate, requires return verification, or is fraudulent.

```json
{
  "model": "inception/mercury-decide:free",
  "state": {
    "account_age_days": 14,
    "orders_completed": 1,
    "claimed_item": "Apple MacBook Pro 16-inch ($2,499)",
    "claim_reason": "Package reported empty upon delivery",
    "carrier_proof_of_delivery": "Photo shows intact parcel weighing 4.8 lbs delivered to front porch",
    "customer_ip_country": "United States",
    "shipping_address_matches_billing": false
  },
  "questions": {
    "suspicion_of_fraud": {
      "type": "noul",
      "instructions": "Is there a high likelihood of fraudulent claim or package interception based on delivery weight and account age?",
      "criteria": {
        "true": "Carrier delivered verified parcel weight but customer claims empty box on new account.",
        "false": "Established customer with consistent ordering history."
      }
    },
    "claim_disposition": {
      "type": "choice",
      "instructions": "What resolution should the claim system execute?",
      "criteria": {
        "approve_immediate_refund": "Low risk; issue refund to original payment method.",
        "require_police_report": "High value claim; mandate official stolen package report before review.",
        "deny_and_blacklist": "Confirmatory evidence of fraud; deny claim and freeze account."
      }
    }
  }
}
```

---

## 6. Social Media & Community Content Moderation
**Use Case:** Evaluate user submissions for spam, phishing, hate speech, and platform policy adherence.

```json
{
  "model": "inception/mercury-decide:free",
  "state": "Post Content: 'ATTENTION ALL INVESTORS! The secret presale for MetaToken is live right now! Deposit 0.1 ETH to our verified contract at 0x9f82... and double your tokens in 10 minutes! Limited to the first 50 wallets: http://bit.ly/meta-presale-fast'",
  "questions": {
    "is_scam_or_phishing": {
      "type": "noul",
      "instructions": "Does this post advertise a fraudulent scheme, wallet drainer, or deceptive crypto giveaway?",
      "criteria": {
        "true": "Promises unrealistic financial returns, unverified contracts, or shortened links.",
        "false": "Legitimate discussion, questions, or non-deceptive community content."
      }
    },
    "moderation_verdict": {
      "type": "choice",
      "instructions": "What enforcement action should be applied to this post and user?",
      "criteria": {
        "allow_post": "Content complies with community guidelines.",
        "flag_for_review": "Borderline content; place in moderator queue.",
        "auto_delete_and_ban": "Direct violation; remove post instantly and suspend user account."
      }
    }
  }
}
```

---

## 7. Healthcare Patient Triage & Telehealth Routing
**Use Case:** Route incoming patient symptom descriptions to appropriate clinical urgency tiers.

```json
{
  "model": "inception/mercury-decide:free",
  "state": "Patient Message: 'I am experiencing sudden crushing tightness in my chest that radiates to my left jaw, accompanied by shortness of breath and sweating for the last 20 minutes.'",
  "questions": {
    "requires_emergency_services": {
      "type": "noul",
      "instructions": "Does the patient report symptoms consistent with an acute life-threatening emergency requiring immediate emergency response?",
      "criteria": {
        "true": "Classic signs of myocardial infarction, stroke, or airway compromise.",
        "false": "Non-emergency chronic symptoms or routine medical question."
      }
    },
    "recommended_care_setting": {
      "type": "choice",
      "instructions": "Where should the patient be directed for care?",
      "criteria": {
        "emergency_department": "Call 911 / Go to nearest Hospital Emergency Room immediately.",
        "urgent_care": "Same-day walk-in clinic for acute non-life-threatening ailments.",
        "primary_care_appointment": "Schedule routine appointment with primary care physician.",
        "self_care_home": "Over-the-counter remedy and home observation."
      }
    },
    "clinical_urgency_score": {
      "type": "score",
      "instructions": "Score patient acuity on the Emergency Severity Index (ESI) scale.",
      "criteria": [
        "ESI 5: Non-urgent (prescription refill, suture removal)",
        "ESI 4: Less urgent (mild rash, chronic pain)",
        "ESI 3: Urgent (moderate fever, stable abdominal pain)",
        "ESI 2: Emergent (high risk, severe pain, confused)",
        "ESI 1: Resuscitation / Immediate life-threat"
      ]
    }
  }
}
```

"""Pre-configured test presets for OpenRouter System One decision models."""
from typing import Dict, Any

PRESETS: Dict[str, Dict[str, Any]] = {
    "agent_guardrail": {
        "title": "🛡️ Agent Guardrail (Tool Call Gating)",
        "description": "Evaluates whether an autonomous agent tool call is destructive and requires human oversight.",
        "state": (
            "Task: clean up inactive accounts before the quarterly report.\n"
            "Proposed tool call:\n"
            "delete_rows(table=\"customers\", where=\"last_login < 2023-01-01\")\n"
            "Context: the customer database contains 420,000 rows across 12 shards."
        ),
        "questions": {
            "is_destructive": {
                "type": "noul",
                "instructions": "Does this tool call perform an irreversible or destructive data deletion without backup?",
                "criteria": {
                    "true": "Deletes or alters user/system data irreversibly.",
                    "false": "Read-only query or safe, reversible modification."
                }
            },
            "gate_approval": {
                "type": "choice",
                "instructions": "What execution policy should the agent execute?",
                "criteria": {
                    "allow": "Execute automatically without user prompt.",
                    "require_confirmation": "Prompt human operator with confirmation dialog.",
                    "block": "Block execution immediately and log security violation."
                }
            }
        }
    },
    "support_routing": {
        "title": "🎧 Customer Support Triage & Routing",
        "description": "Multi-question triage: classifies ticket type, dispatches to team, and rates urgency.",
        "state": {
            "customer_tier": "enterprise",
            "account_arr": "$120,000",
            "subject": "Checkout page blank screen on clicking Pay",
            "ticket": "My checkout page shows a blank white screen after I click Pay. I have reproduced this on both Chrome and Firefox. We have active customers failing checkout transactions right now."
        },
        "questions": {
            "is_bug": {
                "type": "noul",
                "instructions": "Is the customer reporting a software defect or broken functionality?",
                "criteria": {
                    "true": "Customer describes broken product functionality or system error.",
                    "false": "Customer is asking a question, how-to guide, or feature request."
                }
            },
            "team": {
                "type": "choice",
                "instructions": "Which specialized team should own this ticket?",
                "criteria": {
                    "payments": "Checkout, billing, invoice disputes, or payment processing errors.",
                    "frontend": "Rendering, UI layout, browser compatibility, or client side errors.",
                    "account": "Login, SSO, authentication, permissions, or profile settings."
                }
            },
            "urgency": {
                "type": "score",
                "instructions": "How urgent is this incident based on revenue and business impact?",
                "criteria": [
                    "Low: Can wait for normal scheduled release",
                    "Medium: Degraded experience, resolve during business week",
                    "Critical: Revenue-blocking outage requiring immediate escalation"
                ]
            }
        }
    },
    "lead_qualification": {
        "title": "📈 Inbound Lead Qualification & Tier Assignment",
        "description": "Scores sales prospects on an ordinal rubric and assigns optimal service tier.",
        "state": {
            "company": "Fintech Global Inc",
            "headcount": 450,
            "annual_revenue": "$65M",
            "inbound_contact_title": "VP of Engineering",
            "inquiry": "We process 15 million automated agent decisions per day and need sub-50ms latency. We want to migrate from slow LLMs to System One decision models immediately this quarter."
        },
        "questions": {
            "qualification_score": {
                "type": "score",
                "instructions": "How well does this prospect match our ideal customer profile (ICP)?",
                "criteria": [
                    "Unqualified: Low volume, low budget, or mismatched architecture",
                    "Potential: Moderate volume or exploratory timeline",
                    "High-Priority ICP: High enterprise volume, budget, and immediate Q-timeline"
                ]
            },
            "service_tier": {
                "type": "choice",
                "instructions": "Which service deployment architecture should be recommended?",
                "criteria": {
                    "self_serve": "Standard API keys with public pooled rate limits",
                    "dedicated_cluster": "Dedicated inference worker pool with custom SLA",
                    "enterprise_vpc": "Private VPC peering with guaranteed throughput and 99.99% SLA"
                }
            }
        }
    },
    "content_safety": {
        "title": "🛡️ Content Safety & Phishing Moderation",
        "description": "Detects crypto spam / phishing and determines moderation enforcement action.",
        "state": (
            "User message in public community channel:\n"
            "\"URGENT: Flash giveaway! Double your ETH in 15 minutes! "
            "Send 0.05 to 2.0 ETH to contract 0x7382910... and receive double back instantly. "
            "Only 50 slots left! Claim now: https://bit.ly/crypto-fast-airdrop\""
        ),
        "questions": {
            "is_phishing_scam": {
                "type": "noul",
                "instructions": "Does this message constitute a financial scam, wallet drainer, or phishing attempt?",
                "criteria": {
                    "true": "Deceptive scheme promising fraudulent returns or phishing link.",
                    "false": "Legitimate announcement or ordinary conversation."
                }
            },
            "enforcement_action": {
                "type": "choice",
                "instructions": "What moderation action should be applied to this user account?",
                "criteria": {
                    "allow": "Content is harmless; allow publication.",
                    "quarantine": "Flag message for manual human review before display.",
                    "immediate_ban": "Delete content immediately and suspend the offending account."
                }
            }
        }
    }
}

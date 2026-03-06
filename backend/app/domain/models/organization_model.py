from datetime import datetime


class OrganizationModel:

    @staticmethod
    def build(name: str, plan: str = "FREE"):
        token_limit = 100000

        if plan == "PRO":
            token_limit = 500000
        elif plan == "ENTERPRISE":
            token_limit = 2000000

        return {
            "name": name,
            "plan": plan,  # FREE | PRO | ENTERPRISE
            "monthly_token_limit": token_limit,
            "policy_config": {
                "risk_threshold": 0.7,
                "block_partial_support": False,
            },
            "model_config": {
                "free_model": "mistralai/mistral-7b-instruct",
                "pro_model": "deepseek/deepseek-chat",
                "enterprise_model": "openai/gpt-4o"
            },
            "created_at": datetime.utcnow(),
        }
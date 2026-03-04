class RetailPipeline:
    def run(self, app):
        score = app["cibil_score"] - app["foir_post_loan"]
        ltv   = app.get("ltv_ratio", 70)
        risk  = "LOW" if score > 680 and ltv < 75 else "MEDIUM" if score > 600 else "HIGH"
        decision = "APPROVED" if risk == "LOW" else "REVIEW" if risk == "MEDIUM" else "REJECTED"
        return {**app, "risk": risk, "decision": decision,
                "lead_score": round(min(100, score/8), 1),
                "recommended_rate": 8.5 if risk=="LOW" else 10.5 if risk=="MEDIUM" else 13.5}

class SMEPipeline:
    def run(self, app):
        score = app["cibil_score"] + app["dscr"]*40 + app.get("vintage_years",5)*3
        risk  = "LOW" if score > 850 else "MEDIUM" if score > 750 else "HIGH"
        decision = "APPROVED" if risk == "LOW" else "REVIEW" if risk == "MEDIUM" else "REJECTED"
        return {**app, "risk": risk, "decision": decision,
                "financial_health_score": round(min(100, score/10), 1),
                "recommended_rate": 9.0 if risk=="LOW" else 11.5 if risk=="MEDIUM" else 14.5}

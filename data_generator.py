import random

def generate_retail_samples(n=200):
    data = []
    for i in range(n):
        data.append({
            "id": f"R{i}",
            "name": f"Retail_User_{i}",
            "city": random.choice(["Bengaluru","Mumbai","Delhi","Hyderabad"]),
            "employment_type": random.choice(["Salaried","Self Employed"]),
            "loan_amt": random.randint(5,50)*100000,
            "loan_purpose": random.choice(["Home","Car","Personal"]),
            "cibil_score": random.randint(650,800),
            "foir_post_loan": random.uniform(25,50),
            "ltv_ratio": random.uniform(60,85)
        })
    return data

def generate_sme_samples(n=150):
    data = []
    for i in range(n):
        data.append({
            "id": f"S{i}",
            "name": f"SME_Firm_{i}",
            "city": random.choice(["Bengaluru","Mumbai","Delhi"]),
            "industry": random.choice(["IT","Retail","Manufacturing"]),
            "loan_amt": random.randint(10,100)*100000,
            "cibil_score": random.randint(650,800),
            "dscr": random.uniform(1.2,2.0),
            "ltv_ratio": random.uniform(55,80)
        })
    return data

import json
import random
import numpy as np

# name_origin, ethnicity, age_group
ethnicities = ["Caucasian", "African American", "East Asian", "South Asian", "Middle Eastern", "Hispanic"]

names_by_eth = {
    "Caucasian": ["James", "John", "Sarah", "Emily", "Robert", "Emma"],
    "African American": ["Jamal", "Lakisha", "Darius", "Marcus", "Aaliyah", "Malik"],
    "East Asian": ["Wei", "Li", "Min", "Ji-hoon", "Yuki", "Kenji"],
    "South Asian": ["Aisha", "Priya", "Rahul", "Amit", "Kavita", "Raj"],
    "Middle Eastern": ["Mohammed", "Fatima", "Omar", "Amina", "Ali", "Hassan"],
    "Hispanic": ["Carlos", "Maria", "Jose", "Ana", "Luis", "Sofia"]
}

candidates = []
for _ in range(5000):
    eth = random.choice(ethnicities)
    name = random.choice(names_by_eth[eth]) + " " + random.choice(["Smith", "Johnson", "Davis", "Chen", "Patel", "Khan", "Garcia"])
    
    # Normal distribution for experience and GPA
    exp = max(0, min(10, np.random.normal(5, 2)))
    gpa = max(2.0, min(4.0, np.random.normal(3.3, 0.4)))
    
    # Age normally distributed around 35
    age = int(max(20, min(65, np.random.normal(35, 10))))
    
    candidates.append({
        "name": name,
        "age": age,
        "ethnicity": eth,
        "experience": round(exp, 1),
        "gpa": round(gpa, 2)
    })

with open("demo_candidates.json", "w") as f:
    json.dump(candidates, f, indent=2)

print("Generated 5000 nicely distributed candidates!")

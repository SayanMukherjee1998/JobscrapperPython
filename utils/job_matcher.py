import re

def calculate_match_score(description, resume_skills):
    score = 0
    desc_lower = (description or "").lower()
    for skill, weight in resume_skills.items():
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', desc_lower):
            score += weight
    return score

def extract_salary(description):
    patterns = [
        r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)\s*LPA',
        r'₹?\s*(\d+\.?\d*)\s*-\s*(\d+\.?\d*)\s*lakhs?'
    ]
    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return float(match.group(2))
    return 0

def extract_experience(description):
    """
    Extracts minimum years of experience required from the job description.
    Returns an integer (years), or 0 if not found.
    """
    if not description:
        return 0
    # Common patterns: "3+ years", "at least 3 years", "minimum 3 years", etc.
    match = re.search(r'(\d+)\s*\+?\s*(?:years?|yrs?)', description, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0

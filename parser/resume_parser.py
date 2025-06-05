import re
from collections import Counter
from config import RESUME_PATH

TECH_KEYWORDS = [
    'python', 'aws', 'docker', 'react', 'angular', 'node.js', 'postgresql',
    'mysql', 'mongodb', 'git', 'jenkins', 'linux', 'rest api', 'graphql',
    'typescript', 'sql', 'nosql', 'ci/cd', 'javascript', 'html', 'css'
]

def extract_resume_skills(path=RESUME_PATH):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read().lower()

    counts = Counter()
    for skill in TECH_KEYWORDS:
        pattern = r'(?<!\w)' + re.escape(skill) + r'(?!\w)'
        matches = re.findall(pattern, text)
        if matches:
            counts[skill] = len(matches)

    max_count = max(counts.values(), default=1)
    scaled = {
        skill.capitalize(): min(round((count / max_count) * 3), 3)
        for skill, count in counts.items()
    }
    return scaled

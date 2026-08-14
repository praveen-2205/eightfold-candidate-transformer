
SKILL_ALIASES = {
        "tensorflow": "TensorFlow", "tf": "TensorFlow",
    "react": "React", "reactjs": "React", "react.js": "React",
    "kubernetes": "Kubernetes", "kubernets": "Kubernetes", "k8s": "Kubernetes",
    "amazon web services": "AWS", "aws": "AWS",
    "pytorch": "PyTorch", "opencv": "OpenCV",
    "fastapi": "FastAPI", "langgraph": "LangGraph",
    "langchain": "LangChain", "github": "GitHub",
    "neo4j": "Neo4j", "sql": "SQL", "nlp": "NLP",
    "spacy": "spaCy", "scipy": "SciPy", "numpy": "NumPy",
    "pandas": "pandas", "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn", "llm": "LLM", "llms": "LLMs",
    "python": "Python", "java": "Java", "c++": "C++", "c": "C"
}

def canonical_skill(raw_skill: str) -> str | None:
    if not raw_skill:
        return None
    cleaned = raw_skill.strip().lower()
    if cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[cleaned]
    return raw_skill.strip().title()

def is_known(raw_skill: str) -> bool:
    if not raw_skill:
        return False
    return raw_skill.strip().lower() in SKILL_ALIASES

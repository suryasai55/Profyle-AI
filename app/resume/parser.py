import os
import re
import PyPDF2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Define the skills repository and their regex matching patterns
SKILL_PATTERNS = {
    # Core Languages (Weight = 6 points each)
    'Python': (r'\bpython\b', 'Languages', 6),
    'Java': (r'\bjava\b', 'Languages', 6),
    'C++': (r'\bc\+\+(?!\w)', 'Languages', 6),
    'JavaScript': (r'\bjavascript\b|\bjs\b', 'Languages', 6),
    'SQL': (r'\bsql\b|\bmysql\b|\bpostgresql\b|\bsqlite\b', 'Languages', 6),
    'HTML': (r'\bhtml\b|\bhtml5\b', 'Languages', 6),
    'CSS': (r'\bcss\b|\bcss3\b', 'Languages', 6),
    
    # Tools & Frameworks (Weight = 6 points each)
    'React': (r'\breact\b|\breactjs\b|\breact\.js\b', 'Tools & Frameworks', 6),
    'Flask': (r'\bflask\b', 'Tools & Frameworks', 6),
    'Git': (r'\bgit\b|\bgithub\b|\bgitlab\b', 'Tools & Frameworks', 6),
    'Docker': (r'\bdocker\b', 'Tools & Frameworks', 6),
    'Jenkins': (r'\bjenkins\b', 'Tools & Frameworks', 6),
    
    # Cloud & Domain Fields (Weight = 7 points each)
    'AWS': (r'\baws\b|\bamazon web services\b|\bs3\b|\bec2\b', 'Cloud & Advanced Domains', 7),
    'Machine Learning': (r'\bmachine learning\b|\bml\b|\bsklearn\b|\btensorflow\b|\bpytorch\b', 'Cloud & Advanced Domains', 7),
    'NLP': (r'\bnlp\b|\bnatural language processing\b|\bnltk\b|\bspacy\b', 'Cloud & Advanced Domains', 7),
    'Data Science': (r'\bdata science\b|\bpandas\b|\bnumpy\b|\banalytics\b', 'Cloud & Advanced Domains', 7)
}

def extract_text_from_pdf(pdf_path):
    """Extracts raw text content from a PDF file using PyPDF2."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")
        
    text = ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        raise RuntimeError(f"PyPDF2 PDF Extraction error: {str(e)}")

def parse_resume(pdf_path, nltk_data_dir):
    """
    Parses a PDF resume to extract skills, calculate a weighted score,
    and returns a tuple: (score, detected_skills_list, missing_skills_list)
    """
    # 1. Ensure NLTK paths are loaded in the thread
    if nltk_data_dir not in nltk.data.path:
        nltk.data.path.insert(0, nltk_data_dir)
        
    # 2. Extract raw text
    raw_text = extract_text_from_pdf(pdf_path)
    
    # 3. Text cleaning & tokenization
    # Lowercase the entire text for case-insensitive scans
    cleaned_text = raw_text.lower()
    
    # Tokenize text using NLTK (to verify NLP pre-processing works)
    try:
        tokens = word_tokenize(cleaned_text)
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [w for w in tokens if w.isalnum() and w not in stop_words]
        # Re-join filtered tokens to form normalized text for keyword scan
        tokenized_processed_text = " ".join(filtered_tokens)
    except Exception as e:
        # Fallback to simple clean text if NLTK fails under some environment
        tokenized_processed_text = cleaned_text
        
    # 4. Scan for skills
    detected_skills = []
    missing_skills = []
    score = 0
    
    for skill, (pattern, category, weight) in SKILL_PATTERNS.items():
        # Match using word boundaries.
        # Note: We match on 'cleaned_text' because punctuation-retained text
        # is necessary to detect C++ or react.js, which tokenized_processed_text might strip.
        if re.search(pattern, cleaned_text):
            detected_skills.append(skill)
            score += weight
        else:
            missing_skills.append(skill)
            
    # Capping score at 100 just in case
    score = min(score, 100)
    
    return score, detected_skills, missing_skills

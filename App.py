import streamlit as st
import json
import requests  # Using direct HTTP requests for stability

# --- Configuration & CSS Injection ---
st.set_page_config(
    page_title="E-GEO Scorer",
    page_icon="📊",
    layout="wide"
)

# Injecting the exact CSS provided
st.markdown("""
<style>
    :root { --brand: #3182ce; --bg: #ffffff; }
    .stApp { background-color: var(--bg); font-family: sans-serif; }
    
    .user-bubble {
        background: #eebbbb;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 0px;
        margin-top: 5px;
        color: #2c3e50;
        font-size: 1.05rem;
        font-weight: 500;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        line-height: 1.5;
    }
    
    .translation-text {
        color: #718096;
        font-size: 0.9rem;
        font-style: italic;
        margin-top: 6px;
        margin-left: 5px;
        display: flex;
        align-items: center;
    }

    .intent-label {
        font-size: 0.75rem;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 5px;
        margin-top: 15px;
        font-weight: 700;
    }

    .container-box {
        margin-bottom: 25px;
        border-bottom: 1px solid #edf2f7;
        padding-bottom: 15px;
    }

    .score-big {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        line-height: 1;
    }
    
    .status-pass { color: #1a7f37; font-weight: bold; margin-right: 8px;}
    .status-fail { color: #cf222e; font-weight: bold; margin-right: 8px;}
</style>
""", unsafe_allow_html=True)

# --- Scoring Logic ---
GEO_CRITERIA = [
    "User Intent Alignment",
    "Competitive Differentiation", 
    "Social Proof / Reviews",
    "Compelling Narrative",
    "Authoritative Tone",
    "Unique Selling Points (USPs)",
    "Urgency / Call to Action",
    "Scannability (Formatting/Bullets)",
    "Factual Preservation"
]

def analyze_description_raw(api_key, text):
    """
    Uses standard Python 'requests' instead of the SDK to avoid connection errors.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    You are a strict judge for E-Commerce Product Descriptions based on the "E-GEO" academic paper.
    
    Score this description out of 100 based on these 9 criteria:
    {', '.join(GEO_CRITERIA)}
    
    Return ONLY valid JSON:
    {{
        "score": <integer>,
        "critique_summary": "<Short paragraph explaining the score>",
        "breakdown": {{
            "User Intent": {{ "status": "Pass" or "Fail", "comment": "..." }},
            "Competitive Differentiation": {{ "status": "Pass" or "Fail", "comment": "..." }},
            "Social Proof/Reviews": {{ "status": "Pass" or "Fail", "comment": "..." }},
            "Scannability/Format": {{ "status": "Pass" or "Fail", "comment": "..." }},
            "Call to Action": {{ "status": "Pass" or "Fail", "comment": "..." }}
        }}
    }}

    Description: "{text}"
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Return JSON only."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1
    }
    
    try:
        # 30 second timeout to prevent hanging
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            return json.loads(response.json()['choices'][0]['message']['content'])
        else:
            st.error(f"API Error ({response.status_code}): {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Connection Error: Could not reach Groq servers. Check your internet connection.")
        return None
    except requests.exceptions.Timeout:
        st.error("Timeout Error: The model took too long to respond.")
        return None
    except Exception as e:
        st.error(f"Unexpected Error: {e}")
        return None

# --- UI Layout ---

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Groq API Key", type="password")
    st.markdown("---")
    st.markdown("**Criteria:** E-GEO Paper (Table 3)")

st.title("E-GEO Content Judge")
st.markdown("Evaluate product descriptions against Generative Engine Optimization standards.")

if 'result' not in st.session_state:
    st.session_state.result = None

# Input
st.markdown('<div class="intent-label">INPUT DESCRIPTION</div>', unsafe_allow_html=True)
input_text = st.text_area("Paste description...", height=200, label_visibility="collapsed", placeholder="Paste description here...")

if st.button("Calculate Score", type="primary"):
    if not api_key:
        st.warning("Please provide a Groq API Key.")
    elif not input_text:
        st.warning("Please enter text.")
    else:
        with st.spinner("Judging content..."):
            st.session_state.result = analyze_description_raw(api_key, input_text)

# Results
if st.session_state.result:
    res = st.session_state.result
    score = res.get('score', 0)
    
    # Color Logic
    if score >= 80: score_color = "#1a7f37"
    elif score >= 50: score_color = "#d97706"
    else: score_color = "#cf222e"

    st.markdown('<div class="container-box">', unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 2])
    
    with c1:
        st.markdown('<div class="intent-label">GEO SCORE</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="score-big" style="color:{score_color}">{score}/100</p>', unsafe_allow_html=True)
    
    with c2:
        st.markdown('<div class="intent-label">JUDGE\'S FEEDBACK</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="user-bubble">
            {res.get('critique_summary')}
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

    # Breakdown
    st.markdown('<div class="intent-label">DETAILED PARAMETER BREAKDOWN</div>', unsafe_allow_html=True)
    
    breakdown = res.get('breakdown', {})
    for criteria, details in breakdown.items():
        status = details.get('status', 'Fail')
        comment = details.get('comment', '')
        
        status_class = "status-pass" if status == "Pass" else "status-fail"
        icon = "✅" if status == "Pass" else "⚠️"
        
        st.markdown(f"""
        <div style="background: #f6f8fa; padding: 10px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #e1e4e8;">
            <div style="font-size: 0.85rem; font-weight: 600; color: #24292e;">{criteria}</div>
            <div style="font-size: 0.95rem;">
                <span class="{status_class}">{icon} {status}</span>
                <span style="color: #586069;">{comment}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

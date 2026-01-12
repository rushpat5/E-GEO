import streamlit as st
import json
from groq import Groq

# --- Configuration & CSS Injection ---
st.set_page_config(
    page_title="E-GEO Evaluator",
    page_icon="🛒",
    layout="wide"
)

# Injecting the specific CSS provided + a complementary 'system' bubble
st.markdown("""
<style>
    :root { --brand: #3182ce; --bg: #ffffff; }
    .stApp { background-color: var(--bg); font-family: sans-serif; }
    
    /* User Bubble (Input/Original) */
    .user-bubble {
        background: #eebbbb; /* Light Red/Pink */
        padding: 15px 20px;
        border-radius: 18px 18px 18px 0px;
        margin-top: 5px;
        color: #2c3e50;
        font-size: 1.05rem;
        font-weight: 500;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        line-height: 1.5;
    }

    /* System Bubble (Output/Optimized) - Green variant to match theme */
    .system-bubble {
        background: #dcfce7; /* Light Green */
        padding: 15px 20px;
        border-radius: 18px 18px 0px 18px;
        margin-top: 5px;
        color: #14532d;
        font-size: 1.05rem;
        font-weight: 500;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        border: 1px solid #bbf7d0;
        line-height: 1.5;
    }
    
    .translation-text {
        color: #718096;
        font-size: 0.95rem;
        font-style: italic;
        margin-top: 8px;
        margin-left: 5px;
        display: flex;
        align-items: center;
    }

    .intent-label {
        font-size: 0.75rem;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
        margin-top: 20px;
        font-weight: 700;
    }

    .container-box {
        margin-bottom: 25px;
        border-bottom: 1px solid #edf2f7;
        padding-bottom: 15px;
    }

    /* Custom Score Badge */
    .score-badge {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        line-height: 1;
    }
</style>
""", unsafe_allow_html=True)

# --- Logic (Same as before) ---
GEO_CRITERIA = [
    "User Intent Alignment", "Competitive Differentiation", "Social Proof / Reviews",
    "Compelling Narrative", "Authoritative Tone", "Unique Selling Points (USPs)",
    "Urgency / Call to Action", "Scannability (Formatting)", "Factual Preservation"
]

OPTIMIZER_SYSTEM_PROMPT = """
You are an expert in Generative Engine Optimization (GEO). 
Based on the "Universally Effective Strategy", rewrite the product description to:
1. Highlight Unique Value Proposition.
2. Integrate SEO keywords & User Intent.
3. Add Social Proof.
4. Use Markdown (H2, H3, bullets) for scannability.
5. Be Authoritative yet Empathetic.
6. End with Urgency/Call to Action.
7. Maintain strict factual accuracy.
"""

def get_groq_client(api_key):
    return Groq(api_key=api_key)

def analyze_description(client, text):
    prompt = f"""
    Analyze this product description based on E-Commerce GEO principles ({', '.join(GEO_CRITERIA)}).
    Return a valid JSON object:
    {{
        "score": <0-100>,
        "analysis": {{
            "User Intent Alignment": {{ "present": <bool>, "feedback": "<string>" }},
            "Competitive Differentiation": {{ "present": <bool>, "feedback": "<string>" }},
            "Social Proof / Reviews": {{ "present": <bool>, "feedback": "<string>" }},
            "Compelling Narrative": {{ "present": <bool>, "feedback": "<string>" }},
            "Authoritative Tone": {{ "present": <bool>, "feedback": "<string>" }},
            "Unique Selling Points": {{ "present": <bool>, "feedback": "<string>" }},
            "Urgency / Call to Action": {{ "present": <bool>, "feedback": "<string>" }},
            "Scannability": {{ "present": <bool>, "feedback": "<string>" }},
            "Factual Preservation": {{ "present": <bool>, "feedback": "<string>" }}
        }},
        "summary_critique": "<string>"
    }}
    Description: "{text}"
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "JSON Output Only."}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}, temperature=0.3
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def optimize_description(client, text):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": OPTIMIZER_SYSTEM_PROMPT},
                {"role": "user", "content": f"Rewrite this description:\n\n{text}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# --- UI Layout ---

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Groq API Key", type="password")
    st.markdown("---")
    st.markdown("**Design Inspired by E-GEO Paper**")
    st.caption("Using Llama-3.3-70b")

st.title("Generative Engine Optimization")
st.markdown("Testbed for E-Commerce Description Optimization")

# Main Container
if 'analysis_result' not in st.session_state: st.session_state.analysis_result = None
if 'optimized_text' not in st.session_state: st.session_state.optimized_text = None

# Input Section
st.markdown('<div class="intent-label">ORIGINAL PRODUCT DESCRIPTION</div>', unsafe_allow_html=True)
input_text = st.text_area("Paste description...", height=150, label_visibility="collapsed")

if st.button("Analyze Content", type="primary"):
    if not api_key:
        st.warning("Please provide an API Key.")
    elif not input_text:
        st.warning("Please provide text.")
    else:
        client = get_groq_client(api_key)
        with st.spinner("Analyzing..."):
            st.session_state.analysis_result = analyze_description(client, input_text)
            st.session_state.optimized_text = None 

# Analysis Results
if st.session_state.analysis_result:
    res = st.session_state.analysis_result
    score = res.get('score', 0)
    score_color = "#1a7f37" if score >= 80 else "#d97706" if score >= 50 else "#dc2626"
    
    st.markdown('<div class="container-box">', unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 3])
    with c1:
        st.markdown('<div class="intent-label">GEO SCORE</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="score-badge" style="color:{score_color}">{score}</p>', unsafe_allow_html=True)
    
    with c2:
        st.markdown('<div class="intent-label">CRITIQUE</div>', unsafe_allow_html=True)
        # Using the user-bubble style for the critique text
        st.markdown(f"""
        <div class="user-bubble">
            {res.get('summary_critique')}
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

    # Criteria Grid
    with st.expander("View Detailed Criteria Breakdown"):
        for k, v in res.get('analysis', {}).items():
            icon = "✅" if v.get('present') else "❌"
            st.write(f"**{icon} {k}:** {v.get('feedback')}")

    # Optimization Action
    st.markdown('<div class="intent-label">OPTIMIZATION</div>', unsafe_allow_html=True)
    if st.button("✨ Generate Optimized Description"):
        client = get_groq_client(api_key)
        with st.spinner("Applying Universal Strategy..."):
            st.session_state.optimized_text = optimize_description(client, input_text)

# Optimized Output
if st.session_state.optimized_text:
    st.markdown(f"""
    <div class="intent-label">OPTIMIZED RESULT (E-GEO COMPLIANT)</div>
    <div class="system-bubble">
        {st.session_state.optimized_text.replace(chr(10), '<br>')}
    </div>
    <div class="translation-text">
        Generated using Llama-3.3 | Optimized for Scannability, Social Proof, and Intent.
    </div>
    """, unsafe_allow_html=True)

"""Streamlit interface for live customer review sentiment analysis."""

import streamlit as st

from api import analyze_review
from database import get_reviews, initialize_database, save_review

st.set_page_config(page_title="Review Pulse", page_icon="💬", layout="wide")
initialize_database()

st.markdown(
    """
    <style>
    .stApp { background: #211a1c; color: #f8edf0; }
    .block-container { max-width: 1420px; padding: 2rem 3rem 3rem; }
    [data-testid="stHeader"] { background: rgba(33, 26, 28, .96); }
    [data-testid="stToolbar"] { color: #f8edf0; }
    .hero { padding: 1.6rem 1.9rem; border: 1px solid #704746; border-radius: 16px;
            color: #fff7f5; background: linear-gradient(115deg, #39282b, #4a3033);
            margin-bottom: 1.5rem; }
    .hero h1 { margin: 0; font-size: 2rem; font-weight: 650; color: #f5ddd8; }
    .hero p { margin: .45rem 0 0; color: #eedde5; font-size: 1rem; }
    h1, h2, h3, h4, p, label, [data-testid="stMarkdownContainer"] { color: #f5e9eb; }
    h2, h3 { color: #f2c7bd; }
    [data-testid="stCaptionContainer"] { color: #d7c2c6; }
    [data-testid="stMetric"] { background: #302528; border: 1px solid #614346;
        padding: 1rem; border-radius: 13px; box-shadow: 0 3px 12px #120d0e70; }
    [data-testid="stMetricLabel"] { color: #e2cdd1; }
    [data-testid="stMetricValue"] { color: #fff4f2; }
    [data-testid="stTextArea"] textarea { background: #2b2225; color: #fff4f2;
        border: 1px solid #8e6263; caret-color: #f2c7bd; }
    [data-testid="stTextArea"] textarea::placeholder { color: #cbb5ba; opacity: 1; }
    [data-testid="stForm"] { background: #302528; border: 1px solid #614346;
        border-radius: 15px; padding: 1.3rem 1.4rem; }
    [data-testid="stBaseButton-primary"] { background: #995852; border-color: #995852; color: #fff8f6; }
    [data-testid="stBaseButton-primary"]:hover { background: #ad6e68; border-color: #ad6e68; color: #fff; }
    [data-testid="stDataFrame"] { border: 1px solid #614346; border-radius: 12px; overflow: hidden; }
    [data-testid="stDataFrame"] * { color: #f8edf0; }
    [data-testid="stAlert"] { background: #392c30; color: #fff4f2; border: 1px solid #765252; }
    [data-testid="stDivider"] { border-color: #634548; }
    hr { border-color: #634548; }
    @media (max-width: 900px) {
      .block-container { padding: 1.2rem 1rem 2rem; }
    }
    </style>
    <div class="hero"><h1>Review Pulse</h1>
    <p>A simple workspace for understanding customer feedback.</p></div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.35, 1], gap="large", vertical_alignment="top")
with left:
    st.subheader("Analyze a review")
    st.caption("Add a customer comment to identify its sentiment, score, and main topic.")
    with st.form("review_form", clear_on_submit=True):
        review_text = st.text_area(
            "Customer review",
            placeholder="For example: The food was delicious, but delivery took over an hour.",
            height=145,
            max_chars=5000,
        )
        submitted = st.form_submit_button("Analyze review", use_container_width=True, type="primary")

    if submitted:
        if not review_text.strip():
            st.warning("Please enter a review before analyzing.")
        else:
            try:
                with st.spinner("Reading the review…"):
                    result = analyze_review(review_text.strip())
                    save_review(review_text.strip(), result.label, result.score, result.theme)
                st.session_state["latest_analysis"] = {
                    "label": result.label,
                    "score": result.score,
                    "theme": result.theme,
                    "text": review_text.strip(),
                }
                st.success("Review analyzed and saved.")
            except Exception as exc:
                st.error(f"Could not analyze this review. Check your Gemini API key and connection. Details: {exc}")

with right:
    st.subheader("Feedback overview")
    rows = get_reviews()
    if rows:
        total = len(rows)
        positive = sum(row["label"].lower() == "positive" for row in rows)
        average = sum(row["score"] for row in rows) / total
        m1, m2, m3 = st.columns(3)
        m1.metric("Reviews saved", total)
        m2.metric("Positive", f"{positive} / {total}")
        m3.metric("Average score", f"{average:.1f} / 5")
    else:
        st.info("Your review totals and average score will appear here.")

    result = st.session_state.get("latest_analysis")
    if result:
        st.subheader("Latest analysis")
        st.markdown(f"**Review:** “{result['text']}”")
        c1, c2, c3 = st.columns(3)
        c1.metric("Sentiment", result["label"].title())
        c2.metric("Score", f"{result['score']} / 5")
        c3.metric("Topic", result["theme"].title())

st.divider()
st.subheader("Recent reviews")
st.caption("The 10 most recently analyzed reviews, newest first.")
rows = get_reviews()
if not rows:
    st.caption("No reviews yet. Analyze your first review above.")
else:
    st.dataframe(
        [
            {
                "Review": row["review_text"],
                "Sentiment": row["label"].title(),
                "Score": f"{row['score']} / 5",
                "Topic": row["theme"].title(),
                "Saved": row["created_at"],
            }
            for row in rows[:10]
        ],
        use_container_width=True,
        hide_index=True,
        column_config={"Review": st.column_config.TextColumn(width="large"), "Saved": st.column_config.TextColumn(width="medium")},
    )

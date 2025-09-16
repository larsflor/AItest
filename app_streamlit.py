
import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime

# ---------- Settings ----------
st.set_page_config(page_title="AI SOC-assistent (demo)", page_icon="🛡️", layout="wide")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
use_llm = bool(OPENAI_API_KEY)

# ---------- Small helpers ----------
@st.cache_data
def load_incidents():
    return pd.read_csv("data/incidents.csv")

@st.cache_data
def load_kb():
    with open("kb.json") as f:
        return json.load(f)

def simulated_llm(prompt: str) -> str:
    # Very naive, template-based "AI". Just enough for a demo if no API key.
    if "PowerShell" in prompt or "powershell" in prompt:
        return (
            "Sammanfattning: Misstänkt PowerShell-process startad av Office-dokument. "
            "Hög risk för makro-baserad nedladdning.\n\n"
            "Rekommenderade steg:\n"
            "1) Isolera klienten.\n2) Hämta artefakter (processer, nätverk)."
            "\n3) Kör IOC-sökning i miljön.\n4) Blockera indikatorer i EDR/SOAR.\n"
            "5) Informera användare och SOC Manager.\n"
        )
    if "phishing" in prompt.lower():
        return (
            "Bedömning: Sannolik phishing med lookalike-domän och makro-bilaga.\n"
            "Åtgärder: 1) Karantän e-post, 2) Sandboxa bilaga, 3) Informera drabbad användare, "
            "4) Sök efter liknande mail, 5) Uppdatera regler för lookalikes.\n"
        )
    if "SIEM" in prompt or "query" in prompt.lower():
        return "Exempel-SIEM-fråga: index=auth user=svc_admin | transaction user maxspan=10m | where failed>=5 AND success=1"
    if "stakeholder" in prompt.lower() or "intressent" in prompt.lower():
        return (
            "Ämne: Lägesrapport incident\n\nHej,\nVi hanterar en misstänkt händelse på LAPTOP-23F. "
            "Klienten är isolerad och IOC-sökning pågår. Nästa uppdatering om 60 min.\n\nMvh,\nSOC"
        )
    # generic fallback
    return (
        "Sammanfattning: Det här är ett simulerat LLM-svar baserat på din prompt.\n"
        "Föreslagna nästa steg: följ relevant playbook, dokumentera i ärendet, och kommunicera till intressenter."
    )

def call_llm(prompt: str) -> str:
    if not use_llm:
        return simulated_llm(prompt)
    try:
        # Lazy import to avoid dependency if not used
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Du är en kortfattad, handlingsinriktad SOC-analytiker. Svara på svenska."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"(LLM-fel, växlar till simulerat läge)\n\n{simulated_llm(prompt)}"

# ---------- UI ----------
st.title("🛡️ AI SOC-assistent – demo")
st.caption("Förenklad agent som hjälper till med triage, phishing och policyfrågor.")

tab1, tab2, tab3 = st.tabs(["Incidenttriage", "Phishing-analys", "Policy/Playbook Q&A"])

kb = load_kb()

with tab1:
    st.subheader("Incidenttriage")
    df = load_incidents()
    st.dataframe(df, use_container_width=True, hide_index=True)
    selected = st.selectbox("Välj incident", df["id"].tolist())
    row = df[df["id"] == selected].iloc[0]
    st.markdown(f"**{row['title']}**  \nKälla: {row['source']} • Prioritet: {row['severity']} • Tid: {row['event_time']}  \nTillgångar: {row['assets']}")
    st.text_area("Incidentanteckningar", row["notes"], height=120, key="notes_t1")

    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("🧠 Sammanfatta incident"):
            prompt = f"Sammanfatta kort incidenten och risken:\n{row.to_dict()}"
            st.write(call_llm(prompt))
    with colB:
        if st.button("📝 Föreslå åtgärdsplan"):
            # Pick playbook by keyword
            pb_key = "edr_powershell" if "PowerShell" in row["title"] else \
                     "phishing_attachment" if "phishing" in row["title"].lower() else \
                     "after_hours_admin_login"
            steps = kb["playbooks"].get(pb_key, [])
            prompt = f"Föreslå en konkret åtgärdsplan (punktlista) baserat på playbook-steg: {steps}\nIncident: {row.to_dict()}"
            st.write(call_llm(prompt))
    with colC:
        if st.button("📧 Skapa stakeholder-mail"):
            contact = kb["contacts"]["SOC_manager"]
            prompt = f"Skriv ett kort statusmail på svenska till {contact} om incident {row['id']} med tydliga next steps."
            st.write(call_llm(prompt))

    st.divider()
    st.subheader("Hjälp för jakt/queries")
    if st.button("🔎 Ge exempel på SIEM-fråga"):
        q = kb["queries"]["siem_failed_then_success"]
        prompt = f"Föreslå eller förbättra SIEM-fråga för att hitta liknande händelser. Exempel: {q}"
        st.code(call_llm(prompt))

with tab2:
    st.subheader("Phishing-analys")
    sender = st.text_input("Avsändare", "Accounts Payable <ap@inv0ice-co.com>")
    subject = st.text_input("Ämne", "Invoice 2025-09")
    indicators = st.text_area("Indikatorer (domän, bilagor, länkar, språkbruk)", "Lookalike-domän, makro-bilaga DOCM, brådska i språket")
    user = st.text_input("Drabbad användare", "bob@example.com")

    if st.button("🧠 Bedöm & föreslå åtgärder"):
        prompt = f"Bedöm phishingrisk och föreslå åtgärder enligt playbook 'phishing_attachment'. Indata: {sender}, {subject}, {indicators}, user={user}"
        st.write(call_llm(prompt))

with tab3:
    st.subheader("Policy/Playbook Q&A")
    question = st.text_area("Ställ en fråga (ex: 'Vad gör vi vid admininloggningar nattetid?')", height=120)
    if st.button("🔍 Svara baserat på playbooks & KB"):
        # Simple retrieval from kb.playbooks
        context = json.dumps(kb, ensure_ascii=False)
        prompt = f"Besvara på svenska, kortfattat. Använd endast följande kunskapsbas: {context}\n\nFråga: {question}"
        st.write(call_llm(prompt))

st.caption(("✅ LLM-aktivt (OpenAI)" if use_llm else "🟡 Simulerat läge (ingen API-nyckel)")
           + " • Denna demo är förenklad och avsedd för visning.")

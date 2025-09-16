
# AI-agent demo för säkerhetsföretag (enkel SOC-assistent)

Ett superenkelt demo byggt i Streamlit som visar tre användningsfall:
1) Incidenttriage (sammanfatta incident, föreslå nästa steg)
2) Phishing-analys (snabb riskbedömning + användarinfo)
3) Policy/Playbook Q&A (agenten hittar svar i ett litet "kunskapsbibliotek")

## Snabbstart

1. Installera beroenden (Python 3.10+ rekommenderas):
```
pip install streamlit openai pandas
```
2. (Valfritt) Sätt din OpenAI-nyckel för "riktig" AI:
- macOS/Linux:
```
export OPENAI_API_KEY="sk-..."
```
- Windows PowerShell:
```
setx OPENAI_API_KEY "sk-..."
```
3. Starta appen:
```
streamlit run app_streamlit.py
```

> **Ingen API-nyckel?** Inga problem – appen kör ett *simulerat läge* med mallade svar.
> Det räcker för att demonstrera flödet och agentbeteendet.

## Demo-idéer att visa upp
- Klicka på en incident och be agenten **sammanfatta** och **föreslå åtgärdsplan**.
- Låt agenten skapa ett **stakeholder-mail** (t.ex. till SOC Manager).
- Visa hur agenten kan ta fram en **SIEM-fråga** eller ett kort **hunt-upplägg**.
- Kör phishing-exemplet och visa **rekommenderade steg** enligt playbook.
- Ställ en fri fråga i läget **Policy/Playbook Q&A** (t.ex. *”Vad gör vi vid admininloggningar nattetid?”*).

## Filer
- `app_streamlit.py` – huvudappen (svenskt UI)
- `data/incidents.csv` – några påhittade incidenter
- `kb.json` – enkel kunskapsbas med playbooks, queries och kontakter

Lycka till!

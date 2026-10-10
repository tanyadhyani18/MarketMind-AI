import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="MarketMind AI", page_icon="📊", layout="wide")
st.title("📊 MarketMind AI")
st.caption("Agentic Marketing Intelligence | MBA Marketing + Big Data Analytics")

REQUIRED = ["Campaign","Channel","Impressions","Clicks","Conversions","Spend","Revenue"]
NUMERIC = ["Impressions","Clicks","Conversions","Spend","Revenue"]
SAMPLE = pd.DataFrame({
    "Campaign":["Instagram Ads","Google Ads","Facebook Ads","Email Marketing"],
    "Channel":["Social","Search","Social","Email"],
    "Impressions":[50000,40000,60000,20000],
    "Clicks":[2500,3200,1800,1500],
    "Conversions":[100,240,54,180],
    "Spend":[10000,15000,8000,2000],
    "Revenue":[30000,60000,15000,25000]})

def prepare_data(df):
    missing=[c for c in REQUIRED if c not in df.columns]
    if missing: raise ValueError("Missing columns: "+", ".join(missing))
    if df.empty: raise ValueError("CSV has no rows.")
    df=df.copy()
    for c in NUMERIC: df[c]=pd.to_numeric(df[c],errors="coerce")
    if df[NUMERIC].isna().any().any(): raise ValueError("Metric columns must contain valid numbers.")
    if (df[NUMERIC]<0).any().any(): raise ValueError("Metrics cannot be negative.")
    if (df["Impressions"]<=0).any() or (df["Spend"]<=0).any(): raise ValueError("Impressions and spend must be above zero.")
    if (df["Clicks"]>df["Impressions"]).any() or (df["Conversions"]>df["Clicks"]).any():
        raise ValueError("Clicks cannot exceed impressions; conversions cannot exceed clicks.")
    df["CTR (%)"]=(df["Clicks"]/df["Impressions"]*100).round(2)
    df["Conversion Rate (%)"]=(df["Conversions"]/df["Clicks"].replace(0,float("nan"))*100).round(2)
    df["CPC"]=(df["Spend"]/df["Clicks"].replace(0,float("nan"))).round(2)
    df["CPA"]=(df["Spend"]/df["Conversions"].replace(0,float("nan"))).round(2)
    df["ROAS"]=(df["Revenue"]/df["Spend"]).round(2)
    return df

# Specialist agents return structured results.
def data_analyst_agent(df):
    spend=float(df["Spend"].sum()); revenue=float(df["Revenue"].sum())
    return {"campaign_count":len(df),"total_spend":spend,"total_revenue":revenue,
            "conversions":int(df["Conversions"].sum()),"overall_roas":revenue/spend}

def performance_analyst_agent(df):
    best=df.loc[df["ROAS"].idxmax()]; low=df.loc[df["ROAS"].idxmin()]
    return {"best_campaign":str(best["Campaign"]),"best_roas":float(best["ROAS"]),
            "weakest_campaign":str(low["Campaign"]),"weakest_roas":float(low["ROAS"])}

def marketing_strategist_agent(metrics, perf):
    return [
      {"Priority":"1 — Investigate","Recommendation":f"Review {perf['weakest_campaign']} (ROAS {perf['weakest_roas']:.2f}x).","Evidence":"It has the lowest observed revenue-to-spend ratio.","KPI":"ROAS, CPA, conversion rate"},
      {"Priority":"2 — Learn","Recommendation":f"Investigate what contributes to {perf['best_campaign']} (ROAS {perf['best_roas']:.2f}x).","Evidence":"It has the highest observed revenue-to-spend ratio.","KPI":"ROAS, conversion volume, audience quality"},
      {"Priority":"3 — Validate","Recommendation":"Before shifting budget, check margin, attribution, audience overlap and campaign goals.","Evidence":"ROAS is not profit and does not prove causation.","KPI":"Contribution margin, incremental conversions"}]

def orchestrate(df):
    metrics=data_analyst_agent(df)
    perf=performance_analyst_agent(df)
    recs=marketing_strategist_agent(metrics,perf)
    return metrics,perf,recs

with st.sidebar:
    st.header("How to use")
    st.write("Upload a campaign CSV or start with sample data.")
    st.download_button("Download sample CSV",SAMPLE.to_csv(index=False).encode(), "marketmind_sample_campaigns.csv","text/csv")
    st.caption("Agents use explicit Python rules; no LLM/API key is required.")

upload=st.file_uploader("Upload campaign CSV",type=["csv"])
try:
    raw=pd.read_csv(upload) if upload else SAMPLE.copy()
    df=prepare_data(raw)
except Exception as e:
    st.error(f"Could not analyse file: {e}")
    st.info("Required columns: "+", ".join(REQUIRED))
    st.stop()

metrics,perf,recs=orchestrate(df)
st.caption(f"Analysing {len(df)} campaigns")
a,b,c,d=st.columns(4)
a.metric("Total ad spend",f"₹{metrics['total_spend']:,.0f}")
b.metric("Attributed revenue",f"₹{metrics['total_revenue']:,.0f}")
c.metric("Conversions",f"{metrics['conversions']:,}")
d.metric("Overall ROAS",f"{metrics['overall_roas']:.2f}x")
st.caption("ROAS = attributed revenue ÷ ad spend; it is not profit.")

t1,t2,t3,t4=st.tabs(["📈 Dashboard","🤖 Agent workflow","💬 Customer feedback","📄 Data & reports"])
with t1:
    left,right=st.columns(2)
    left.plotly_chart(px.bar(df,x="Campaign",y="Conversions",color="Channel",title="Conversions by campaign"),use_container_width=True)
    right.plotly_chart(px.bar(df,x="Campaign",y="ROAS",color="Channel",title="ROAS by campaign"),use_container_width=True)
    st.plotly_chart(px.bar(df,x="Channel",y="Spend",color="Channel",title="Spend by channel"),use_container_width=True)
    st.dataframe(df,use_container_width=True,hide_index=True)
with t2:
    st.subheader("Agent 1 — Data Analyst")
    st.json(metrics)
    st.subheader("Agent 2 — Campaign Performance Analyst")
    st.write(f"Highest ROAS: **{perf['best_campaign']}** ({perf['best_roas']:.2f}x)")
    st.write(f"Lowest ROAS: **{perf['weakest_campaign']}** ({perf['weakest_roas']:.2f}x)")
    st.subheader("Agent 3 — Marketing Strategist")
    st.dataframe(pd.DataFrame(recs),use_container_width=True,hide_index=True)
    st.warning("Rule-based recommendations: review business context before making decisions. The app does not change ad budgets.")
with t3:
    st.write("Upload a CSV with a `Review` column for approximate keyword-based sentiment.")
    review_file=st.file_uploader("Upload customer reviews CSV",type=["csv"],key="reviews")
    if review_file:
        try:
            reviews=pd.read_csv(review_file)
            if "Review" not in reviews.columns: st.error("CSV needs a column named Review.")
            else:
                pos={"good","great","love","excellent","easy","fast","helpful","happy","recommend"}
                neg={"bad","poor","slow","expensive","broken","late","difficult","refund","disappointed"}
                def sentiment(value):
                    words=set(str(value).lower().replace("."," ").replace(","," ").split())
                    score=len(words&pos)-len(words&neg)
                    return "Positive" if score>0 else "Negative" if score<0 else "Neutral / unclear"
                reviews["Approximate sentiment"]=reviews["Review"].fillna("").map(sentiment)
                st.dataframe(reviews,use_container_width=True,hide_index=True)
                st.plotly_chart(px.histogram(reviews,x="Approximate sentiment",title="Approximate customer sentiment"),use_container_width=True)
                st.download_button("Download sentiment CSV",reviews.to_csv(index=False).encode(),"marketmind_sentiment.csv","text/csv")
        except Exception as e: st.error(str(e))
    else: st.info("Optional section. Keyword sentiment is approximate, not an LLM or trained model.")
with t4:
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.download_button("Download analysed CSV",df.to_csv(index=False).encode(),"marketmind_analysis.csv","text/csv")
    report=f"""# MarketMind AI Report

Campaigns analysed: {metrics['campaign_count']}
Total spend: ₹{metrics['total_spend']:,.0f}
Attributed revenue: ₹{metrics['total_revenue']:,.0f}
Conversions: {metrics['conversions']}
Overall ROAS: {metrics['overall_roas']:.2f}x

Highest ROAS: {perf['best_campaign']} ({perf['best_roas']:.2f}x)
Lowest ROAS: {perf['weakest_campaign']} ({perf['weakest_roas']:.2f}x)

## Recommendations
"""+"\n".join(f"- {r['Priority']}: {r['Recommendation']} Evidence: {r['Evidence']}" for r in recs)
    st.download_button("Download report (Markdown)",report,"marketmind_report.md","text/markdown")
st.divider()
st.caption("Educational prototype. Sample data is illustrative. Validate insights before taking action.")

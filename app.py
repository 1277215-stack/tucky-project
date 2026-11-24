import json, math
from decimal import Decimal, ROUND_HALF_UP
import numpy as np, pandas as pd, streamlit as st, plotly.express as px
from scipy import stats

st.set_page_config(page_title="Career Venture Lab | NUR-4 (tuckies)", layout="wide")
D = lambda v: Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

if "st" not in st.session_state:
    st.session_state.st = {
        "team_id": "tuckies", "course": "AP Statistics", "pathway_id": "NUR-4",
        "level": "Advanced", "v": 1, "cash": 4000.0, "equip": 1500.0,
        "equity": 6000.0, "ret_earn": -500.0, "ledger": [], "run_ids": []
    }
S = st.session_state.st

st.title("Career Venture Lab — NUR-4 (Nurse-Led Health Education)")
st.caption(f"Team: {S['team_id']} | Course: {S['course']} | Pathway: {S['pathway_id']} | State: v{S['v']} | Simulation Only (No Clinical Care)")

# Persistent Math Skills & Challenge Level Panel
with st.expander("Math Skills & Challenge Level Panel", expanded=True):
    S["level"] = st.selectbox("Challenge Level", ["Foundation", "Applied", "Advanced"], index=["Foundation", "Applied", "Advanced"].index(S["level"]))
    tasks = {
        "Foundation": "Analyze synthetic randomized sample (n=80, 40/group): p̂_A = 12/40 = 0.30, p̂_B = 20/40 = 0.50. Explain why synthetic findings are not market proof.",
        "Applied": "Two-proportion z-interval & pooled z-test (H0: p_B = p_A). Check random assignment, 10% independence, and large counts.",
        "Advanced": "Translate 95% CI [0.0102, 0.3898] (unpooled) into capacity/budget decisions; separate CI for effect from sales forecast bands."
    }
    st.info(f"**{S['level']} Task:** {tasks[S['level']]}")

t1, t2, t3, t4 = st.tabs(["1. Operations & Ledger", "2. AP Stats Experiment", "3. Reports & Visuals", "4. Save / Load"])

with t1:
    c1, c2, c3 = st.columns(3)
    price = D(c1.number_input("Price/Seat ($)", 1.0, 500.0, 25.0))
    req = c1.number_input("Requested Seats", 0, 500, 80)
    run_id = c1.text_input("Run ID", f"RUN-{len(S['ledger'])+1:02d}")
    hrs = c2.number_input("Educator Hours", 0.0, 200.0, 30.0)
    seats = c2.number_input("Venue Seats", 0, 200, 60)
    noshow = c2.slider("No-Show Rate", 0.0, 1.0, 0.0, 0.05)
    var_c = D(c3.number_input("Variable Cost/Seat ($)", 0.0, 100.0, 5.0))
    fix_c = D(c3.number_input("Fixed Cost/Month ($)", 0.0, 5000.0, 700.0))
    ad_c = D(c3.number_input("Approved Ad Cost ($)", 0.0, 2000.0, 0.0))

    cap = min(math.floor(hrs / 0.5), seats)
    booked = min(req, cap)
    sold = math.floor(booked * (1 - noshow))
    st.write(f"**Preview:** Cap = {cap} | Booked = {booked} | Attended/Sold = {sold} | Lost Demand = {max(0, req - booked)}")

    b1, b2 = st.columns(2)
    if b1.button("Approve & Run Month", type="primary"):
        if run_id in S["run_ids"]:
            st.error("Duplicate Run ID rejected.")
        else:
            rev, v_exp = D(price * sold), D(var_c * sold)
            prof = D(rev - v_exp - fix_c - ad_c)
            S["cash"] = float(D(Decimal(str(S["cash"])) + prof))
            S["ret_earn"] = float(D(Decimal(str(S["ret_earn"])) + prof))
            S["v"] += 1
            S["run_ids"].append(run_id)
            S["ledger"].append({"run_id": run_id, "v": S["v"], "req": req, "cap": cap, "sold": sold, "rev": float(rev), "exp": float(v_exp + fix_c + ad_c), "profit": float(prof), "cash": S["cash"]})
            st.rerun()

    if b2.button("Replay NUR-4 3-Month Fixture"):
        S.update({"v": 1, "cash": 4000.0, "ret_earn": -500.0, "ledger": [], "run_ids": []})
        for idx, (m, r, c_ov, ad) in enumerate([("2027-01", 80, 60, 0), ("2027-02", 88, 60, 100), ("2027-03", 72, 45, 0)], 1):
            bk = min(r, c_ov)
            rev, exp = D(25 * bk), D(5 * bk + 700 + ad)
            prof = D(rev - exp)
            S["cash"] = float(D(Decimal(str(S["cash"])) + prof))
            S["ret_earn"] = float(D(Decimal(str(S["ret_earn"])) + prof))
            S["v"] += 1
            S["run_ids"].append(f"FIX-{idx}")
            S["ledger"].append({"run_id": f"FIX-{idx}", "v": S["v"], "req": r, "cap": c_ov, "sold": bk, "rev": float(rev), "exp": float(exp), "profit": float(prof), "cash": S["cash"]})
        st.rerun()

with t2:
    rng = np.random.default_rng(2027)
    df_exp = pd.DataFrame({"message": ["A"]*40 + ["B"]*40, "converted": np.r_[rng.permutation([1]*12+[0]*28), rng.permutation([1]*20+[0]*20)]})
    pA, pB = 12/40, 20/40
    se_unp = math.sqrt(pA*(1-pA)/40 + pB*(1-pB)/40)
    se_pool = math.sqrt((32/80)*(48/80)*(2/40))
    z = (pB - pA) / se_pool
    pval = 2 * (1 - stats.norm.cdf(abs(z)))
    st.metric("Lift (p̂_B - p̂_A)", f"{pB-pA:.2f}", f"95% CI: [{(pB-pA)-1.96*se_unp:.4f}, {(pB-pA)+1.96*se_unp:.4f}]")
    st.write(f"Pooled z = `{z:.4f}`, two-sided p = `{pval:.5f}`. Synthetic seed 2027 supports internal comparison only, not population generalization.")
    st.plotly_chart(px.bar(x=["Message A", "Message B"], y=[pA, pB], labels={"x": "Variant", "y": "Conversion Rate"}, title="Synthetic Experiment (n=80)"), use_container_width=True)

with t3:
    if S["ledger"]:
        df_l = pd.DataFrame(S["ledger"])
        st.dataframe(df_l, use_container_width=True)
        st.write(f"**Balance Check:** Assets (${S['cash'] + S['equip']:,.2f}) = Equity + Retained Earnings (${S['equity'] + S['ret_earn']:,.2f})")
        st.plotly_chart(px.line(df_l, x="run_id", y=["rev", "exp", "profit"], markers=True, title="Revenue, Expense & Profit"), use_container_width=True)
        st.download_button("Export CSV", df_l.to_csv(index=False), "nur4_ledger.csv", "text/csv")
    else:
        st.info("Run a month or replay the fixture in Tab 1 to view reports.")

with t4:
    st.download_button("Download Snapshot JSON", json.dumps(S, indent=2), f"tuckies_NUR4_v{S['v']}.json", "application/json")
    up = st.file_uploader("Restore Snapshot JSON", type=["json"])
    if up:
        data = json.load(up)
        if data.get("team_id") != "tuckies" or data.get("v", 0) < S["v"]:
            st.error("Rejected: Wrong team_id or stale state version.")
        else:
            st.session_state.st = data
            st.rerun()

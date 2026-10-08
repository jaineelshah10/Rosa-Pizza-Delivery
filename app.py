from pathlib import Path

import pandas as pd
import streamlit as st
from starter import ZONES, TIME_BLOCKS, COSTS, delivery_times

# Use a fixed seed so the numbers are the same every time the app runs
SEED = 1


def cost_of_one_late_order(cost_info):
    # works out how much one late order costs the business in total
    # cost_info is a dictionary holding the cost assumptions

    # money paid back to the customer for the late order
    refund = cost_info["refund"]

    # profit lost from future orders the customer won't place because of the late delivery
    # (number of lost orders x profit made on each order)
    lost_profit = cost_info["churn_orders"] * cost_info["margin"]

    # total cost = refund now + profit lost later
    total = refund + lost_profit
    return total


def find_best_promise(zone, block, promise_list, cost_info):
    # tries each promised delivery time in promise_list and finds the one
    # that gives the highest profit for this zone and time block

    # cost of a single late order (refund + lost future profit)
    late_cost = cost_of_one_late_order(cost_info)

    # one row per promise tried: [promise, orders, late orders, profit]
    results = []

    # no best yet, so start both as None
    best_promise = None
    best_profit = None

    for p in promise_list:
        # simulate orders using p as the promised time
        # (the number of orders can change with the promise)
        order_times = delivery_times(zone, block, p, seed=SEED)
        num_orders = len(order_times)

        # count the orders that arrived after the promise
        num_late = 0
        for t in order_times:
            if t > p:
                num_late = num_late + 1

        # profit = profit from all orders - cost of the late ones
        profit = num_orders * cost_info["margin"] - num_late * late_cost
        results.append([p, num_orders, num_late, profit])

        # remember this promise if it is the best one so far
        if best_profit is None or profit > best_profit:
            best_promise = p
            best_profit = profit

    # send back the best promise, its profit, and the full results table
    return best_promise, best_profit, results


st.set_page_config(page_title="Rosa's Pizza", page_icon="🍕", layout="wide")

# --- Style: boxed title, step cards, recommendation card ---
st.markdown(
    """<style>
    .title-box {border:2px solid #4DA3FF; border-radius:14px; padding:18px 24px;
                text-align:center; background:#131a26;}
    .title-box h1 {color:#4DA3FF; margin:8px 0 0 0; padding:0; font-size:2rem;}
    .step {color:#4DA3FF; font-weight:700; font-size:1.1rem; margin-bottom:4px;}
    .rec-card {border-radius:16px; padding:28px; text-align:center;
               background:linear-gradient(135deg,#16314f,#1a1f2b);
               border:1px solid #4DA3FF;}
    .rec-card .label {color:#9db7d5; font-size:0.9rem; letter-spacing:0.12em;
                      text-transform:uppercase;}
    .rec-card .big {color:#ffffff; font-size:3.4rem; font-weight:700; line-height:1.1;}
    .rec-card .sub {color:#4DA3FF; font-size:1.2rem; margin-top:6px;}
    </style>""",
    unsafe_allow_html=True,
)

logo_svg = (Path(__file__).parent / "logo.svg").read_text(encoding="utf-8")
# collapse to one line with no indentation, otherwise markdown treats it as a code block
logo_svg = " ".join(line.strip() for line in logo_svg.splitlines())

st.markdown(
    '<div class="title-box">'
    + logo_svg
    + "<h1>Rosa's Pizza: Best Promised Delivery Time</h1></div>",
    unsafe_allow_html=True,
)
st.write("")

# --- Inputs: three cards side by side, all on one page ---
card1, card2, card3 = st.columns(3)

with card1.container(border=True):
    st.markdown('<div class="step">1 &nbsp; Where &amp; when</div>', unsafe_allow_html=True)
    zone = st.selectbox("Zone", ZONES)
    block = st.selectbox("Time block", TIME_BLOCKS)

with card2.container(border=True):
    st.markdown('<div class="step">2 &nbsp; Promises to try</div>', unsafe_allow_html=True)
    low, high = st.slider(
        "Range (minutes)", min_value=10, max_value=120, value=(20, 80)
    )
    step = st.number_input(
        "Step size (minutes)", min_value=1, max_value=30, value=5, step=1
    )

with card3.container(border=True):
    st.markdown('<div class="step">3 &nbsp; Cost assumptions</div>', unsafe_allow_html=True)
    margin = st.number_input(
        "Profit margin per order ($)",
        min_value=0.0,
        value=float(COSTS["margin"]),
        step=0.5,
    )
    churn = st.number_input(
        "Churn: lost orders per late order",
        min_value=0.0,
        value=float(COSTS["churn_orders"]),
        step=0.1,
    )
    refund = st.number_input(
        "Refund per late order ($)",
        min_value=0.0,
        value=float(COSTS["refund"]),
        step=0.5,
    )

run = st.button("Find best promise", type="primary", width="stretch")

# --- Calculation (only when the button is clicked) ---
if run:
    # copy COSTS so the user's changes don't alter the starter's values
    cost_info = dict(COSTS)
    cost_info["margin"] = margin
    cost_info["churn_orders"] = churn
    cost_info["refund"] = refund

    promise_list = list(range(int(low), int(high) + 1, int(step)))

    best, profit, results = find_best_promise(zone, block, promise_list, cost_info)

    table = pd.DataFrame(
        results, columns=["Promise (min)", "Orders", "Late orders", "Net profit ($)"]
    )

    st.write("")
    st.markdown(
        '<div class="rec-card">'
        f'<div class="label">Recommended promise &middot; {zone} &middot; {block}</div>'
        f'<div class="big">{best} min</div>'
        f'<div class="sub">Net profit ${profit:,.1f}</div></div>',
        unsafe_allow_html=True,
    )
    st.write("")

    # warn if the best promise is at either end of the range
    if best == promise_list[0] or best == promise_list[-1]:
        st.warning(
            "The best promise is at the edge of the range. "
            "A promise outside the range might be even better, so widen the range and try again."
        )

    # chart and table side by side
    chart_col, table_col = st.columns(2)
    with chart_col.container(border=True):
        st.markdown('<div class="step">Net profit by promise</div>', unsafe_allow_html=True)
        st.line_chart(table, x="Promise (min)", y="Net profit ($)")
    with table_col.container(border=True):
        st.markdown('<div class="step">Full results</div>', unsafe_allow_html=True)
        st.dataframe(table, hide_index=True, width="stretch")

---
name: notebook-to-streamlit
description: Convert the Rosa's Pizza analysis from the Jupyter notebook into a Streamlit app. Use when building or updating app.py.
---

# Notebook to Streamlit

## Goal
Build `app.py`, a Streamlit app that helps Rosa choose the best promised delivery time, using the logic from the notebook `Jaineel_Shah_Assignment_1_Rosa_Pizza.ipynb`.

## Rules
1. Copy the functions `cost_of_one_late_order` and `find_best_promise` from the notebook into app.py exactly as written. Do not change the logic.
2. Import `ZONES`, `TIME_BLOCKS`, `COSTS` and `delivery_times` from `starter`. Never redefine them. Use `SEED = 1` like the notebook.
3. Inputs:
   - `st.selectbox` for the zone and for the time block
   - `st.slider` for the range of promised times to try, and `st.number_input` for the step size
   - `st.number_input` for profit margin, churn per late order, and refund per late order, with defaults from `COSTS`
4. Only run the calculation when the user clicks a "Find best promise" button.
5. Show the recommended promise and its net profit, a line chart of net profit by promise, and the full results table.
6. If the best promise is at the edge of the range, show a warning to widen the range.
7. Do not put any personal information in app.py.
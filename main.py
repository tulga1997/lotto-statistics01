import streamlit as st
import pandas as pd
from itertools import combinations
import random

st.title("Lotto New Combination Generator")

# Define custom color groups
def get_color_group(n):
    if 1 <= n <= 10:
        return 'Yellow'
    elif 11 <= n <= 20:
        return 'Blue'
    elif 21 <= n <= 30:
        return 'Red'
    elif 31 <= n <= 40:
        return 'Black'
    else:
        return 'Green'

uploaded_history = st.file_uploader("Upload previous draws (CSV with draw number, 6 numbers, bonus)", type="csv")

if uploaded_history:
    try:
        history_df = pd.read_csv(uploaded_history, usecols=[1,2,3,4,5,6,7])
        previous_draws = set(tuple(sorted(map(int, row[:6]))) for row in history_df.dropna().values)
        bonus_sets = set(tuple(sorted(map(int, row[:6])) + [int(row[6])]) for row in history_df.dropna().values)
    except Exception as e:
        st.error(f"⚠️ Error loading previous data: {e}")
        st.stop()

    with st.expander("Number filter"):
        selected_numbers = st.multiselect("Select from numbers:", list(range(1, 46)), default=list(range(1, 46)))
        only_even = st.checkbox("Even only")
        only_odd = st.checkbox("Odd only")
        must_include = st.text_input("Numbers to include (comma-separated)", "")
        use_color_balance = st.checkbox("Use color balance (1 Yellow, 1 Blue, 1 Red, etc.)")

    n_generate = st.number_input("How many combinations to generate?", 1, 1000, 100)

    if st.button("Generate new combinations"):
        numbers = selected_numbers
        if only_even:
            numbers = [n for n in numbers if n % 2 == 0]
        if only_odd:
            numbers = [n for n in numbers if n % 2 == 1]

        combos = combinations(numbers, 6)
        unique_combos = []

        for c in combos:
            sorted_c = tuple(sorted(c))
            if sorted_c in previous_draws:
                continue
            for row in history_df.dropna().values:
                if sorted_c == tuple(sorted(map(int, row[:6]))) and int(row[6]) in sorted_c:
                    break
            else:
                if use_color_balance:
                    color_counts = {"Yellow":0, "Blue":0, "Red":0, "Black":0, "Green":0}
                    for n in sorted_c:
                        color_counts[get_color_group(n)] += 1
                    if not (color_counts["Yellow"] >= 1 and color_counts["Blue"] >= 1 and color_counts["Red"] >= 1):
                        continue
                unique_combos.append(sorted_c)

        random.shuffle(unique_combos)

        if must_include:
            try:
                must = set(map(int, must_include.split(",")))
                unique_combos = [c for c in unique_combos if must <= set(c)]
            except:
                st.warning("Must include field must be valid comma-separated numbers.")

        out_combos = unique_combos[:n_generate]
        df = pd.DataFrame(out_combos, columns=["N1", "N2", "N3", "N4", "N5", "N6"])
        st.write(df)

        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, file_name="new_combinations.csv")

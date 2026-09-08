import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Global Digital Connectivity Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .dashboard-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #172033;
        margin-bottom: 0.2rem;
    }

    .dashboard-subtitle {
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.45rem;
        font-weight: 650;
        color: #172033;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    .section-description {
        color: #64748b;
        margin-bottom: 1rem;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748b;
    }

    div[data-testid="stMetricValue"] {
        color: #172033;
    }

    .insight-box {
        background: white;
        border-left: 4px solid #2563eb;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
        color: #334155;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.85rem;
        padding: 2rem 0 1rem 0;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    # Works when CSV is in the same folder as app.py
    file_path = Path(__file__).parent / "global_digital_connectivity_intelligence44.csv"

    df = pd.read_csv(file_path)

    # Remove exact duplicates
    df = df.drop_duplicates().copy()

    # Convert year
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    # Numeric columns
    numeric_columns = df.select_dtypes(include=np.number).columns

    # Median imputation
    for column in numeric_columns:
        if df[column].isnull().any():
            df[column] = df[column].fillna(df[column].median())

    return df


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_number(value, decimals=1):
    if pd.isna(value):
        return "N/A"

    if abs(value) >= 1000000:
        return f"{value / 1000000:.{decimals}f}M"

    if abs(value) >= 1000:
        return f"{value / 1000:.{decimals}f}K"

    return f"{value:.{decimals}f}"


def metric_average(data, column):
    if column not in data.columns or data.empty:
        return np.nan
    return data[column].mean()


def normalize_series(series):
    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(100, index=series.index)

    return ((series - minimum) / (maximum - minimum)) * 100


# ============================================================
# LOAD
# ============================================================

try:
    df = load_data()

except FileNotFoundError:

    st.error(
        "Dataset not found. Make sure "
        "'global_digital_connectivity_intelligence44(1).csv' "
        "is in the same folder as app.py."
    )

    st.stop()


# ============================================================
# DATA INFORMATION
# ============================================================

latest_year = int(df["Year"].max())
first_year = int(df["Year"].min())

countries = sorted(df["Country"].dropna().unique())
regions = sorted(df["Region"].dropna().unique())
income_groups = sorted(df["Income_Group"].dropna().unique())


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🌍 Connectivity Intelligence")

    st.markdown("---")

    st.markdown("### Dashboard Filters")

    selected_year = st.selectbox(
        "Year",
        sorted(df["Year"].unique(), reverse=True),
        index=0
    )

    selected_region = st.multiselect(
        "Region",
        regions,
        default=regions
    )

    selected_income = st.multiselect(
        "Income Group",
        income_groups,
        default=income_groups
    )

    country_options = sorted(
        df[
            df["Region"].isin(selected_region)
            & df["Income_Group"].isin(selected_income)
        ]["Country"].unique()
    )

    selected_country = st.selectbox(
        "Country Deep Dive",
        ["All Countries"] + country_options
    )

    st.markdown("---")

    st.markdown("### Dataset")

    st.write(f"**Years:** {first_year}–{latest_year}")
    st.write(f"**Countries:** {df['Country'].nunique()}")
    st.write(f"**Regions:** {df['Region'].nunique()}")
    st.write(f"**Records:** {len(df):,}")

    st.markdown("---")

    st.caption(
        "This dashboard uses the supplied synthetic educational "
        "panel dataset. Values should not be interpreted as official "
        "real-world statistics."
    )


# ============================================================
# FILTER DATA
# ============================================================

year_data = df[
    (df["Year"] == selected_year)
    & (df["Region"].isin(selected_region))
    & (df["Income_Group"].isin(selected_income))
].copy()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">🌍 Global Digital Connectivity Intelligence</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Measuring digital access, infrastructure, affordability and readiness '
    f'across countries and regions • {first_year}–{latest_year}'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# KPI CARDS
# ============================================================

st.markdown(
    '<div class="section-title">Executive Overview</div>',
    unsafe_allow_html=True
)

if not year_data.empty:

    avg_internet = year_data["Internet_Usage_Pct"].mean()
    avg_fixed = year_data["Avg_Fixed_Download_Speed_Mbps"].mean()
    avg_mobile = year_data["Avg_Mobile_Download_Speed_Mbps"].mean()
    avg_4g = year_data["Network_Coverage_4G_Pct"].mean()
    avg_5g = year_data["Availability_5G_Pct"].mean()
    avg_literacy = year_data["Digital_Literacy_Pct"].mean()
    avg_cost = year_data["Connectivity_Cost_Pct_Income"].mean()

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(
            "Internet Usage",
            f"{avg_internet:.1f}%"
        )

    with k2:
        st.metric(
            "Fixed Broadband",
            f"{avg_fixed:.1f} Mbps"
        )

    with k3:
        st.metric(
            "Mobile Speed",
            f"{avg_mobile:.1f} Mbps"
        )

    with k4:
        st.metric(
            "Digital Literacy",
            f"{avg_literacy:.1f}%"
        )

    k5, k6, k7, k8 = st.columns(4)

    with k5:
        st.metric(
            "4G Coverage",
            f"{avg_4g:.1f}%"
        )

    with k6:
        st.metric(
            "5G Availability",
            f"{avg_5g:.1f}%"
        )

    with k7:
        st.metric(
            "Connectivity Cost",
            f"{avg_cost:.1f}% of income"
        )

    with k8:
        st.metric(
            "Countries",
            f"{year_data['Country'].nunique()}"
        )


# ============================================================
# EXECUTIVE INSIGHTS
# ============================================================

st.markdown(
    '<div class="section-title">Key Insights</div>',
    unsafe_allow_html=True
)

if not year_data.empty:

    highest_internet = year_data.loc[
        year_data["Internet_Usage_Pct"].idxmax()
    ]

    lowest_internet = year_data.loc[
        year_data["Internet_Usage_Pct"].idxmin()
    ]

    fastest = year_data.loc[
        year_data["Avg_Fixed_Download_Speed_Mbps"].idxmax()
    ]

    slowest = year_data.loc[
        year_data["Avg_Fixed_Download_Speed_Mbps"].idxmin()
    ]

    insights = [
        f"**Internet adoption leader:** {highest_internet['Country']} "
        f"with {highest_internet['Internet_Usage_Pct']:.1f}% internet usage.",

        f"**Lowest internet adoption:** {lowest_internet['Country']} "
        f"with {lowest_internet['Internet_Usage_Pct']:.1f}% usage.",

        f"**Fixed broadband leader:** {fastest['Country']} "
        f"with {fastest['Avg_Fixed_Download_Speed_Mbps']:.1f} Mbps.",

        f"**Fixed broadband laggard:** {slowest['Country']} "
        f"with {slowest['Avg_Fixed_Download_Speed_Mbps']:.1f} Mbps."
    ]

    for insight in insights:

        st.markdown(
            f'<div class="insight-box">💡 {insight}</div>',
            unsafe_allow_html=True
        )


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "🌐 Global Overview",
        "🌍 Regional Analysis",
        "🏆 Country Rankings",
        "⚖️ Digital Divide",
        "💰 Affordability",
        "🔎 Country Deep Dive"
    ]
)


# ============================================================
# TAB 1 — GLOBAL OVERVIEW
# ============================================================

with tab1:

    st.markdown(
        '<div class="section-title">Global Connectivity Trends</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Track how global digital connectivity has evolved from '
        f'{first_year} to {latest_year}.'
        '</div>',
        unsafe_allow_html=True
    )

    yearly = (
        df.groupby("Year")
        .agg({
            "Internet_Usage_Pct": "mean",
            "Household_Internet_Access_Pct": "mean",
            "Smartphone_Adoption_Pct": "mean",
            "Digital_Literacy_Pct": "mean"
        })
        .reset_index()
    )

    c1, c2 = st.columns(2)

    with c1:

        fig = px.line(
            yearly,
            x="Year",
            y=[
                "Internet_Usage_Pct",
                "Household_Internet_Access_Pct",
                "Smartphone_Adoption_Pct"
            ],
            markers=True,
            labels={
                "value": "Percentage",
                "variable": "Indicator"
            },
            title="Digital Adoption Evolution"
        )

        fig.update_layout(
            legend_title_text="Indicator",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        speed_yearly = (
            df.groupby("Year")
            .agg({
                "Avg_Fixed_Download_Speed_Mbps": "mean",
                "Avg_Mobile_Download_Speed_Mbps": "mean"
            })
            .reset_index()
        )

        fig = px.line(
            speed_yearly,
            x="Year",
            y=[
                "Avg_Fixed_Download_Speed_Mbps",
                "Avg_Mobile_Download_Speed_Mbps"
            ],
            markers=True,
            labels={
                "value": "Mbps",
                "variable": "Connection Type"
            },
            title="Global Internet Speed Evolution"
        )

        fig.update_layout(
            legend_title_text="Connection Type",
            hovermode="x unified"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # 4G / 5G / Literacy
    infrastructure = (
        df.groupby("Year")
        .agg({
            "Network_Coverage_4G_Pct": "mean",
            "Availability_5G_Pct": "mean",
            "Digital_Literacy_Pct": "mean"
        })
        .reset_index()
    )

    fig = px.line(
        infrastructure,
        x="Year",
        y=[
            "Network_Coverage_4G_Pct",
            "Availability_5G_Pct",
            "Digital_Literacy_Pct"
        ],
        markers=True,
        title="Infrastructure and Digital Capability Evolution"
    )

    fig.update_layout(
        yaxis_title="Percentage",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# TAB 2 — REGIONAL ANALYSIS
# ============================================================

with tab2:

    st.markdown(
        '<div class="section-title">Regional Digital Landscape</div>',
        unsafe_allow_html=True
    )

    regional = (
        year_data.groupby("Region")
        .agg({
            "Internet_Usage_Pct": "mean",
            "Avg_Fixed_Download_Speed_Mbps": "mean",
            "Avg_Mobile_Download_Speed_Mbps": "mean",
            "Network_Coverage_4G_Pct": "mean",
            "Availability_5G_Pct": "mean",
            "Digital_Literacy_Pct": "mean"
        })
        .reset_index()
    )

    c1, c2 = st.columns(2)

    with c1:

        fig = px.bar(
            regional.sort_values("Internet_Usage_Pct"),
            x="Internet_Usage_Pct",
            y="Region",
            orientation="h",
            title=f"Internet Usage by Region — {selected_year}",
            text_auto=".1f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        fig = px.bar(
            regional.sort_values(
                "Avg_Fixed_Download_Speed_Mbps"
            ),
            x="Avg_Fixed_Download_Speed_Mbps",
            y="Region",
            orientation="h",
            title=f"Fixed Broadband Speed by Region — {selected_year}",
            text_auto=".1f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Regional comparison table

    st.markdown("### Regional Performance Scorecard")

    display_regional = regional.copy()

    display_regional.columns = [
        "Region",
        "Internet Usage (%)",
        "Fixed Speed (Mbps)",
        "Mobile Speed (Mbps)",
        "4G Coverage (%)",
        "5G Availability (%)",
        "Digital Literacy (%)"
    ]

    st.dataframe(
        display_regional.round(2),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 3 — COUNTRY RANKINGS
# ============================================================

with tab3:

    st.markdown(
        '<div class="section-title">Country Performance Rankings</div>',
        unsafe_allow_html=True
    )

    ranking_metric = st.selectbox(
        "Select metric",
        [
            "Internet_Usage_Pct",
            "Avg_Fixed_Download_Speed_Mbps",
            "Avg_Mobile_Download_Speed_Mbps",
            "Network_Coverage_4G_Pct",
            "Availability_5G_Pct",
            "Digital_Literacy_Pct",
            "Smartphone_Adoption_Pct"
        ]
    )

    top_n = st.slider(
        "Number of countries",
        min_value=5,
        max_value=20,
        value=10
    )

    ranking = (
        year_data[
            ["Country", "Region", "Income_Group", ranking_metric]
        ]
        .sort_values(
            ranking_metric,
            ascending=False
        )
        .head(top_n)
    )

    fig = px.bar(
        ranking.sort_values(ranking_metric),
        x=ranking_metric,
        y="Country",
        orientation="h",
        color="Region",
        title=f"Top {top_n} Countries — {ranking_metric}",
        text_auto=".1f"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("### Ranking Table")

    st.dataframe(
        ranking.round(2),
        use_container_width=True,
        hide_index=True
    )

    # Bottom performers

    st.markdown("### Lowest Performers")

    bottom = (
        year_data[
            ["Country", "Region", "Income_Group", ranking_metric]
        ]
        .sort_values(
            ranking_metric,
            ascending=True
        )
        .head(top_n)
    )

    st.dataframe(
        bottom.round(2),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 4 — DIGITAL DIVIDE
# ============================================================

with tab4:

    st.markdown(
        '<div class="section-title">The Digital Divide</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Measure differences in access, speed and infrastructure '
        'between regions and income groups.'
        '</div>',
        unsafe_allow_html=True
    )

    # Regional speed gap

    gap = (
        year_data.groupby("Region")[
            "Avg_Fixed_Download_Speed_Mbps"
        ]
        .agg(["min", "max"])
        .reset_index()
    )

    gap["Speed_Gap_Mbps"] = gap["max"] - gap["min"]

    c1, c2 = st.columns(2)

    with c1:

        fig = px.bar(
            gap.sort_values("Speed_Gap_Mbps"),
            x="Speed_Gap_Mbps",
            y="Region",
            orientation="h",
            title=f"Fixed Broadband Speed Gap Within Regions — {selected_year}",
            text_auto=".1f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        adoption_gap = (
            year_data.groupby("Region")[
                "Internet_Usage_Pct"
            ]
            .agg(["min", "max"])
            .reset_index()
        )

        adoption_gap["Adoption_Gap"] = (
            adoption_gap["max"]
            - adoption_gap["min"]
        )

        fig = px.bar(
            adoption_gap.sort_values("Adoption_Gap"),
            x="Adoption_Gap",
            y="Region",
            orientation="h",
            title=f"Internet Adoption Gap Within Regions — {selected_year}",
            text_auto=".1f"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Income group digital divide

    income = (
        year_data.groupby("Income_Group")
        .agg({
            "Internet_Usage_Pct": "mean",
            "Avg_Fixed_Download_Speed_Mbps": "mean",
            "Digital_Literacy_Pct": "mean",
            "Availability_5G_Pct": "mean"
        })
        .reset_index()
    )

    fig = px.bar(
        income,
        x="Income_Group",
        y="Internet_Usage_Pct",
        color="Income_Group",
        title=f"Internet Usage by Income Group — {selected_year}",
        text_auto=".1f"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        income.round(2),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 5 — AFFORDABILITY
# ============================================================

with tab5:

    st.markdown(
        '<div class="section-title">Internet Affordability</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Explore whether the cost of connectivity is associated '
        'with internet adoption.'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:

        fig = px.scatter(
            year_data,
            x="Connectivity_Cost_Pct_Income",
            y="Internet_Usage_Pct",
            size="Population_Millions",
            color="Region",
            hover_name="Country",
            title="Connectivity Cost vs Internet Adoption",
            trendline="ols"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        fig = px.scatter(
            year_data,
            x="Mobile_Data_Cost_per_GB_USD",
            y="Internet_Usage_Pct",
            size="Population_Millions",
            color="Income_Group",
            hover_name="Country",
            title="Mobile Data Cost vs Internet Adoption",
            trendline="ols"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # Correlation

    cost_corr = year_data[
        [
            "Connectivity_Cost_Pct_Income",
            "Internet_Usage_Pct"
        ]
    ].corr().iloc[0, 1]

    mobile_corr = year_data[
        [
            "Mobile_Data_Cost_per_GB_USD",
            "Internet_Usage_Pct"
        ]
    ].corr().iloc[0, 1]

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Cost vs Internet Usage",
            f"{cost_corr:.2f}"
        )

    with c2:
        st.metric(
            "Mobile Data Cost vs Usage",
            f"{mobile_corr:.2f}"
        )

    st.markdown("### Most Expensive Connectivity")

    expensive = year_data[
        [
            "Country",
            "Broadband_Monthly_Cost_USD",
            "Mobile_Data_Cost_per_GB_USD",
            "Connectivity_Cost_Pct_Income"
        ]
    ].sort_values(
        "Connectivity_Cost_Pct_Income",
        ascending=False
    ).head(10)

    st.dataframe(
        expensive.round(2),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# TAB 6 — COUNTRY DEEP DIVE
# ============================================================

with tab6:

    st.markdown(
        '<div class="section-title">Country Deep Dive</div>',
        unsafe_allow_html=True
    )

    if selected_country == "All Countries":

        st.info(
            "Select a country from the sidebar to view its "
            "2018–2025 digital transformation."
        )

    else:

        country_data = df[
            df["Country"] == selected_country
        ].sort_values("Year")

        country_latest = country_data[
            country_data["Year"] == latest_year
        ]

        if not country_latest.empty:

            row = country_latest.iloc[0]

            st.markdown(
                f"### {selected_country}"
            )

            st.caption(
                f"{row['Region']} • {row['Income_Group']}"
            )

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric(
                    "Internet Usage",
                    f"{row['Internet_Usage_Pct']:.1f}%"
                )

            with c2:
                st.metric(
                    "Fixed Speed",
                    f"{row['Avg_Fixed_Download_Speed_Mbps']:.1f} Mbps"
                )

            with c3:
                st.metric(
                    "4G Coverage",
                    f"{row['Network_Coverage_4G_Pct']:.1f}%"
                )

            with c4:
                st.metric(
                    "5G Availability",
                    f"{row['Availability_5G_Pct']:.1f}%"
                )

        # Internet adoption history

        c1, c2 = st.columns(2)

        with c1:

            fig = px.line(
                country_data,
                x="Year",
                y="Internet_Usage_Pct",
                markers=True,
                title="Internet Usage Evolution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with c2:

            fig = px.line(
                country_data,
                x="Year",
                y=[
                    "Avg_Fixed_Download_Speed_Mbps",
                    "Avg_Mobile_Download_Speed_Mbps"
                ],
                markers=True,
                title="Internet Speed Evolution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # Infrastructure

        fig = px.line(
            country_data,
            x="Year",
            y=[
                "Network_Coverage_4G_Pct",
                "Availability_5G_Pct"
            ],
            markers=True,
            title="4G and 5G Evolution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # Country table

        st.markdown("### Historical Country Data")

        columns_to_show = [
            "Year",
            "Internet_Usage_Pct",
            "Household_Internet_Access_Pct",
            "Smartphone_Adoption_Pct",
            "Avg_Fixed_Download_Speed_Mbps",
            "Avg_Mobile_Download_Speed_Mbps",
            "Network_Coverage_4G_Pct",
            "Availability_5G_Pct",
            "Digital_Literacy_Pct",
            "Connectivity_Cost_Pct_Income"
        ]

        columns_to_show = [
            col for col in columns_to_show
            if col in country_data.columns
        ]

        st.dataframe(
            country_data[columns_to_show].round(2),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# DIGITAL READINESS SECTION
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">🧠 Digital Readiness Index</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'A project-defined composite score combining internet adoption, '
    'household access, smartphone adoption, speed, network coverage '
    'and digital literacy. This is not an official external index.'
    '</div>',
    unsafe_allow_html=True
)

readiness_columns = [
    "Internet_Usage_Pct",
    "Household_Internet_Access_Pct",
    "Smartphone_Adoption_Pct",
    "Avg_Fixed_Download_Speed_Mbps",
    "Avg_Mobile_Download_Speed_Mbps",
    "Network_Coverage_4G_Pct",
    "Availability_5G_Pct",
    "Digital_Literacy_Pct"
]

available_readiness = [
    col for col in readiness_columns
    if col in year_data.columns
]

readiness_df = year_data[
    ["Country", "Region", "Income_Group"] + available_readiness
].copy()

normalized_columns = []

for column in available_readiness:

    normalized_column = column + "_Normalized"

    readiness_df[normalized_column] = normalize_series(
        readiness_df[column]
    )

    normalized_columns.append(normalized_column)


readiness_df["Digital_Readiness_Score"] = (
    readiness_df[normalized_columns]
    .mean(axis=1)
)

readiness_ranked = readiness_df.sort_values(
    "Digital_Readiness_Score",
    ascending=False
)

c1, c2 = st.columns([1.4, 1])

with c1:

    top_readiness = readiness_ranked.head(10).sort_values(
        "Digital_Readiness_Score"
    )

    fig = px.bar(
        top_readiness,
        x="Digital_Readiness_Score",
        y="Country",
        orientation="h",
        color="Region",
        title=f"Top 10 Digital Readiness Countries — {selected_year}",
        text_auto=".1f"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with c2:

    regional_readiness = (
        readiness_df.groupby("Region")[
            "Digital_Readiness_Score"
        ]
        .mean()
        .reset_index()
        .sort_values("Digital_Readiness_Score")
    )

    fig = px.bar(
        regional_readiness,
        x="Digital_Readiness_Score",
        y="Region",
        orientation="h",
        title=f"Digital Readiness by Region — {selected_year}",
        text_auto=".1f"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.markdown("### Digital Readiness Ranking")

st.dataframe(
    readiness_ranked[
        [
            "Country",
            "Region",
            "Income_Group",
            "Digital_Readiness_Score"
        ]
    ].round(2),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 2018 → 2025 IMPROVEMENT
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">📈 Digital Transformation: '
    f'{first_year} → {latest_year}</div>',
    unsafe_allow_html=True
)

first_snapshot = df[
    df["Year"] == first_year
][
    ["Country", "Internet_Usage_Pct"]
].rename(
    columns={
        "Internet_Usage_Pct": "Internet_First"
    }
)

last_snapshot = df[
    df["Year"] == latest_year
][
    ["Country", "Internet_Usage_Pct"]
].rename(
    columns={
        "Internet_Usage_Pct": "Internet_Last"
    }
)

improvement = first_snapshot.merge(
    last_snapshot,
    on="Country",
    how="inner"
)

improvement["Improvement"] = (
    improvement["Internet_Last"]
    - improvement["Internet_First"]
)

improvement = improvement.sort_values(
    "Improvement",
    ascending=False
)

top_improvers = improvement.head(10).sort_values(
    "Improvement"
)

fig = px.bar(
    top_improvers,
    x="Improvement",
    y="Country",
    orientation="h",
    title=f"Top 10 Countries by Internet Adoption Improvement "
          f"({first_year}–{latest_year})",
    text_auto=".1f"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# DOWNLOAD FILTERED DATA
# ============================================================

st.markdown("---")

st.markdown(
    '<div class="section-title">⬇️ Export Data</div>',
    unsafe_allow_html=True
)

download_data = year_data.to_csv(index=False)

st.download_button(
    label="Download Filtered Dataset",
    data=download_data,
    file_name=f"digital_connectivity_{selected_year}.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">'
    'Global Digital Connectivity Intelligence • '
    'Python • Pandas • NumPy • Plotly • Streamlit'
    '</div>',
    unsafe_allow_html=True
)

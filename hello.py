# Import necessary libraries
from preswald import (
    connect, query, text, table, slider, selectbox,
    plotly, checkbox, sidebar, alert, topbar
)
import plotly.express as px
import pandas as pd

# Initialize connection
connect()

# Load and clean the data
sql = """
    SELECT 
        "Sales Person" as sales_person,
        Country,
        Product,
        "Date" as date,
        CAST(REPLACE(REPLACE("Amount", '$', ''), ',', '') AS FLOAT) as amount,
        "Boxes Shipped" as boxes_shipped
    FROM chocolatedata_csv
"""

# execute the query and process dates
df = query(sql, "chocolatedata_csv")

# Convert date strings to datetime objects
df['date'] = pd.to_datetime(df['date'], format='%d-%b-%y')

# Convert date to string format for display
df['display_date'] = df['date'].dt.strftime('%Y-%m-%d')

# Convert numpy float to Python float
df['amount'] = df['amount'].astype(float)
df['boxes_shipped'] = df['boxes_shipped'].astype(float)

# Create the dashboard
sidebar()

text("# Chocolate Sales Dashboard")
text("### Analyze chocolate sales data from various perspectives")

# Data Overview Section
text("## Data Overview")
show_raw = checkbox("Show raw data?", default=False)

if show_raw:
    # Create display DataFrame with formatted date
    display_df = df.copy()
    display_df['date'] = display_df['display_date']
    display_df = display_df.drop('display_date', axis=1)
    table(display_df, title="Raw Data")

# Filters
text("## Filters")

# Arrange filters side by side
selected_country = selectbox(
    "Select Country",
    options=["All"] + sorted(df["Country"].unique().tolist()),
    size=0.5
)

min_amount = df["amount"].min()
max_amount = df["amount"].max()

amount_threshold = slider(
    "Minimum Sale Amount ($)",
    min_val=float(min_amount),
    max_val=float(max_amount),
    default=float(min_amount),
    size=0.5
)

# Filter data based on selections
filtered_df = df[df["amount"] >= amount_threshold].copy()

if selected_country != "All":
    filtered_df = filtered_df[filtered_df["Country"] == selected_country]

# Sales Analysis
text("## Sales Analysis")

# Total metrics
total_sales = filtered_df["amount"].sum()
total_boxes = filtered_df["boxes_shipped"].sum()

alert(
    f"Total Sales: ${total_sales:,.2f} | Total Boxes Shipped: {total_boxes:,}",
    level="info"
)

# Sales by Country
fig_country = px.bar(
    filtered_df.groupby("Country")["amount"].sum().reset_index(),
    x="Country",
    y="amount",
    title="Sales by Country",
    labels={"amount": "Sales Amount ($)", "Country": "Country"}
)

plotly(fig_country, size=0.5)

# Sales by Product
fig_product = px.pie(
    filtered_df.groupby("Product")["amount"].sum().reset_index(),
    values="amount",
    names="Product",
    title="Sales Distribution by Product"
)

plotly(fig_product, size=0.5)

# Top Sales People
text("## Top Sales People")

# Top sales table
top_sales = filtered_df.groupby("sales_person")["amount"].sum().sort_values(
    ascending=False
).reset_index()

table(top_sales, title="Sales Performance by Person")

text("## Monthly Trend")

# Convert dates to string format for JSON serialization
monthly_sales = filtered_df.groupby(
    pd.Grouper(key="date", freq="ME")
)["amount"].sum().reset_index()
monthly_sales['date'] = monthly_sales['date'].dt.strftime('%Y-%m-%d')
fig_trend = px.line(
    monthly_sales,
    x="date",
    y="amount",
    title="Monthly Sales Trend",
    labels={"amount": "Sales Amount ($)", "date": "Month"}
)

plotly(fig_trend, size=0.5)

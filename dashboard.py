import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns


@st.cache_data
def load_data():
    data = pd.read_csv(r"C:\Users\DELL\wppool\wppool\data.csv")
    data["install_date"] = pd.to_datetime(data["install_date"])
    data["active_users"] = (data["days_active"] > 0).astype(int)
    data["churned_users"] = data["churned"].astype(int)
    return data

data = load_data()

# Calculate Metrics
current_conversion_ratio = (data["active_users"].sum() / data["user_id"].count()) * 100
upgrade_ratio = (data["pro_upgrade_date"].notna().sum() / data["active_users"].sum()) * 100

# --- Sidebar ---
st.sidebar.title("📊 User Dashboard")
st.sidebar.write("Filter the data as needed.")
subscription_filter = st.sidebar.selectbox("Filter by Subscription Type", ["All"] + list(data["subscription_type"].unique()))
country_filter = st.sidebar.selectbox("Filter by Country", ["All"] + list(data["country"].unique()))

# Filter Data
filtered_data = data
if subscription_filter != "All":
    filtered_data = filtered_data[filtered_data["subscription_type"] == subscription_filter]
if country_filter != "All":
    filtered_data = filtered_data[filtered_data["country"] == country_filter]

# --- Main Dashboard ---
st.title("📈 User Engagement & Revenue Dashboard")
st.markdown("An interactive dashboard for analyzing user conversion, churn, and revenue insights.")

# --- KPI Metrics ---
col1, col2 = st.columns(2)
col1.metric("Current Conversion Ratio", f"{current_conversion_ratio:.2f}%")
col2.metric("Upgrade Ratio", f"{upgrade_ratio:.2f}%")

# --- Conversion Rate by Subscription Type ---
st.subheader("🚀 Conversion Rate by Subscription Type")
conversion_rates = filtered_data.groupby("subscription_type")["active_users"].mean() * 100
fig, ax = plt.subplots(figsize=(6,4))
sns.barplot(x=conversion_rates.index, y=conversion_rates.values, palette="Blues", ax=ax)
ax.set_ylabel("Conversion Rate (%)")
ax.set_xlabel("Subscription Type")
ax.set_title("Conversion Rate")
st.pyplot(fig)

# --- Pro Upgrade Over Time ---
st.subheader("📅 Pro Upgrade Count Over Time")
upgrade_over_time = filtered_data.groupby(filtered_data["install_date"].dt.date)["pro_upgrade_date"].count()
fig = px.line(x=upgrade_over_time.index, y=upgrade_over_time.values, markers=True, title="Pro Upgrade Count Over Time")
st.plotly_chart(fig)

# --- Churned vs Active Users ---
st.subheader("📉 Churned vs. Active Users by Subscription Type")
churn_vs_active = filtered_data.groupby("subscription_type")[["active_users", "churned_users"]].sum()
fig, ax = plt.subplots(figsize=(6,4))
churn_vs_active.plot(kind="bar", stacked=True, ax=ax, colormap="coolwarm")
ax.set_ylabel("Number of Users")
ax.set_xlabel("Subscription Type")
ax.set_title("Churned vs. Active Users")
st.pyplot(fig)

# --- Monthly Revenue by Country ---
st.subheader("🌍 Total Monthly Revenue by Country")
revenue_by_country = filtered_data.groupby("country")["monthly_revenue"].sum().reset_index()
fig = px.bar(revenue_by_country, x="country", y="monthly_revenue", color="country", title="Total Monthly Revenue by Country")
st.plotly_chart(fig)

# --- Show Data ---
st.subheader("📊 Raw Data")
st.dataframe(filtered_data)

import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import hashlib

st.set_page_config(
    page_title="Local Tourism Promotion Portal",
    layout="wide"
)

DB_PATH = "tourism_users.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()

def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_user(email, password):
    cursor.execute(
        "INSERT INTO users(email,password) VALUES (?,?)",
        (email, make_hash(password))
    )
    conn.commit()

def login_user(email, password):
    cursor.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, make_hash(password))
    )
    data = cursor.fetchall()
    return data

def load_default_data():
    return pd.read_csv("year.csv")

if "data" not in st.session_state:
    st.session_state.data = load_default_data()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🏔 Local Tourism Promotion Portal")

    menu = st.sidebar.selectbox(
        "Select Option",
        ["Login", "Register"]
    )

    if menu == "Login":

        st.subheader("🔐 Login")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            result = login_user(email, password)

            if result:
                st.success(f"Welcome {email}")
                st.session_state.logged_in = True
                st.rerun()

            else:
                st.error("Invalid Email or Password")

    elif menu == "Register":

        st.subheader("📝 Create New Account")

        email = st.text_input("Email")
        new_password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Register"):

            if "@" not in email or "." not in email:
                st.error("Enter Valid Email")

            else:
                try:
                    add_user(email, new_password)
                    st.success("Account Created Successfully")
                    st.info("Go to Login Menu to Login")

                except:
                    st.error("Email Already Exists")

else:

    st.sidebar.success("Logged In")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🏔 Local Tourism Promotion Portal")
    st.subheader("Tourism Analytics Dashboard")

    st.sidebar.title("Navigation")

    menu = st.sidebar.radio(
        "Select Option",
        [
            "Home",
            "Upload Dataset",
            "Tourism Analytics",
            "Revenue Analysis",
            "Best Time to Visit",
            "Top Locations",
            "About"
        ]
    )

    if menu == "Home":

        st.image(
            "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
            use_container_width=True
        )

        st.markdown("""
        ## Welcome to the Local Tourism Promotion Portal

        This portal helps analyze:

        - Tourist Visitors
        - Revenue Generation
        - Seasonal Trends
        - Best Tourist Destinations
        - Monthly Tourism Growth

        ### Features
        ✔ Interactive Dashboard  
        ✔ Dataset Upload  
        ✔ Data Cleaning  
        ✔ Charts & Graphs  
        ✔ Revenue Analysis  
        ✔ Best Time Prediction  
        """)

    elif menu == "Upload Dataset":

        st.header("📂 Upload Tourism Dataset")

        uploaded_file = st.file_uploader(
            "Upload CSV File",
            type=["csv"]
        )

        if uploaded_file is not None:

            df = pd.read_csv(uploaded_file)

            st.write("## Original Dataset")
            st.dataframe(df)


            st.header("🧹 Data Cleaning")


            st.subheader("🔍 Missing Values Before Cleaning")

            missing_values = df.isnull().sum()

            st.write(missing_values)

            # Highlight missing values
            st.write("### Dataset with Missing Values Highlighted")

            def highlight_missing(val):
                if pd.isnull(val):
                    return 'background-color: red'
                return ''

            st.dataframe(
                df.style.map(highlight_missing)
            )


            rows_before = len(df)

            df = df.dropna()

            rows_after = len(df)

            removed_rows = rows_before - rows_after

            st.success(
                f"Removed {removed_rows} rows containing missing values"
            )

            duplicate_rows = df.duplicated().sum()

            if duplicate_rows > 0:
                df = df.drop_duplicates()

            st.success(
                f"Removed {duplicate_rows} duplicate rows"
            )

            text_cols = df.select_dtypes(
                include=["object"]
            ).columns

            for col in text_cols:
                df[col] = df[col].astype(str).str.strip()

            if "Month" in df.columns:
                df["Month"] = (
                    df["Month"]
                    .astype(str)
                    .str.title()
                )

            st.subheader("✅ Missing Values After Cleaning")

            st.write(df.isnull().sum())

            st.success("Dataset Cleaned Successfully ✅")

            st.write("## Cleaned Dataset")

            st.dataframe(df)

            cleaned_csv = (
                df.to_csv(index=False)
                .encode("utf-8")
            )

            st.download_button(
                label="⬇ Download Cleaned Dataset",
                data=cleaned_csv,
                file_name="cleaned_tourism_data.csv",
                mime="text/csv"
            )

            st.session_state.data = df


            st.write("## Dataset Statistics")

            st.write(df.describe())

        else:
            st.info("Using Current Dataset")
            st.dataframe(st.session_state.data.head())

    elif menu == "Tourism Analytics":

        st.header("📊 Tourism Analytics Dashboard")

        df = st.session_state.data

        total_visitors = df["Visitors"].sum()
        total_revenue = df["Revenue"].sum()
        total_locations = df["Location"].nunique()

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Visitors", total_visitors)
        col2.metric("Total Revenue", f"₹ {total_revenue:,}")
        col3.metric("Total Locations", total_locations)

        st.write("---")

        # Visitors per year
        st.subheader("Year-wise Visitors")

        year_visitors = (
            df.groupby("Year")["Visitors"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            year_visitors,
            x="Year",
            y="Visitors",
            title="Visitors Per Year"
        )

        st.plotly_chart(fig, use_container_width=True)

        # Monthly Revenue
        st.subheader("Month-wise Revenue")

        month_revenue = (
            df.groupby("Month")["Revenue"]
            .sum()
            .reset_index()
        )

        fig2 = px.line(
            month_revenue,
            x="Month",
            y="Revenue",
            markers=True,
            title="Monthly Revenue"
        )

        st.plotly_chart(fig2, use_container_width=True)

    elif menu == "Revenue Analysis":

        st.header("💰 Revenue Analysis")

        df = st.session_state.data

        location_revenue = (
            df.groupby("Location")["Revenue"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            location_revenue,
            values="Revenue",
            names="Location",
            title="Revenue Contribution by Location"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Top Revenue Locations")

        st.dataframe(
            location_revenue.sort_values(
                by="Revenue",
                ascending=False
            )
        )

    elif menu == "Best Time to Visit":

        st.header("🌤 Best Time to Visit")

        df = st.session_state.data

        location = st.selectbox(
            "Select Location",
            df["Location"].unique()
        )

        filtered_df = df[df["Location"] == location]

        best_month = (
            filtered_df.groupby("Month")["Visitors"]
            .sum()
            .idxmax()
        )


        st.success(
            f"Best Month to Visit {location}: {best_month}"
        )

        # Revenue Chart
        st.subheader("💰 Year-wise Revenue Analysis")

        year_revenue = (
            filtered_df.groupby("Year")["Revenue"]
            .sum()
            .reset_index()
        )

        fig1 = px.bar(
            year_revenue,
            x="Year",
            y="Revenue",
            color="Year",
            title=f"Year-wise Revenue for {location}"
        )

        st.plotly_chart(fig1, use_container_width=True)

        # Visitors Chart
        st.subheader("📊 Year-wise Visitors Analysis")

        year_visitors = (
            filtered_df.groupby("Year")["Visitors"]
            .sum()
            .reset_index()
        )

        fig2 = px.bar(
            year_visitors,
            x="Year",
            y="Visitors",
            color="Year",
            title=f"Year-wise Visitors for {location}"
        )

        st.plotly_chart(fig2, use_container_width=True)

    elif menu == "Top Locations":

        st.header("🏆 Top Tourist Locations")

        df = st.session_state.data

        top_locations = (
            df.groupby("Location")["Visitors"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        st.dataframe(top_locations)

        fig = px.bar(
            top_locations,
            x="Location",
            y="Visitors",
            title="Most Visited Tourist Places"
        )

        st.plotly_chart(fig, use_container_width=True)

    elif menu == "About":

        st.header("About Project")

        st.markdown("""
        ### Local Tourism Promotion Portal

        This project is developed using:

        - Python
        - Streamlit
        - Pandas
        - Plotly
        - SQLite Database

        ### Objectives

        - Promote Local Tourism
        - Analyze Tourism Data
        - Perform Data Cleaning
        - Find Best Tourist Seasons
        - Revenue Analysis
        - Tourism Insights
        """)

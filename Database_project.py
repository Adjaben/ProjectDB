import streamlit as st
import mysql.connector
import plotly.express as px
import pandas as pd

# ---------------------- DB Connection ----------------------

def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Afia@Ashesi27",
        database="Finalsdb"
    )

# ---------------------- Queries Functions ----------------------

def run_query_1():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.Brand_Name, i.Industry_Name
        FROM BRAND b
        JOIN INDUSTRY_BRAND ib ON b.Brand_ID = ib.Brand_ID
        JOIN INDUSTRY i ON ib.Industry_ID = i.Industry_ID
    """)
    data = cursor.fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=["Brand", "Industry"])
    st.dataframe(df)

def run_query_2():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT inf.Handle
        FROM INFLUENCER inf
        WHERE inf.Application_ID NOT IN (SELECT Application_ID FROM BRAND_APPLICATION)
    """)
    data = cursor.fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=["Unlinked Influencers"])
    st.dataframe(df)

def run_query_3():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT inf.Handle, ba.Brand_Name, ba.Pay_Package
        FROM INFLUENCER inf
        JOIN BRAND_APPLICATION ba ON inf.Application_ID = ba.Application_ID
    """)
    data = cursor.fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=["Influencer", "Brand", "Pay Package"])
    st.dataframe(df)

def run_query_4():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT inf.Handle, app.Application_ID, app.Status
        FROM INFLUENCER inf
        JOIN APPLICATION app ON inf.Application_ID = app.Application_ID
        WHERE app.Status IN ('Active', 'Pending')
    """)
    data = cursor.fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=["Influencer", "Application ID", "Status"])
    st.dataframe(df)

def run_query_5():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT inf.Handle, app.Application_ID, app.Status
        FROM INFLUENCER inf
        JOIN APPLICATION app ON inf.Application_ID = app.Application_ID
        WHERE app.Status IN ('Active', 'Approved')
    """)
    data = cursor.fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=["Influencer", "Application ID", "Status"])
    st.dataframe(df)

def run_query_6():
    conn = create_connection()
    cursor = conn.cursor()
    industry = st.text_input("Enter Industry:")
    if st.button("Find Influencers"):
        cursor.execute("""
            SELECT i.Handle, a.Status
            FROM INFLUENCER i
            JOIN APPLICATION a ON i.Application_ID = a.Application_ID
            WHERE i.Industry = %s AND a.Status = 'Approved'
        """, (industry,))
        data = cursor.fetchall()
        conn.close()
        df = pd.DataFrame(data, columns=["Influencer", "Status"])
        st.dataframe(df)

def run_query_7():
    conn = create_connection()
    cursor = conn.cursor()
    # This query requires a linking table between CAMPAIGN and INFLUENCER.
    # Based on your schema, this direct relationship doesn't exist.
    # You would typically link them through a junction table (e.g., CAMPAIGN_INFLUENCER)
    # or potentially through the APPLICATION table if that's the intended link.
    # For now, this query will be adapted to show campaigns and the number of applications associated with them.
    cursor.execute("""
        SELECT c.Campaign_ID, COUNT(a.Application_ID) AS Application_Count
        FROM CAMPAIGN c
        LEFT JOIN APPLICATION a ON c.Campaign_ID = a.Application_ID # Assuming a link through Application_ID
        GROUP BY c.Campaign_ID
        ORDER BY Application_Count DESC
        LIMIT 5
    """)
    data = cursor.fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=["Campaign ID", "Application Count"])
    st.dataframe(df)
    st.bar_chart(df.set_index("Campaign ID"))

# ---------------------- App Layout ----------------------

st.title("🔥 Influencer-Brand Platform Admin")

menu = [
    "Home",
    "Manage Influencers",
    "Manage Brands",
    "Manage Campaigns",
    "Brand ↔ Influencer Match",
    "Run Queries"
]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------------- Manage Influencers ----------------------

if choice == "Home":
    st.subheader("🏡 Welcome to the Influencer-Brand Management Dashboard")

    conn = create_connection()

    # --- Fetch summary stats ---
    total_influencers = pd.read_sql("SELECT COUNT(*) FROM INFLUENCER", conn).iloc[0, 0]
    total_brands = pd.read_sql("SELECT COUNT(*) FROM BRAND", conn).iloc[0, 0]
    total_campaigns = pd.read_sql("SELECT COUNT(*) FROM CAMPAIGN", conn).iloc[0, 0]
    total_matches = pd.read_sql("SELECT COUNT(*) FROM BRAND_APPLICATION", conn).iloc[0, 0]

    # --- Display summary stats ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="👤 Influencers", value=total_influencers)
    with col2:
        st.metric(label="🏢 Brands", value=total_brands)
    with col3:
        st.metric(label="🎯 Campaigns", value=total_campaigns)
    with col4:
        st.metric(label="🔗 Matches", value=total_matches)

    st.markdown("---")

    # --- Bar Chart: Number of Influencers per Industry ---
    industry_df = pd.read_sql("""
        SELECT Industry, COUNT(*) AS Num_Influencers
        FROM INFLUENCER
        GROUP BY Industry
        ORDER BY Num_Influencers DESC
    """, conn)

    st.markdown("### 📈 Influencers by Industry")
    st.bar_chart(industry_df.set_index('Industry'))

    st.markdown("---")

    # --- Pie Chart: Campaign Status Distribution ---
    status_df = pd.read_sql("""
        SELECT Status, COUNT(*) AS Count
        FROM CAMPAIGN
        GROUP BY Status
    """, conn)

    st.markdown("### 🥧 Campaigns by Status")
    fig = px.pie(status_df, names='Status', values='Count', title='Campaign Status Distribution', hole=0.4)
    st.plotly_chart(fig)

    conn.close()
elif choice == "Manage Influencers":
    st.subheader("Influencer Management")

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT Influencer_ID, Handle FROM INFLUENCER")
    influencers = cursor.fetchall()

    st.markdown("### ➕ Add New Influencer")

    with st.form("add_influencer_form"):
        new_handle = st.text_input("Handle")
        new_age = st.number_input("Age", min_value=13, max_value=100)
        new_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        new_industry = st.text_input("Industry")
        new_field = st.text_input("Field")
        # Assuming you might want to link to an application when adding
        cursor.execute("SELECT Application_ID FROM APPLICATION")
        application_ids = [row[0] for row in cursor.fetchall()]
        new_application_id = st.selectbox("Application ID (Optional)", [None] + application_ids)
        submit_add = st.form_submit_button("Add Influencer")

        if submit_add:
            query = """
                INSERT INTO INFLUENCER (Handle, Age, Gender, Industry, Field, Application_ID)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (new_handle, new_age, new_gender, new_industry, new_field, new_application_id)
            cursor.execute(query, values)
            conn.commit()
            st.success(f"Influencer {new_handle} added!")

    st.markdown("### 🔄 Update Existing Influencer")

    selected_influencer = st.selectbox("Select Influencer to Update", influencers)

    with st.form("update_influencer_form"):
        updated_handle = st.text_input("New Handle", selected_influencer[1])
        updated_age = st.number_input("New Age", min_value=13, max_value=100)
        updated_gender = st.selectbox("New Gender", ["Male", "Female", "Other"])
        updated_industry = st.text_input("New Industry")
        updated_field = st.text_input("New Field")
        cursor.execute("SELECT Application_ID FROM APPLICATION")
        application_ids_update = [row[0] for row in cursor.fetchall()]
        updated_application_id = st.selectbox("New Application ID (Optional)", [None] + application_ids_update)
        submit_update = st.form_submit_button("Update Influencer")

        if submit_update:
            query = """
                UPDATE INFLUENCER
                SET Handle=%s, Age=%s, Gender=%s, Industry=%s, Field=%s, Application_ID=%s
                WHERE Influencer_ID=%s
            """
            values = (updated_handle, updated_age, updated_gender, updated_industry, updated_field, updated_application_id, selected_influencer[0])
            cursor.execute(query, values)
            conn.commit()
            st.success(f"Influencer {selected_influencer[1]} updated!")

    conn.close()

# ---------------------- Manage Brands ----------------------

elif choice == "Manage Brands":
    st.subheader("Brand Management")

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT Brand_ID, Brand_name FROM BRAND")
    brands = cursor.fetchall()

    st.markdown("### ➕ Add New Brand")

    with st.form("add_brand_form"):
        new_brand_name = st.text_input("Brand Name")
        new_pay_package = st.number_input("Pay Package", min_value=0.0)
        submit_brand_add = st.form_submit_button("Add Brand")

        if submit_brand_add:
            query = """
                INSERT INTO BRAND (Brand_name, Pay_Package)
                VALUES (%s, %s)
            """
            values = (new_brand_name, new_pay_package)
            cursor.execute(query, values)
            conn.commit()
            st.success(f"Brand '{new_brand_name}' added!")

    st.markdown("### 🔄 Update Existing Brand")

    selected_brand = st.selectbox("Select Brand to Update", brands)

    with st.form("update_brand_form"):
        updated_brand_name = st.text_input("New Brand Name", selected_brand[1])
        updated_pay_package = st.number_input("New Pay Package", min_value=0.0)
        submit_brand_update = st.form_submit_button("Update Brand")

        if submit_brand_update:
            query = """
                UPDATE BRAND
                SET Brand_name=%s, Pay_Package=%s
                WHERE Brand_ID=%s
            """
            values = (updated_brand_name, updated_pay_package, selected_brand[0])
            cursor.execute(query, values)
            conn.commit()
            st.success(f"Brand '{selected_brand[1]}' updated!")

    conn.close()

# ---------------------- Manage Campaigns ----------------------

elif choice == "Manage Campaigns":
    st.subheader("Campaign Management")

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT Campaign_ID, Status FROM CAMPAIGN")
    campaigns = cursor.fetchall()
    cursor.execute("SELECT Industry_ID, Industry_Name FROM INDUSTRY")
    industries = cursor.fetchall()

    st.markdown("### ➕ Add New Campaign")

    with st.form("add_campaign_form"):
        new_status = st.selectbox("Campaign Status", ["Active", "Pending", "Completed"])
        new_start_date = st.date_input("Start Date")
        new_end_date = st.date_input("End Date")
        new_industry_id = st.selectbox("Industry", industries)
        submit_campaign_add = st.form_submit_button("Add Campaign")

        if submit_campaign_add:
            query = """
                INSERT INTO CAMPAIGN (Status, Start_Date, End_Date, Industry_ID)
                VALUES (%s, %s, %s, %s)
            """
            values = (new_status, new_start_date, new_end_date, new_industry_id[0])
            cursor.execute(query, values)
            conn.commit()
            st.success(f"Campaign added with status '{new_status}'!")

    st.markdown("### 🔄 Update Existing Campaign")

    selected_campaign = st.selectbox("Select Campaign to Update", campaigns)

    with st.form("update_campaign_form"):
        updated_status = st.selectbox("New Status", ["Active", "Pending", "Completed"])
        updated_start_date = st.date_input("New Start Date")
        updated_end_date = st.date_input("New End Date")
        updated_industry_id = st.selectbox("New Industry", industries)
        submit_campaign_update = st.form_submit_button("Update Campaign")

        if submit_campaign_update:
            query = """
                UPDATE CAMPAIGN
                SET Status=%s, Start_Date=%s, End_Date=%s, Industry_ID=%s
                WHERE Campaign_ID=%s
            """
            values = (updated_status, updated_start_date, updated_end_date, updated_industry_id[0], selected_campaign[0])
            cursor.execute(query, values)
            conn.commit()
            st.success(f"Campaign '{selected_campaign[0]}' updated!")

    conn.close()

# ---------------------- Brand ↔ Influencer Match ----------------------

elif choice == "Brand ↔ Influencer Match":
    st.subheader("🔗 Match Brands with Influencers")

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT Brand_ID, Brand_name FROM BRAND")
    brands = cursor.fetchall()

    cursor.execute("SELECT Application_ID FROM APPLICATION WHERE Status = 'Approved'")
    approved_applications = cursor.fetchall()

    with st.form("match_form"):
        selected_brand = st.selectbox("Select Brand", brands)
        selected_application = st.selectbox("Select Approved Application ID", approved_applications)
        proposed_budget = st.number_input("Proposed Budget", min_value=0.0)

        submit_match = st.form_submit_button("Link Brand to Application")

        if submit_match:
            # Assuming you want to update the BRAND_APPLICATION table to link a brand to an application
            # You might need to consider how the Pay_Package in BRAND and the BID_Amount in APPLICATION relate.
            # For now, we'll insert a new entry.
            cursor.execute("SELECT Brand_Name FROM BRAND WHERE Brand_ID = %s", (selected_brand[0],))
            brand_name = cursor.fetchone()[0]

            query = """
                INSERT INTO BRAND_APPLICATION (Brand_Name, Pay_Package, Brand_ID, Application_ID)
                VALUES (%s, %s, %s, %s)
            """
            values = (brand_name, proposed_budget, selected_brand[0], selected_application[0])
            cursor.execute(query, values)
            conn.commit()
            st.success(f"Linked {selected_brand[1]} to Application ID {selected_application[0]} with budget {proposed_budget}!")

    conn.close()

# ---------------------- Run Queries ----------------------

elif choice == "Run Queries":
    st.subheader("📋 Predefined Queries")

    query_option = st.selectbox("Select a Query", [
        "List of Brands and Industries",
        "Influencers Not Linked to Brands",
        "All Influencers with Brand and Pay",
        "Influencers and Campaigns (Active/Pending)",
        "Influencers and Campaigns (Active/Approved)",
        "Influencers in Industry with 'Approved' Status",
        "Top 5 Campaigns by Influencer Count"
    ])

    if query_option == "List of Brands and Industries":
        run_query_1()
    elif query_option == "Influencers Not Linked to Brands":
        run_query_2()
    elif query_option == "All Influencers with Brand and Pay":
        run_query_3()
    elif query_option == "Influencers and Campaigns (Active/Pending)":
        run_query_4()
    elif query_option == "Influencers and Campaigns (Active/Approved)":
        run_query_5()
    elif query_option == "Influencers in Industry with 'Approved' Status":
        run_query_6()
    elif query_option == "Top 5 Campaigns by Influencer Count":
        run_query_7()
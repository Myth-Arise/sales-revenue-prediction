# # Import python packages
# import streamlit as st
# import os

# # Write directly to the app
# st.title(f"Example Streamlit App :balloon: {st.__version__}")
# st.write(
#   """Replace this example with your own code!
#   **And if you're new to Streamlit,** check
#   out our easy-to-follow guides at
#   [docs.streamlit.io](https://docs.streamlit.io).
#   """
# )

# st.markdown("""
# - :page_with_curl: [Streamlit open source documentation](https://docs.streamlit.io)
# - :snowflake: [Streamlit in Snowflake documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
# - :books: [Demo repo with templates](https://github.com/Snowflake-Labs/snowflake-demo-streamlit)
# - :memo: [Streamlit in Snowflake release notes](https://docs.snowflake.com/en/release-notes/streamlit-in-snowflake)
# """)

# # Create a database connection to Snowflake
# conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))
# session = conn.session()

# # Use an interactive slider to get user input
# hifives_val = st.slider(
#   "Number of high-fives in Q3",
#   min_value=0,
#   max_value=90,
#   value=60,
#   help="Use this to enter the number of high-fives you gave in Q3",
# )

# #  Create an example dataframe
# #  Note: this is just some dummy data, but you can easily connect to your Snowflake data
# #  It is also possible to query data using raw SQL using session.sql() e.g. session.sql("select * from table")
# created_dataframe = session.create_dataframe(
#   [[50, 25, "Q1"], [20, 35, "Q2"], [hifives_val, 30, "Q3"]],
#   schema=["HIGH_FIVES", "FIST_BUMPS", "QUARTER"],
# )

# # Execute the query and convert it into a Pandas dataframe
# queried_data = created_dataframe.to_pandas()

# # Create a simple bar chart
# # See docs.streamlit.io for more types of charts
# st.subheader("Number of high-fives")
# st.bar_chart(data=queried_data, x="QUARTER", y="HIGH_FIVES")

# st.subheader("Underlying data")
# st.dataframe(queried_data, use_container_width=True)



# import streamlit as st
# import pandas as pd
# import numpy as np
# import joblib
# import os
# import tempfile
# import glob

# from datetime import date
# from snowflake.snowpark.context import get_active_session

# # --------------------------------------------------
# # 1. APPLICATION CONFIGURATION
# # --------------------------------------------------

# st.set_page_config(
#     page_title="Sales Revenue Predictor",
#     page_icon="📊",
#     layout="wide"
# )

# st.title("📊 Sales Revenue Prediction")
# st.write(
#     "Predict store sales revenue using our trained "
#     "Machine Learning model."
# )

# session = get_active_session()

# MODEL_STAGE = (
#     "@SALES_ML_DB.SALES_PREDICTION.MODEL_STAGE/"
#     "sales_model.joblib"
# )

# STORE_TABLE = (
#     "SALES_ML_DB.SALES_PREDICTION.STORE_DETAILS"
# )

# HISTORY_TABLE = (
#     "SALES_ML_DB.SALES_PREDICTION.SALES_PREDICTION_HISTORY"
# )


# # --------------------------------------------------
# # 2. LOAD TRAINED MODEL
# # --------------------------------------------------

# @st.cache_resource
# def load_model():

#     folder = tempfile.mkdtemp()

#     session.file.get(
#         MODEL_STAGE,
#         folder
#     )

#     files = glob.glob(
#         os.path.join(folder, "**", "sales_model.joblib"),
#         recursive=True
#     )

#     if not files:
#         raise FileNotFoundError(
#             "Trained model was not found in Snowflake stage."
#         )

#     return joblib.load(files[0])


# # --------------------------------------------------
# # 3. LOAD STORE INFORMATION
# # --------------------------------------------------

# @st.cache_data
# def load_store_data():

#     df = session.table(STORE_TABLE).to_pandas()

#     # Normalize Snowflake column names
#     df.columns = [col.upper() for col in df.columns]

#     return df


# try:
#     model = load_model()
#     store_data = load_store_data()

#     st.success("Machine Learning model loaded successfully!")

# except Exception as e:
#     st.error(f"Unable to load application resources: {e}")
#     st.stop()


# # --------------------------------------------------
# # 4. USER INPUT SECTION
# # --------------------------------------------------

# st.header("Enter Store Information")

# store_ids = sorted(
#     store_data["STORE"].astype(int).unique().tolist()
# )

# col1, col2 = st.columns(2)

# with col1:

#     selected_store = st.selectbox(
#         "Select Store ID",
#         store_ids
#     )

#     prediction_date = st.date_input(
#         "Prediction Date",
#         value=date.today()
#     )

#     is_open = st.selectbox(
#         "Is the store open?",
#         ["Yes", "No"]
#     )

#     promo = st.selectbox(
#         "Is promotion active?",
#         ["Yes", "No"]
#     )

# with col2:

#     school_holiday = st.selectbox(
#         "Is it a school holiday?",
#         ["Yes", "No"]
#     )

#     state_holiday = st.selectbox(
#         "State Holiday",
#         ["0", "a", "b", "c"]
#     )


# # --------------------------------------------------
# # 5. RETRIEVE SELECTED STORE DETAILS
# # --------------------------------------------------

# store_info = store_data[
#     store_data["STORE"].astype(int) == selected_store
# ].iloc[0]


# # --------------------------------------------------
# # 6. FEATURE ENGINEERING
# # --------------------------------------------------

# day_of_week = prediction_date.weekday() + 1

# features = {
#     "Store": str(selected_store),
#     "DayOfWeek": day_of_week,
#     "Open": 1 if is_open == "Yes" else 0,
#     "Promo": 1 if promo == "Yes" else 0,
#     "StateHoliday": state_holiday,
#     "SchoolHoliday": 1 if school_holiday == "Yes" else 0,
#     "StoreType": str(store_info["STORETYPE"]),
#     "Assortment": str(store_info["ASSORTMENT"]),
#     "CompetitionDistance": store_info["COMPETITIONDISTANCE"],
#     "CompetitionOpenSinceMonth": store_info["COMPETITIONOPENSINCEMONTH"],
#     "CompetitionOpenSinceYear": store_info["COMPETITIONOPENSINCEYEAR"],
#     "Promo2": store_info["PROMO2"],
#     "Promo2SinceWeek": store_info["PROMO2SINCEWEEK"],
#     "Promo2SinceYear": store_info["PROMO2SINCEYEAR"],
#     "PromoInterval": str(store_info["PROMOINTERVAL"]),
#     "Year": prediction_date.year,
#     "Month": prediction_date.month,
#     "Day": prediction_date.day,
#     "WeekOfYear": prediction_date.isocalendar().week,
#     "IsWeekend": 1 if day_of_week in [6, 7] else 0
# }

# input_df = pd.DataFrame([features])

# categorical_features = [
#     "StateHoliday",
#     "StoreType",
#     "Assortment",
#     "PromoInterval",
#     "Store"
# ]

# for col in categorical_features:
#     input_df[col] = input_df[col].astype(str)


# # --------------------------------------------------
# # 7. DISPLAY STORE DETAILS
# # --------------------------------------------------

# st.subheader("Selected Store Details")

# c1, c2, c3 = st.columns(3)

# c1.metric("Store ID", selected_store)
# c2.metric("Store Type", store_info["STORETYPE"])
# c3.metric(
#     "Competition Distance",
#     f'{store_info["COMPETITIONDISTANCE"]:,.0f}'
#     if pd.notna(store_info["COMPETITIONDISTANCE"])
#     else "Not available"
# )


# # --------------------------------------------------
# # 8. SALES PREDICTION
# # --------------------------------------------------

# st.divider()

# if st.button("Predict Sales Revenue", type="primary"):

#     if is_open == "No":

#         predicted_sales = 0.0

#     else:

#         predicted_sales = float(
#             model.predict(input_df)[0]
#         )

#         predicted_sales = max(predicted_sales, 0)

#     st.subheader("Prediction Result")

#     st.metric(
#         label="Predicted Sales Revenue",
#         value=f"{predicted_sales:,.2f}"
#     )

#     st.success("Sales prediction completed successfully!")

#     # --------------------------------------------------
#     # 9. SAVE PREDICTION IN SNOWFLAKE
#     # --------------------------------------------------

#     session.sql(f"""
#         CREATE TABLE IF NOT EXISTS {HISTORY_TABLE} (
#             PREDICTION_TIMESTAMP TIMESTAMP_NTZ
#                 DEFAULT CURRENT_TIMESTAMP(),
#             STORE_ID NUMBER,
#             PREDICTION_DATE DATE,
#             PROMO NUMBER,
#             PREDICTED_SALES FLOAT
#         )
#     """).collect()

#     session.sql(
#         f"""
#         INSERT INTO {HISTORY_TABLE}
#         (STORE_ID, PREDICTION_DATE, PROMO, PREDICTED_SALES)
#         VALUES (?, ?, ?, ?)
#         """,
#         params=[
#             int(selected_store),
#             prediction_date.isoformat(),
#             1 if promo == "Yes" else 0,
#             predicted_sales
#         ]
#     ).collect()

#     st.info("Prediction saved to Snowflake successfully!")

# # --------------------------------------------------
# # 10. FOOTER
# # --------------------------------------------------

# st.divider()

# st.caption(
#     "Sales Revenue Prediction | "
#     "Powered by Python, Scikit-learn and Snowflake"
# )





import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from datetime import date
from snowflake.snowpark.context import get_active_session

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Sales Revenue Predictor",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# 2. APPLICATION CONFIGURATION
# --------------------------------------------------

DATABASE = "SALES_ML_DB"
SCHEMA = "SALES_PREDICTION"

MODEL_STAGE = (
    "@SALES_ML_DB.SALES_PREDICTION.MODEL_STAGE"
)

STORE_TABLE = (
    "SALES_ML_DB.SALES_PREDICTION.STORE_DETAILS"
)

MODEL_DIRECTORY = "/tmp/sales_model"
MODEL_FILE = os.path.join(
    MODEL_DIRECTORY,
    "sales_model.joblib"
)

# --------------------------------------------------
# 3. SNOWFLAKE CONNECTION
# --------------------------------------------------

@st.cache_resource
def get_session():
    return get_active_session()


session = get_session()

# --------------------------------------------------
# 4. LOAD TRAINED MACHINE LEARNING MODEL
# --------------------------------------------------

@st.cache_resource
def load_model():

    os.makedirs(
        MODEL_DIRECTORY,
        exist_ok=True
    )

    session.file.get(
        MODEL_STAGE,
        MODEL_DIRECTORY
    )

    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError(
            "sales_model.joblib was not found in the model stage."
        )

    model = joblib.load(MODEL_FILE)

    return model


# --------------------------------------------------
# 5. LOAD STORE INFORMATION
# --------------------------------------------------

@st.cache_data
def load_store_data():

    store_df = session.table(
        STORE_TABLE
    ).to_pandas()

    # Normalize Snowflake column names
    store_df.columns = [
        col.upper() for col in store_df.columns
    ]

    return store_df


# --------------------------------------------------
# 6. LOAD APPLICATION DATA
# --------------------------------------------------

try:

    model = load_model()
    store_df = load_store_data()

    st.sidebar.success(
        "Connected to Snowflake"
    )

    st.sidebar.success(
        "Machine learning model loaded"
    )

except Exception as e:

    st.error(
        f"Application initialization failed: {e}"
    )

    st.stop()


# --------------------------------------------------
# 7. APPLICATION HEADER
# --------------------------------------------------

st.title("📊 Sales Revenue Predictor")

st.write(
    """
    Predict daily store sales using a trained
    Machine Learning Regression Model.

    Select a store, enter the sales conditions,
    and generate an estimated sales prediction.
    """
)

st.divider()


# --------------------------------------------------
# 8. SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Choose a section",
    [
        "Dashboard",
        "Sales Prediction",
        "Store Information",
        "About Project"
    ]
)


# --------------------------------------------------
# 9. DASHBOARD
# --------------------------------------------------

if page == "Dashboard":

    st.header("Project Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Stores",
            f"{len(store_df):,}"
        )

    with col2:
        st.metric(
            "Model Type",
            "Linear Regression"
        )

    with col3:
        st.metric(
            "Prediction Target",
            "Daily Sales"
        )

    st.divider()

    st.subheader("Store Distribution")

    if "STORETYPE" in store_df.columns:

        store_counts = (
            store_df["STORETYPE"]
            .value_counts()
            .sort_index()
        )

        st.bar_chart(store_counts)

    st.subheader("Assortment Distribution")

    if "ASSORTMENT" in store_df.columns:

        assortment_counts = (
            store_df["ASSORTMENT"]
            .value_counts()
        )

        st.bar_chart(assortment_counts)

    st.info(
        """
        The application uses a trained Linear Regression
        model developed using the Rossmann Store Sales dataset.
        """
    )


# --------------------------------------------------
# 10. SALES PREDICTION
# --------------------------------------------------

elif page == "Sales Prediction":

    st.header("Generate Sales Prediction")

    st.write(
        "Enter the store and sales-related information below."
    )

    # Store selection
    store_ids = sorted(
        store_df["STORE"].dropna().astype(int).unique()
    )

    selected_store = st.selectbox(
        "Select Store",
        store_ids
    )

    # Retrieve selected store details
    selected_store_data = store_df[
        store_df["STORE"].astype(int) == selected_store
    ].iloc[0]

    st.subheader("Store Information")

    info1, info2, info3 = st.columns(3)

    with info1:
        st.write(
            f"**Store Type:** {selected_store_data['STORETYPE']}"
        )

    with info2:
        st.write(
            f"**Assortment:** {selected_store_data['ASSORTMENT']}"
        )

    with info3:
        distance = selected_store_data["COMPETITIONDISTANCE"]

        st.write(
            f"**Competition Distance:** {distance:,.0f}"
            if pd.notna(distance)
            else "**Competition Distance:** Not available"
        )

    st.divider()

    # Prediction inputs
    st.subheader("Sales Conditions")

    col1, col2 = st.columns(2)

    with col1:

        prediction_date = st.date_input(
            "Select Prediction Date",
            value=date.today()
        )

        open_status = st.selectbox(
            "Store Open?",
            ["Yes", "No"]
        )

        promo_status = st.selectbox(
            "Promotion Active?",
            ["Yes", "No"]
        )

    with col2:

        state_holiday = st.selectbox(
            "State Holiday",
            ["0", "a", "b", "c"],
            format_func=lambda x: {
                "0": "No Holiday",
                "a": "Public Holiday",
                "b": "Easter Holiday",
                "c": "Christmas"
            }[x]
        )

        school_holiday = st.selectbox(
            "School Holiday?",
            ["Yes", "No"]
        )

    # --------------------------------------------------
    # 11. PREPARE MODEL INPUT
    # --------------------------------------------------

    if st.button(
        "Predict Sales Revenue",
        type="primary",
        use_container_width=True
    ):

        if open_status == "No":

            st.success(
                "Predicted Sales Revenue: 0"
            )

            st.info(
                "The store is closed, so predicted sales are zero."
            )

        else:

            # Extract date features
            day_of_week = prediction_date.weekday() + 1

            year = prediction_date.year
            month = prediction_date.month
            day = prediction_date.day

            week_of_year = (
                prediction_date.isocalendar().week
            )

            is_weekend = int(
                day_of_week in [6, 7]
            )

            # Extract store-related features
            competition_distance = (
                selected_store_data["COMPETITIONDISTANCE"]
            )

            if pd.isna(competition_distance):
                competition_distance = 0

            competition_month = (
                selected_store_data[
                    "COMPETITIONOPENSINCEMONTH"
                ]
            )

            competition_year = (
                selected_store_data[
                    "COMPETITIONOPENSINCEYEAR"
                ]
            )

            promo2_since_week = (
                selected_store_data["PROMO2SINCEWEEK"]
            )

            promo2_since_year = (
                selected_store_data["PROMO2SINCEYEAR"]
            )

            # Prepare model input with exact training features
            input_data = pd.DataFrame([{

                "Store": str(selected_store),

                "DayOfWeek": day_of_week,

                "Open": 1,

                "Promo": int(
                    promo_status == "Yes"
                ),

                "StateHoliday": str(
                    state_holiday
                ),

                "SchoolHoliday": int(
                    school_holiday == "Yes"
                ),

                "StoreType": str(
                    selected_store_data["STORETYPE"]
                ),

                "Assortment": str(
                    selected_store_data["ASSORTMENT"]
                ),

                "CompetitionDistance": competition_distance,

                "CompetitionOpenSinceMonth": competition_month,

                "CompetitionOpenSinceYear": competition_year,

                "Promo2": int(
                    selected_store_data["PROMO2"]
                ),

                "Promo2SinceWeek": promo2_since_week,

                "Promo2SinceYear": promo2_since_year,

                "PromoInterval": str(
                    selected_store_data["PROMOINTERVAL"]
                ),

                "Year": year,

                "Month": month,

                "Day": day,

                "WeekOfYear": week_of_year,

                "IsWeekend": is_weekend

            }])

            # Ensure correct feature order
            feature_columns = [
                "Store",
                "DayOfWeek",
                "Open",
                "Promo",
                "StateHoliday",
                "SchoolHoliday",
                "StoreType",
                "Assortment",
                "CompetitionDistance",
                "CompetitionOpenSinceMonth",
                "CompetitionOpenSinceYear",
                "Promo2",
                "Promo2SinceWeek",
                "Promo2SinceYear",
                "PromoInterval",
                "Year",
                "Month",
                "Day",
                "WeekOfYear",
                "IsWeekend"
            ]

            input_data = input_data[
                feature_columns
            ]

            # Generate prediction
            try:

                prediction = model.predict(
                    input_data
                )[0]

                prediction = max(
                    0,
                    float(prediction)
                )

                st.divider()

                st.subheader(
                    "Prediction Result"
                )

                st.success(
                    "Sales prediction generated successfully!"
                )

                st.metric(
                    "Estimated Daily Sales",
                    f"{prediction:,.2f}"
                )

                # Prediction summary
                result_df = pd.DataFrame({

                    "Parameter": [
                        "Store ID",
                        "Prediction Date",
                        "Day of Week",
                        "Promotion",
                        "State Holiday",
                        "School Holiday"
                    ],

                    "Value": [
                        selected_store,
                        prediction_date.strftime("%d-%m-%Y"),
                        prediction_date.strftime("%A"),
                        promo_status,
                        state_holiday,
                        school_holiday
                    ]

                })

                st.subheader(
                    "Prediction Summary"
                )

                st.dataframe(
                    result_df,
                    use_container_width=True,
                    hide_index=True
                )

                # Visual representation
                st.subheader(
                    "Estimated Revenue"
                )

                st.bar_chart(
                    pd.DataFrame({
                        "Estimated Sales": [prediction]
                    }),
                    y="Estimated Sales"
                )

                if year > 2015:
                    st.warning(
                        "This date is beyond the model's training period "
                        "(2013–2015). Treat the prediction as an estimate "
                        "because it involves extrapolation."
                    )

            except Exception as e:

                st.error(
                    f"Prediction failed: {e}"
                )


# --------------------------------------------------
# 12. STORE INFORMATION
# --------------------------------------------------

elif page == "Store Information":

    st.header("Store Information")

    st.write(
        "Explore the store details used by the prediction model."
    )

    search_store = st.selectbox(
        "Choose Store ID",
        sorted(
            store_df["STORE"].dropna().astype(int).unique()
        )
    )

    store_details = store_df[
        store_df["STORE"].astype(int) == search_store
    ]

    st.subheader(
        f"Details for Store {search_store}"
    )

    st.dataframe(
        store_details,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("All Store Records")

    st.dataframe(
        store_df,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# 13. ABOUT THE PROJECT
# --------------------------------------------------

elif page == "About Project":

    st.header("About Sales Revenue Prediction")

    st.markdown(
        """
        ### Project Objective

        To predict daily sales revenue for retail stores
        using historical sales patterns and store-related
        information.

        ### Dataset

        Rossmann Store Sales dataset.

        ### Technologies Used

        - Python
        - Snowflake
        - Snowpark
        - Pandas
        - NumPy
        - Scikit-learn
        - Streamlit
        - Joblib

        ### Machine Learning Algorithm

        Linear Regression.

        ### Model Evaluation

        | Evaluation Metric | Result |
        |---|---:|
        | MAE | 1107.94 |
        | RMSE | 1539.02 |
        | R² Score | 0.828 |

        ### Features Used

        - Store information
        - Day of week
        - Promotions
        - State holidays
        - School holidays
        - Competition distance
        - Assortment
        - Store type
        - Date-based features

        ### Storage

        The trained model and store information are
        stored in Snowflake.
        """
    )


# --------------------------------------------------
# 14. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Sales Revenue Prediction | Python + Machine Learning + Snowflake"
)

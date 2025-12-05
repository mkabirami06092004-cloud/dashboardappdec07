import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(layout="wide")

st.title('Pizza Sales Dashboard')

# Load the dataset
@st.cache_data
def load_data():
    df = pd.read_csv('pizza_sales.csv')
    return df

df = load_data()

# Pre-processing for numerical columns for filters and plots
numerical_cols = df.select_dtypes(include=['number']).columns.tolist()

# --- Data Filtering ---
st.subheader('Data Filtering')

# Filter 'order_quantity' using a slider
if 'order_quantity' in numerical_cols:
    min_quantity = int(df['order_quantity'].min())
    max_quantity = int(df['order_quantity'].max())
    quantity_range = st.slider(
        'Select Order Quantity Range',
        min_value=min_quantity,
        max_value=max_quantity,
        value=(min_quantity, max_quantity)
    )
    df_filtered = df[(df['order_quantity'] >= quantity_range[0]) & (df['order_quantity'] <= quantity_range[1])]
else:
    st.warning("'order_quantity' column not found or is not numerical. Skipping slider filter.")
    df_filtered = df.copy()

st.write(f"Displaying {len(df_filtered)} rows after filtering.")

# --- Interactive Scatter Plot ---
st.subheader('Interactive Scatter Plot')

# Identify available columns for plotting
available_cols = df_filtered.columns.tolist()

if len(available_cols) >= 2:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        x_axis = st.selectbox('Select X-axis', available_cols, index=0)
    with col2:
        # Try to select a different column for Y-axis if available
        default_y_index = 1 if len(available_cols) > 1 else 0
        y_axis = st.selectbox('Select Y-axis', available_cols, index=default_y_index if default_y_index < len(available_cols) else 0)
    with col3:
        color_col = st.selectbox('Select Color (Optional)', ['None'] + available_cols, index=0)
    with col4:
        size_col = st.selectbox('Select Size (Optional)', ['None'] + numerical_cols, index=0)

    fig_scatter = px.scatter(
        df_filtered,
        x=x_axis,
        y=y_axis,
        color=color_col if color_col != 'None' else None,
        size=size_col if size_col != 'None' else None,
        hover_name=df_filtered.columns[0] if len(df_filtered.columns) > 0 else None,
        title=f'Scatter Plot of {y_axis} vs {x_axis}'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.warning("Not enough columns in the dataset to create a scatter plot.")

# --- Interactive Pie Chart ---
st.subheader('Interactive Pie Chart')

if len(available_cols) >= 2:
    pie_col1, pie_col2 = st.columns(2)
    with pie_col1:
        # Default to a categorical column if available for names
        categorical_cols = df_filtered.select_dtypes(include=['object', 'category']).columns.tolist()
        default_names_index = 0
        if 'pizza_category' in categorical_cols: default_names_index = categorical_cols.index('pizza_category')
        elif 'pizza_name' in categorical_cols: default_names_index = categorical_cols.index('pizza_name')
        elif len(categorical_cols) > 0: default_names_index = 0
        else: categorical_cols = available_cols # Fallback to all if no categorical

        pie_names = st.selectbox('Select Category (Slices)', categorical_cols, index=default_names_index if len(categorical_cols) > default_names_index else 0)
    with pie_col2:
        # Default to a numerical column if available for values
        default_values_index = 0
        if 'total_price' in numerical_cols: default_values_index = numerical_cols.index('total_price')
        elif 'quantity' in numerical_cols: default_values_index = numerical_cols.index('quantity')
        elif len(numerical_cols) > 0: default_values_index = 0
        else: numerical_cols = available_cols # Fallback to all if no numerical

        pie_values = st.selectbox('Select Value (Size of Slices)', numerical_cols, index=default_values_index if len(numerical_cols) > default_values_index else 0)

    # Aggregate data for pie chart if names column has many unique values
    if df_filtered[pie_names].nunique() > 20: # Limit number of slices for readability
        pie_data = df_filtered.groupby(pie_names)[pie_values].sum().reset_index()
        fig_pie = px.pie(
            pie_data,
            names=pie_names,
            values=pie_values,
            title=f'Distribution of {pie_values} by {pie_names}',
            hole=0.3
        )
    else:
        fig_pie = px.pie(
            df_filtered,
            names=pie_names,
            values=pie_values,
            title=f'Distribution of {pie_values} by {pie_names}',
            hole=0.3
        )
    st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.warning("Not enough columns in the dataset to create a pie chart.")

# --- Summary Report ---
st.subheader('Summary Report')

if st.button('Show Summary Statistics'):
    if not df_filtered.empty:
        st.write("### Descriptive Statistics for Filtered Data")
        st.write(df_filtered.describe())
    else:
        st.info("No data to display summary statistics for after filtering.")

st.markdown('''
**Column Information:**
- **order_id**: Unique identifier for each order.
- **pizza_id**: Unique identifier for each pizza within an order.
- **order_date**: Date when the order was placed.
- **order_time**: Time when the order was placed.
- **item_price**: Price of a single item.
- **quantity**: Number of items ordered.
- **total_price**: Total price for the order item (item_price * quantity).
- **pizza_size**: Size of the pizza (e.g., S, M, L, XL, XXL).
- **pizza_category**: Category of the pizza (e.g., Classic, Veggie, Chicken, Supreme).
- **pizza_ingredients**: List of ingredients in the pizza.
- **pizza_name**: Name of the pizza.
''')

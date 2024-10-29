import streamlit as st
import pandas as pd
import boto3
import json
import os

# Set environment variables using st.secrets
os.environ["TEAM_API_KEY"] = st.secrets["TEAM_API_KEY"]
AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]

from aixplain.factories import ModelFactory

# Set Streamlit page config to wide layout
st.set_page_config(layout="wide")

# Inject custom CSS to widen table columns
st.markdown("""
    <style>
        .stButton > button {
            width: 100%;
        }
        .stDataFrame {
            max-width: 100% !important;
        }
        .stTextInput {
            max-width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Function to extract text from image using Textract and external model
def extract_text_from_image(image_file):
    textract_client = boto3.client(
        'textract',
        region_name='us-east-1',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    image_bytes = image_file.read()

    response = textract_client.detect_document_text(Document={'Bytes': image_bytes})
    receipt_data = ""
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE':
            receipt_data += item['Text'] + '\n'

    model = ModelFactory.get("6414bd3cd09663e9225130e8")

    model_output = model.run({
        "text": f"""
        Extract the item names and final prices after discounts from the following receipt.

        Receipt:
        {receipt_data}

        Only return a dictionary (with no other extra texts outside of the dictionary) where the keys are the item names and the values are the counts and prices (Note this is price per item. If an item appears multiple times, dont sum up the prices). 
        Note that the count of each item should determined by how many times that item's name appears in the list. Dont use any other number to determine count. The counts and prices should be a list.
        Include tax as well. Count for the tax should be 1. Also, include the bag charges, if any, in the same format as Tax (1 count). Dont include "convenience item" as an item key. Dont include "SGST" or "CGST" as item keys.
        MAKE SURE THE PRICE AND COUNTS FOR EACH ITEM ARE INTEGTER/FLOAT, NOT STRING.
        """,
        "max_tokens": 6000,
        "temperature": 0.1
    })

    bill_dict = json.loads(model_output['data'])
    
    # Create a list where each item is duplicated by count
    expanded_items = []
    for item, values in bill_dict.items():
        item_count, item_price = values['item_count'], values['price_per']
        expanded_items.extend([(item, item_price) for _ in range(int(item_count))])

    # Convert expanded list into a DataFrame
    expanded_df = pd.DataFrame(expanded_items, columns=['Item', 'Price'])
    
    return expanded_df

# Title
st.title("Bill Splitter")

# Step 1: File Uploader (Use session state to store file)
if 'uploaded_image' not in st.session_state:
    st.session_state['uploaded_image'] = None

uploaded_image = st.file_uploader("Upload your bill image", type=["jpg", "png", "jpeg"])

# Store the uploaded image in session state
if uploaded_image is not None:
    st.session_state['uploaded_image'] = uploaded_image

# Ensure session state variables are initialized
if 'uploaded_image' not in st.session_state:
    st.session_state['uploaded_image'] = None

if 'checkbox_state' not in st.session_state:
    st.session_state.checkbox_state = {}

if 'select_all_state' not in st.session_state:
    st.session_state.select_all_state = {}

# Step 2: Input names
names_input = st.text_input("Enter names of people involved (comma-separated)", "Alice,Bob,Charlie")
names_list = [name.strip() for name in names_input.split(",")]

# On Submit
if st.button("Submit"):
    if st.session_state['uploaded_image'] is not None:
        # Extract text from the image (stored in session state)
        df = extract_text_from_image(st.session_state['uploaded_image'])

        # Store the DataFrame in session state to avoid reinitialization
        st.session_state['df'] = df

# Retrieve the DataFrame from session state
if 'df' in st.session_state:
    df = st.session_state['df']

    # Calculate total bill price
    total_bill_price = df['Price'].sum()

    # Display the total bill price
    st.write(f"**Total Bill Price: ${total_bill_price:.2f}**")

    # Step 3: Display the table with checkboxes for each person
    st.write("Please check the items each person is responsible for:")
    for index, row in df.iterrows():
        cols = st.columns(len(names_list) + 3)  # Extra column for "Select All" button
        cols[0].write(row['Item'])  # Item name
        cols[1].write(f"${row['Price']:.2f}")  # Item price

        # Loop through each name and render the checkbox
        for i, name in enumerate(names_list):
            checkbox_key = f"{name}_{index}"

            # Retrieve checkbox state from session state (or default to False)
            checkbox_state = st.session_state.checkbox_state.get(checkbox_key, False)

            # Show the checkbox and store state in session state
            df.at[index, name] = cols[i + 2].checkbox(name, value=checkbox_state, key=checkbox_key)

            # Update checkbox state in session state after click
            st.session_state.checkbox_state[checkbox_key] = df.at[index, name]

    # Step 4: Generate the split
    if st.button("Generate Split"):
        total_per_person = {name: 0.0 for name in names_list}

        for index, row in df.iterrows():
            # Count how many people selected this item
            people_who_selected = [name for name in names_list if row.get(name, False)]
            num_people = len(people_who_selected)

            if num_people > 0:  # Only split if at least one person selected the item
                price_per_person = row['Price'] / num_people

                # Add the split amount to each person who selected the item
                for name in people_who_selected:
                    total_per_person[name] += price_per_person

        st.write("Total per person:")
        for name in names_list:
            st.write(f"{name}: ${total_per_person[name]:.2f}")

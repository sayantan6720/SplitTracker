# SplitTracker

**SplitTracker** is a bill-splitting tool designed to simplify the process of calculating and tracking how much each participant owes for shared expenses. Using AWS Textract, it extracts text from bill images and automates the division of costs among multiple people.

## Features

- **Upload and Parse Bill Images**: Upload a photo of your bill, and SplitTracker uses AWS Textract to read and extract item details and prices automatically.
- **Fair Expense Calculation**: Easily select which participants are responsible for each item and calculate the exact amount each person owes.
- **Custom Splits**: Supports custom splits, allowing uneven distribution of costs between participants.
- **Total Bill Calculation**: Displays the total bill amount and the individual totals for each participant.
- **"Select All" Functionality**: Conveniently select all items for a participant, making it faster to assign shared expenses.
- **Intuitive UI**: SplitTracker is powered by Streamlit, providing a simple and user-friendly interface.

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up your AWS credentials to use AWS Textract. Ensure you have a valid `TEAM_API_KEY` for the AI-powered model.

## Usage

1. Run the application:
    ```bash
    streamlit run app.py
    ```

2. Upload a bill image (JPG, PNG, or JPEG format).

3. Enter the names of the participants involved in splitting the bill.

4. Review the extracted data and assign items to the appropriate participants using checkboxes.

5. Click **Generate Split** to calculate the amount owed by each participant.

## Technologies Used

- **Python**: Core programming language used for development.
- **Streamlit**: For building an interactive web-based interface.
- **AWS Textract**: For OCR and text extraction from images.
- **Pandas**: For data processing and managing tabular data.


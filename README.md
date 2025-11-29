# FinTrackAI - Universal Finance Tracker

FinTrackAI is a personal finance application that uses AI to ingest data from messy sources (CSV, Text, Excel) and provides a conversational interface to interact with your financial data.

## Features

-   **AI Data Ingestion**: Upload raw statements (CSV, Excel, or plain text) and let the LLM extract structured transaction data.
-   **Conversational Interface**: Chat with your data ("How much did I spend on coffee?").
-   **Bulk Category Updates**: Use natural language to update categories (e.g., "Change Walmart to Groceries").
-   **Service-Repository Architecture**: Modular backend design allowing easy swapping of LLM providers (Gemini, Local Ollama).
-   **Modern Stack**: FastAPI (Python) backend and React + Vite + Tailwind frontend.

## Tech Stack

-   **Backend**: Python 3.11+, FastAPI, Motor (MongoDB), Google Generative AI / Ollama.
-   **Frontend**: Node.js 20+, React, Vite, Tailwind CSS.
-   **Database**: MongoDB.

## Setup Instructions

### Prerequisites

-   Python 3.11+
-   Node.js 20+
-   MongoDB running locally (default port 27017)

### Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Configure Environment Variables:
    -   Create a `.env` file in `backend/`.
    -   Add your Google API Key:
        ```env
        GEMINI_API_KEY=your_api_key_here
        GEMINI_MODEL=gemini-2.0-flash # or gemini-1.5-flash
        LLM_TYPE=CLOUD # or LOCAL
        MONGO_URL=mongodb://localhost:27017
        ```
4.  Run the server:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

### Frontend Setup

1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
4.  Open `http://localhost:5173` in your browser.

## Usage

1.  **Upload**: Drag and drop a bank statement or paste text into the upload zone.
2.  **Chat**: Ask questions about your spending in the chat widget.
3.  **Update Categories**: Type commands like "Change Uber to Transport" to bulk update categories.

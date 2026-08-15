# Cryptocurrency Projects

A simple full-stack application built as a technical task.

The backend is implemented with **Python and FastAPI** and retrieves cryptocurrency market data from the **CoinGecko API**. It applies the required filtering criteria and exposes the resulting data through a REST API endpoint.

The frontend is implemented with **React and TypeScript**. It communicates only with the backend and allows the user to:

* View the filtered cryptocurrency projects
* Search projects by name using partial matching
* Filter projects by a user-defined maximum Fully Diluted Valuation (FDV)
* Sort projects by Market Capitalization
* Sort projects by 24h Trading Volume

## Project Structure

```text
test_task/
├── backend/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── key.txt
└── README.md
```

## Running the Application

### 1. CoinGecko API Key

Create a `key.txt` file in the project root and place your CoinGecko Demo API key inside it:

```text
CG-your-api-key
```

The file should contain only the API key.

### 2. Backend

Navigate to the backend directory:

```bash
cd backend
```

Create and activate a virtual environment if needed:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

The cryptocurrency endpoint is:

```text
GET /api/coins
```

### 3. Frontend

Open another terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install the dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

## Filtering Assumption

The original task requires projects to satisfy all of the following conditions:

* Market Capitalization > $0
* `preview_listing = true`
* Max Supply equals Total Supply
* Fully Diluted Valuation (FDV) < $100M
* 24h Trading Volume > $50K
* Total Value Locked (TVL) > $50K

During implementation, applying all of these conditions to the current CoinGecko API data resulted in an empty list.

The restrictive condition was:

```text
preview_listing = true
```

Projects marked by CoinGecko as preview listings are generally projects that are not yet fully active listings. As a result, they may not have the live market data required by the other conditions, such as market capitalization, trading volume, and TVL.

During testing, projects successfully passed the market capitalization, FDV, volume, and supply filters, but none of them also had:

```text
preview_listing = true
```

Therefore, the `preview_listing` filter was disabled in the submitted demonstration version so that the application can return real CoinGecko projects and the frontend functionality can be demonstrated.

All other required backend filters remain applied:

```text
Market Capitalization > $0
Max Supply = Total Supply
FDV < $100M
24h Trading Volume > $50K
TVL > $50K
```

If the `preview_listing = true` condition is enabled as specified in the original requirements, the backend currently returns an empty list because no projects in the retrieved dataset satisfy all of the conditions simultaneously.

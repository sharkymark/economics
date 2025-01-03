# Economic Indicators vs. ETF Analysis

This Python application analyzes and visualizes the relationship between various economic indicators and ETF performance.

## Features
- Correlates bank ETF performance with economic indicators
  - Fetches KBE ETF data from Yahoo Finance using yfinance
  - Retrieves economic indicators from FRED API:
    - New Home Sales (HSN1F)
    - Housing Starts (HOUST)
    - 10-Year Treasury Yield (GS10)
  - Calculates year-over-year (YoY) changes for all series
  - Creates a comparative visualization of all datasets
- Correlates 10 year benchmark treasury rate with Russell 2000 ETF performance
  - Fetches IWM and IMO (growth) ETF data from Yahoo Finance using yfinance
  - Retrieves 10-Year Treasury Yield (GS10) from FRED API
  - Calculates year-over-year (YoY) changes for both series
  - Creates a comparative visualization of both datasets

## Installation
1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up FRED API key:
   - Create a `.env` file in the project root
   - Add your FRED API key:
     ```
     FRED_API_KEY=your_api_key_here
     ```
4. Run the application:
   ```bash
   python main.py
   ```

## Data Sources
- **Yahoo Finance** (via yfinance):
  - ETF data
- **FRED (Federal Reserve Economic Data)**:
  - New Home Sales (HSN1F)
  - Housing Starts (HOUST)
  - 10-Year Treasury Yield (GS10)

## Requirements
- Python 3.8+
- Required packages (see requirements.txt):
  - yfinance
  - fredapi
  - pandas
  - matplotlib
  - python-dotenv

## Usage
The application will:
1. Fetch and process all data
2. Print key statistics about each dataset
3. Display an interactive plot showing YoY changes for all series
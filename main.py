import requests
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def fetch_housing_data():
    """Fetch new home sales data from Census Bureau API"""
    # Use FRED API for New Home Sales data
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": "HSN1F",
        "api_key": "329c6ea515537c0bfa6823cc9f9a08b1",
        "file_type": "json",
        "observation_start": "2018-01-01"
    }
    try:
        response = requests.get(url, params=params)
        print("API Response:", response.text)  # Print raw response for debugging
        response.raise_for_status()
        # Process the FRED response
        data = response.json()
        if 'observations' not in data:
            print("Invalid API response format")
            return None
            
        observations = data['observations']
        if not observations:
            print("No data found in API response")
            return None
            
        # Extract year and sales data
        processed_data = []
        for obs in observations:
            try:
                year = int(obs['date'][:4])
                sales = float(obs['value'])
                processed_data.append((year, sales))
            except (KeyError, ValueError) as e:
                print(f"Error processing observation: {e}")
                continue
        
        if len(processed_data) < 2:
            print("Not enough data points for YoY calculation")
            return None
            
        # Calculate year-over-year percentage change
        years = [row[0] for row in processed_data]
        sales = [row[1] for row in processed_data]
        yoy_changes = [(sales[i] - sales[i-1])/sales[i-1]*100
                      for i in range(1, len(sales))]
        
        print(f"Processed {len(yoy_changes)} YoY changes")
        return list(zip(years[1:], yoy_changes))
    except requests.exceptions.RequestException as e:
        print(f"Error fetching housing data: {e}")
        return None

def fetch_etf_data():
    """Fetch bank ETF data using yfinance"""
    try:
        # Possible Bank ETFs: KBE, KBWB, IAT, VFH, XLF
        etf = yf.Ticker("KBE")
        # Get 6 years of historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*6)
        data = etf.history(start=start_date, end=end_date)
        return data
    except Exception as e:
        print(f"Error fetching ETF data: {e}")
        return None

def process_and_plot(housing_data, etf_data):
    """Process and plot the data"""
    if housing_data is None or etf_data is None or etf_data.empty:
        print("Missing or invalid data - cannot plot")
        return
        
    # Process housing data
    years = [row[0] for row in housing_data]
    yoy_changes = [row[1] for row in housing_data]
    
    # Process ETF data - calculate year-over-year percentage change
    etf_data = etf_data.resample('YE').last()
    etf_years = etf_data.index.year
    etf_prices = etf_data['Close'].pct_change() * 100
    
    # Format x-axis
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: int(x)))
    
    # Simple plot with both datasets
    plt.figure(figsize=(12, 6))
    
    # Plot housing YoY changes
    plt.plot(years, yoy_changes, 'b-', label='New Home Sales YoY Change')
    
    # Plot ETF YoY changes
    plt.plot(etf_years, etf_prices, 'r-', label='Bank ETF YoY Change')
    
    # Format plot
    plt.title("USA New Home Sales vs NASDAQ-100 ETF YoY Changes (2010-2024)")
    plt.xlabel('Year')
    plt.ylabel('YoY Change (%)')
    plt.grid(True)
    plt.legend()
    
    # Show plot
    plt.show(block=True)

def main():
    housing_data = fetch_housing_data()
    etf_data = fetch_etf_data()
    process_and_plot(housing_data, etf_data)

if __name__ == "__main__":
    main()
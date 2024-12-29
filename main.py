import yfinance as yf
import fredapi
import matplotlib.pyplot as plt
import pandas as pd
import urllib3
import ssl
import datetime
import os
from dotenv import load_dotenv

# Disable SSL verification warnings
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from .env file
load_dotenv()

def get_kbe_data() -> pd.DataFrame:
    """Get KBE ETF data from Yahoo Finance
    
    Returns:
        pd.DataFrame: DataFrame containing KBE historical data
    
    Raises:
        Exception: If there's an error fetching data from Yahoo Finance
    """
    try:
        kbe = yf.Ticker("KBE")
        data = kbe.history(period="5y")
        if data.empty:
            raise ValueError("No data returned from Yahoo Finance")
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch KBE data: {str(e)}")

def get_new_home_sales_data():
    """Get new home sales data from FRED
    
    Returns:
        pd.DataFrame: DataFrame containing new home sales data
    
    Raises:
        ValueError: If FRED_API_KEY is not set in environment variables
        Exception: For any FRED API related errors
    """
    fred_api_key = os.getenv("FRED_API_KEY")
    if not fred_api_key:
        raise ValueError("FRED_API_KEY environment variable is not set")

    try:
        fred = fredapi.Fred(api_key=fred_api_key)
        # Calculate start date 5 years ago
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365*5)).strftime("%Y-%m-%d")

        data = fred.get_series("HSN1F", observation_start=start_date)
        data = pd.DataFrame(data, columns=["New Home Sales"])
        data.index = pd.to_datetime(data.index)
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch FRED data: {str(e)}")

def calculate_yoy(data: pd.DataFrame, column: str = "Close") -> pd.DataFrame:
    """Calculate year-over-year changes for financial data
    
    Args:
        data (pd.DataFrame): DataFrame containing financial data
        column (str): Column name to calculate YoY changes for
    
    Returns:
        pd.DataFrame: DataFrame with added YoY change column
    
    Raises:
        ValueError: If required columns are missing
    """
    if column not in data.columns:
        raise ValueError(f"Input data must contain '{column}' column")
    
    data["YoY"] = data[column].pct_change(252) * 100  # Approximately 252 trading days per year
    return data

def plot_data(kbe_data: pd.DataFrame, new_home_sales_data: pd.DataFrame) -> None:
    """Plot KBE ETF and new home sales YoY changes
    
    Args:
        kbe_data (pd.DataFrame): DataFrame containing KBE YoY data
        new_home_sales_data (pd.DataFrame): DataFrame containing new home sales YoY data
    """
    # Print data ranges being plotted
    print("Plotting KBE Data Range:", kbe_data.index.min(), "to", kbe_data.index.max())
    print("Plotting New Home Sales Data Range:", new_home_sales_data.index.min(), "to", new_home_sales_data.index.max())

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(kbe_data.index, kbe_data["YoY"], color="blue", label="KBE YoY Change")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("KBE YoY Change (%)", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.grid(True, linestyle="--", alpha=0.7)

    ax2 = ax1.twinx()
    ax2.plot(new_home_sales_data.index, new_home_sales_data["YoY"],
             color="red", label="New Home Sales YoY Change")
    ax2.set_ylabel("New Home Sales YoY Change (%)", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    # Combine legends from both axes
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper left")

    plt.title("KBE ETF and New Home Sales YoY Changes")
    plt.tight_layout()
    plt.show()

def main():
    kbe_data = get_kbe_data()
    print("KBE Data Start Date:", kbe_data.index.min())
    print("KBE Data End Date:", kbe_data.index.max())
    kbe_data = calculate_yoy(kbe_data)
    new_home_sales_data = get_new_home_sales_data()
    
    # Resample new home sales data to daily frequency
    new_home_sales_data = new_home_sales_data.resample('D').ffill()
    
    # Calculate YoY for both datasets
    # Calculate YoY for both datasets
    kbe_data = calculate_yoy(kbe_data)
    print("KBE columns after YoY calculation:", kbe_data.columns)
    new_home_sales_data = calculate_yoy(new_home_sales_data, column="New Home Sales")
    print("New Home Sales columns after YoY calculation:", new_home_sales_data.columns)
    
    # Ensure both datasets use timezone-aware timestamps
    kbe_data.index = kbe_data.index.tz_localize(None)
    new_home_sales_data.index = new_home_sales_data.index.tz_localize(None)
    
    # Print initial date ranges
    print("Initial KBE Data Start Date:", kbe_data.index.min())
    print("Initial New Home Sales Data Start Date:", new_home_sales_data.index.min())
    
    # Align start dates based on earliest available data
    start_date = min(kbe_data.index.min(), new_home_sales_data.index.min())
    
    # Forward fill KBE data if new home sales data starts earlier
    if new_home_sales_data.index.min() < kbe_data.index.min():
        print("Warning: New home sales data starts earlier than KBE data. Forward filling KBE data.")
        # Create a date range from the earliest date to latest date
        full_date_range = pd.date_range(start=start_date, end=max(kbe_data.index.max(), new_home_sales_data.index.max()))
        print("Full date range:", full_date_range.min(), "to", full_date_range.max())
        
        # Reindex KBE data to full date range and forward fill
        kbe_data = kbe_data.reindex(full_date_range).ffill()
        print("KBE data after forward fill - Start Date:", kbe_data.index.min())
    
    # Filter both datasets to aligned date range
    kbe_data = kbe_data[kbe_data.index >= start_date]
    new_home_sales_data = new_home_sales_data[new_home_sales_data.index >= start_date]
    
    # Print final date ranges
    print("Final KBE Data Start Date:", kbe_data.index.min())
    print("Final New Home Sales Data Start Date:", new_home_sales_data.index.min())
    
    print("Aligned Data Start Date:", start_date)
    print("KBE Data End Date:", kbe_data.index.max())
    print("New Home Sales Data End Date:", new_home_sales_data.index.max())
    
    plot_data(kbe_data, new_home_sales_data)

if __name__ == "__main__":
    main()

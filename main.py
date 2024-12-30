import yfinance as yf
import fredapi
import matplotlib.pyplot as plt
import pandas as pd
import urllib3
import ssl
import datetime
import os
from dotenv import load_dotenv
import argparse

YEARS = 10

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
        data = kbe.history(period=f"{YEARS}y")
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
        # Calculate start date
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365*YEARS)).strftime("%Y-%m-%d")

        data = fred.get_series("HSN1F", observation_start=start_date)
        data = pd.DataFrame(data, columns=["New Home Sales"])
        data.index = pd.to_datetime(data.index)
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch FRED data: {str(e)}")

def get_housing_starts_data():
    """Get housing starts data from FRED
    
    Returns:
        pd.DataFrame: DataFrame containing housing starts data
    
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
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365*YEARS)).strftime("%Y-%m-%d")

        data = fred.get_series("HOUST", observation_start=start_date)
        data = pd.DataFrame(data, columns=["Housing Starts"])
        data.index = pd.to_datetime(data.index)
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch FRED data: {str(e)}")

def get_existing_home_sales_data():
    """Get existing home sales data from FRED
    
    Returns:
        pd.DataFrame: DataFrame containing existing home sales data
    
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
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365*YEARS)).strftime("%Y-%m-%d")

        data = fred.get_series("EXHOSLUSM495S", observation_start=start_date)
        data = pd.DataFrame(data, columns=["Existing Home Sales"])
        data.index = pd.to_datetime(data.index)
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch FRED data: {str(e)}")

def get_10yr_treasury_data():
    """Get 10-year Treasury yield data from FRED
    
    Returns:
        pd.DataFrame: DataFrame containing 10-year Treasury yield data
    
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
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365*YEARS)).strftime("%Y-%m-%d")

        data = fred.get_series("GS10", observation_start=start_date)
        data = pd.DataFrame(data, columns=["10-Year Treasury"])
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

def plot_data(kbe_data: pd.DataFrame, new_home_sales_data: pd.DataFrame, housing_starts_data: pd.DataFrame = None, existing_home_sales_data: pd.DataFrame = None, treasury_data: pd.DataFrame = None) -> None:
    """Plot KBE ETF, new home sales, housing starts, and 10-year Treasury YoY changes
    
    Args:
        kbe_data (pd.DataFrame): DataFrame containing KBE YoY data
        new_home_sales_data (pd.DataFrame): DataFrame containing new home sales YoY data
        housing_starts_data (pd.DataFrame): DataFrame containing housing starts YoY data
        existing_home_sales_data (pd.DataFrame): DataFrame containing existing home sales YoY data
        treasury_data (pd.DataFrame): DataFrame containing 10-year Treasury YoY data
    """
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    ax1.plot(kbe_data.index, kbe_data["YoY"], color="blue", label="KBE YoY Change")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("KBE YoY Change (%)", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.grid(True, linestyle="--", alpha=0.7)

    ax2 = ax1.twinx()
    
    ax2.plot(new_home_sales_data.index, new_home_sales_data["YoY"],
             color="red", label="New Home Sales YoY Change")
    if args.housestart:
        ax2.plot(housing_starts_data.index, housing_starts_data["YoY"],
                 color="green", label="Housing Starts YoY Change")
    if args.tenyear:
        ax2.plot(treasury_data.index, treasury_data["YoY"],
                 color="purple", label="10-Year Treasury YoY Change")
    if args.existinghome:
        ax2.plot(existing_home_sales_data.index, existing_home_sales_data["YoY"],
                 color="orange", label="Existing Home Sales YoY Change")
    
    ax2.set_ylabel("Economic Indicators YoY Change (%)", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    # Combine legends from both axes
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper left")

    plt.title("KBE ETF, New Home Sales, Housing Starts, Existing Home Sales, and 10-Year Treasury YoY Changes")
    plt.tight_layout()
    plt.show()

def main():

    global YEARS, args

    parser = argparse.ArgumentParser(description="Plot financial and economic data.")
    parser.add_argument("--years", type=int, default=10, help="Number of years for historical data (default: 10)")
    parser.add_argument("--housestart", action="store_true", help="Plot housing starts data")
    parser.add_argument("--existinghome", action="store_true", help="Plot existing home sales data")
    parser.add_argument("--tenyear", action="store_true", help="Plot 10-year Treasury data")
    args = parser.parse_args()

    YEARS = args.years

    kbe_data = get_kbe_data()
    new_home_sales_data = get_new_home_sales_data()
    housing_starts_data = get_housing_starts_data()
    existing_home_sales_data = get_existing_home_sales_data()
    treasury_data = get_10yr_treasury_data()

    # Resample to daily frequency
    new_home_sales_data = new_home_sales_data.resample('D').ffill()
    housing_starts_data = housing_starts_data.resample('D').ffill()
    existing_home_sales_data = existing_home_sales_data.resample('D').ffill()
    treasury_data = treasury_data.resample('D').ffill()
    
    # Calculate YoY 
    kbe_data = calculate_yoy(kbe_data)
    new_home_sales_data = calculate_yoy(new_home_sales_data, column="New Home Sales")
    housing_starts_data = calculate_yoy(housing_starts_data, column="Housing Starts")
    existing_home_sales_data = calculate_yoy(existing_home_sales_data, column="Existing Home Sales")    
    treasury_data = calculate_yoy(treasury_data, column="10-Year Treasury")

    # Ensure datasets use timezone-aware timestamps
    kbe_data.index = kbe_data.index.tz_localize(None)
    new_home_sales_data.index = new_home_sales_data.index.tz_localize(None)
    housing_starts_data.index = housing_starts_data.index.tz_localize(None)
    existing_home_sales_data.index = existing_home_sales_data.index.tz_localize(None)
    treasury_data.index = treasury_data.index.tz_localize(None)
    
    # Align start dates based on earliest available data
    start_date = min(kbe_data.index.min(), new_home_sales_data.index.min(), housing_starts_data.index.min(), existing_home_sales_data.index.min(), treasury_data.index.min())
    
    # Forward fill KBE data if new home sales data starts earlier

    # Forward fill KBE data if any dataset starts earlier than KBE data
    if (new_home_sales_data.index.min() < kbe_data.index.min() or
        housing_starts_data.index.min() < kbe_data.index.min() or
        existing_home_sales_data.index.min() < kbe_data.index.min() or
        treasury_data.index.min() < kbe_data.index.min()):
        # Do something

        print("Warning: New home sales data starts earlier than KBE data. Forward filling KBE data.")
        # Create a date range from the earliest date to latest date
        full_date_range = pd.date_range(start=start_date, end=max(kbe_data.index.max(), new_home_sales_data.index.max() , housing_starts_data.index.max(), existing_home_sales_data.index.max(), treasury_data.index.max()))
        print("Full date range:", full_date_range.min(), "to", full_date_range.max())
        
        # Reindex KBE data to full date range and forward fill
        kbe_data = kbe_data.reindex(full_date_range).ffill()
        print("KBE data after forward fill - Start Date:", kbe_data.index.min())
    
    # Filter datasets to aligned date range
    kbe_data = kbe_data[kbe_data.index >= start_date]
    new_home_sales_data = new_home_sales_data[new_home_sales_data.index >= start_date]
    housing_starts_data = housing_starts_data[housing_starts_data.index >= start_date]
    existing_home_sales_data = existing_home_sales_data[existing_home_sales_data.index >= start_date]
    treasury_data = treasury_data[treasury_data.index >= start_date]
    
    
    plot_data(kbe_data, new_home_sales_data, housing_starts_data, existing_home_sales_data, treasury_data)

if __name__ == "__main__":
    main()

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

# Disable SSL verification warnings
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from .env file
load_dotenv()

def get_kbe_data(ticker: str="KBE", years: int=10) -> pd.DataFrame:
    """Get KBE ETF data from Yahoo Finance
    
    Returns:
        pd.DataFrame: DataFrame containing KBE historical data
    
    Raises:
        Exception: If there's an error fetching data from Yahoo Finance
    """
    try:
        fetch_years = years + 1 if years == 1 else years # fetch an extra year when only 1 year is requested

        # Calculate start date for Yahoo Finance call
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365 * fetch_years)).strftime("%Y-%m-%d")

        kbe = yf.Ticker(ticker)
        data = kbe.history(start=start_date, end=end_date)
        data.index = data.index.tz_localize(None) # make data timezone-naive for easier manipulation
        if data.empty:
            raise ValueError("No data returned from Yahoo Finance")
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch KBE data: {str(e)}")

def get_new_home_sales_data(years: int) -> pd.DataFrame:
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
        fetch_years = years + 1 if years == 1 else years  # Fetch an extra year when years=1
        # Calculate start date
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365 * fetch_years)).strftime("%Y-%m-%d")
        data = fred.get_series("HSN1F", observation_start=start_date)
        data = pd.DataFrame(data, columns=["New Home Sales"])
        data.index = pd.to_datetime(data.index)
        data.index = data.index.tz_localize(None)  # Make dates timezone naive
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch FRED data: {str(e)}")

def get_housing_starts_data(years: int) -> pd.DataFrame:
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
        fetch_years = years + 1 if years == 1 else years # Fetch an extra year when years=1
        # Calculate start date 5 years ago
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365 * fetch_years)).strftime("%Y-%m-%d")
        data = fred.get_series("HOUST", observation_start=start_date)
        data = pd.DataFrame(data, columns=["Housing Starts"])
        data.index = pd.to_datetime(data.index)
        data.index = data.index.tz_localize(None)  # Make dates timezone naive
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch FRED data: {str(e)}")

def get_10yr_treasury_data(years: int) -> pd.DataFrame:
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
        fetch_years = years + 1 if years == 1 else years # Fetch an extra year when years=1
        # Calculate start date x years ago
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365 * fetch_years)).strftime("%Y-%m-%d")
        data = fred.get_series("GS10", observation_start=start_date)
        data = pd.DataFrame(data, columns=["10-Year Treasury"])
        data.index = pd.to_datetime(data.index)
        data.index = data.index.tz_localize(None)  # Make dates timezone naive
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

def plot_data(kbe_data: pd.DataFrame, new_home_sales_data: pd.DataFrame, housing_starts_data: pd.DataFrame = None, treasury_data: pd.DataFrame = None, ticker: str="KBE") -> None:
    """Plot ETF, new home sales, housing starts, and 10-year Treasury YoY changes
    
    Args:
        kbe_data (pd.DataFrame): DataFrame containing KBE YoY data
        new_home_sales_data (pd.DataFrame): DataFrame containing new home sales YoY data
        housing_starts_data (pd.DataFrame): DataFrame containing housing starts YoY data
        treasury_data (pd.DataFrame): DataFrame containing 10-year Treasury YoY data
        ticker (str): Ticker symbol for ETF
    """
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    ax1.plot(kbe_data.index, kbe_data["YoY"], color="blue", label=f"{ticker} YoY Change")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("KBE YoY Change (%)", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.grid(True, linestyle="--", alpha=0.7)

    ax2 = ax1.twinx()
    
    ax2.plot(new_home_sales_data.index, new_home_sales_data["YoY"],
             color="red", label="New Home Sales YoY Change")
    if housing_starts_data is not None:
        ax2.plot(housing_starts_data.index, housing_starts_data["YoY"],
                 color="green", label="Housing Starts YoY Change")
    if treasury_data is not None:
        ax2.plot(treasury_data.index, treasury_data["YoY"],
                 color="purple", label="10-Year Treasury YoY Change")
    
    ax2.set_ylabel("Economic Indicators YoY Change (%)", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    # Combine legends from both axes
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper left")

    plt.title("KBE ETF, New Home Sales, Housing Starts, and 10-Year Treasury YoY Changes")
    plt.tight_layout()
    plt.show()

def get_etf_data(ticker: str, years: int=2) -> pd.DataFrame:
    """Get ETF data from Yahoo Finance
    
    Args:
        ticker (str): ETF ticker symbol
        years (int): Number of years of data to fetch
        
    Returns:
        pd.DataFrame: DataFrame containing ETF historical data
    """
    try:
        fetch_years = years + 1 if years == 1 else years
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365 * fetch_years)).strftime("%Y-%m-%d")

        etf = yf.Ticker(ticker)
        data = etf.history(start=start_date, end=end_date)
        data.index = data.index.tz_localize(None)
        if data.empty:
            raise ValueError(f"No data returned for {ticker}")
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch {ticker} data: {str(e)}")

def get_10yr_treasury_data(years: int=2) -> pd.DataFrame:
    """Get 10-year Treasury yield data from FRED"""
    fred_api_key = os.getenv("FRED_API_KEY")
    if not fred_api_key:
        raise ValueError("FRED_API_KEY environment variable is not set")
    try:
        fred = fredapi.Fred(api_key=fred_api_key)
        fetch_years = years + 1 if years == 1 else years
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365 * fetch_years)).strftime("%Y-%m-%d")
        data = fred.get_series("GS10", observation_start=start_date)
        data = pd.DataFrame(data, columns=["10-Year Treasury"])
        data.index = pd.to_datetime(data.index)
        data.index = data.index.tz_localize(None)
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch FRED data: {str(e)}")

def plot_correlation(treasury_data: pd.DataFrame, etf_data: dict) -> None:
    """Plot inverse correlation between 10-year treasury and ETFs"""
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Plot treasury yields
    ax1.plot(treasury_data.index, treasury_data["10-Year Treasury"], 
             color="blue", label="10-Year Treasury Yield")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("10-Year Treasury Yield (%)", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.grid(True, linestyle="--", alpha=0.7)

    ax2 = ax1.twinx()
    
    # Plot ETF prices
    for ticker, data in etf_data.items():
        ax2.plot(data.index, data["Close"], 
                 label=f"{ticker} Price")
    
    ax2.set_ylabel("ETF Price ($)", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    # Combine legends
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper left")

    plt.title("10-Year Treasury Yield vs Russell 2000 ETFs")
    plt.tight_layout()
    plt.show(block=False)
    
    # Wait for user input before returning to menu
    input("\nPress Enter to return to menu...")
    plt.close()

def display_menu() -> int:
    """Display menu and get user choice"""
    print("\nEconomic Data Analysis Menu")
    print("1. New Home Sales vs Banking ETF")
    print("2. 10-Year Treasury vs Russell 2000 ETFs") 
    print("3. Exit")
    while True:
        try:
            choice = int(input("Enter choice (1-3): "))
            if 1 <= choice <= 3:
                return choice
            print("Please enter a number between 1 and 3")
        except ValueError:
            print("Please enter a valid number")

def main():

    parser = argparse.ArgumentParser(description="Plot financial and economic data.")
    parser.add_argument("--years", type=int, default=10, help="Number of years for historical data (default: 10)")
    parser.add_argument("--housestart", action="store_true", help="Plot housing starts data")
    parser.add_argument("--tenyear", action="store_true", help="Plot 10-year Treasury data")
    parser.add_argument("--ticker", type=str, default="KBE", help="Ticker symbol to fetch data for (default: KBE)")

    args = parser.parse_args()

    years = args.years
    ticker = args.ticker

    while True:
        choice = display_menu()
        
        if choice == 1:
            try:


                kbe_data = get_kbe_data(ticker, years)
                new_home_sales_data = get_new_home_sales_data(years)

                housing_starts_data = None
                treasury_data = None

                if args.housestart:
                    housing_starts_data = get_housing_starts_data(years)
                
                if args.tenyear:
                    treasury_data = get_10yr_treasury_data(years)

                # Resample all dataframes to daily data using forward fill
                new_home_sales_data = new_home_sales_data.resample('D').ffill()
                if housing_starts_data is not None:
                    housing_starts_data = housing_starts_data.resample('D').ffill()
                if treasury_data is not None:
                    treasury_data = treasury_data.resample('D').ffill()


                # Calculate earliest start date from all of the data sources


                all_start_dates = [kbe_data.index.min(), new_home_sales_data.index.min()]
                if housing_starts_data is not None:
                    all_start_dates.append(housing_starts_data.index.min())
                if treasury_data is not None:
                    all_start_dates.append(treasury_data.index.min())

                earliest_start_date = min(all_start_dates)   
            
                print("Earliest start dates across datasets")
                print(f"KBE Data: ", kbe_data.index.min())
                print(f"New Home Sales Data: ", new_home_sales_data.index.min())
                if housing_starts_data is not None:
                    print(f"Housing Starts Data: ", housing_starts_data.index.min())
                if treasury_data is not None:
                    print(f"Treasury Data: ", treasury_data.index.min())


                # Filter each dataframe by the latest start date.
                kbe_data = kbe_data[kbe_data.index >= earliest_start_date]
                new_home_sales_data = new_home_sales_data[new_home_sales_data.index >= earliest_start_date]

                if housing_starts_data is not None:
                    housing_starts_data = housing_starts_data[housing_starts_data.index >= earliest_start_date]

                if treasury_data is not None:
                    treasury_data = treasury_data[treasury_data.index >= earliest_start_date]

                # Calculate YoY for all datasets now
                kbe_data = calculate_yoy(kbe_data)
                new_home_sales_data = calculate_yoy(new_home_sales_data, column="New Home Sales")

                if housing_starts_data is not None:
                    housing_starts_data = calculate_yoy(housing_starts_data, column="Housing Starts")

                if treasury_data is not None:
                    treasury_data = calculate_yoy(treasury_data, column="10-Year Treasury")

                """
                # Shift FRED data to account for lag
                new_home_sales_data.index = new_home_sales_data.index + pd.DateOffset(months=1)
                if housing_starts_data is not None:
                    housing_starts_data.index = housing_starts_data.index - pd.DateOffset(months=1)
                if treasury_data is not None:
                    treasury_data.index = treasury_data.index - pd.DateOffset(months=1)
                """

                # Shift FRED data for display, only using values from the filtered data set
                new_home_sales_data.index = new_home_sales_data.index.map(lambda x: x + pd.DateOffset(months=1) if x >= earliest_start_date else x)
                if housing_starts_data is not None:
                    housing_starts_data.index = housing_starts_data.index.map(lambda x: x + pd.DateOffset(months=1) if x >= earliest_start_date else x)
                if treasury_data is not None:
                    treasury_data.index = treasury_data.index.map(lambda x: x + pd.DateOffset(months=1) if x >= earliest_start_date else x)



                print("Latest Start Date:", earliest_start_date)
                print("KBE Data End Date:", kbe_data.index.max())
                print("New Home Sales Data End Date:", new_home_sales_data.index.max())
                if housing_starts_data is not None:
                    print("Housing Starts Data End Date:", housing_starts_data.index.max())
                if treasury_data is not None:
                    print("10-Year Treasury Data End Date:", treasury_data.index.max())
                
                plot_data(kbe_data, new_home_sales_data, housing_starts_data, treasury_data, ticker)

            except Exception as e:
                print(f"\nError: {str(e)}")
                input("Press Enter to return to menu...")


        elif choice == 2:
            # Get 2 years of data
            treasury_data = get_10yr_treasury_data(years)
            
            # Get Russell 2000 ETFs data
            etf_data = {
                "IWM": get_etf_data("IWM", years),
                "IWO": get_etf_data("IWO", years)
            }
            
            # Plot correlation
            plot_correlation(treasury_data, etf_data)
            
        elif choice == 3:
            print("Exiting program...")
            break




if __name__ == "__main__":
    main()

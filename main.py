import yfinance as yf
import fredapi
import matplotlib.pyplot as plt
import pandas as pd
import urllib3

def get_kbe_data():
    """Get KBE ETF data from Yahoo Finance"""
    kbe = yf.Ticker("KBE")
    data = kbe.history(period="5y")
    return data

def get_new_home_sales_data():
    """Get new home sales data from FRED"""
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    fred = fredapi.Fred(api_key="329c6ea515537c0bfa6823cc9f9a08b1")
    data = fred.get_series("HSN1F")
    data = pd.DataFrame(data, columns=["New Home Sales"])
    data.index = pd.to_datetime(data.index)
    return data

def calculate_yoy(data):
    """Calculate year-over-year changes"""
    data["YoY"] = data["Close"].pct_change(252) * 100
    return data

def plot_data(kbe_data, new_home_sales_data):
    """Plot KBE ETF and new home sales data"""
    fig, ax1 = plt.subplots()
    ax1.plot(kbe_data.index, kbe_data["YoY"], color="blue")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("KBE YoY Change (%)", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")

    ax2 = ax1.twinx()
    ax2.plot(new_home_sales_data.index, new_home_sales_data["New Home Sales"], color="red")
    ax2.set_ylabel("New Home Sales", color="red")
    ax2.tick_params(axis="y", labelcolor="red")

    plt.title("KBE ETF and New Home Sales YoY Change")
    plt.show()

def main():
    kbe_data = get_kbe_data()
    kbe_data = calculate_yoy(kbe_data)
    new_home_sales_data = get_new_home_sales_data()
    plot_data(kbe_data, new_home_sales_data)

if __name__ == "__main__":
    main()
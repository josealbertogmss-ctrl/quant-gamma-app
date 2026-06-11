import yfinance as yf


def load_ticker(symbol):

    ticker = yf.Ticker(symbol)

    return ticker


def get_spot_price(ticker):

    return float(
        ticker.history(
            period="1d"
        )["Close"].iloc[-1]
    )

get_expirations()

download_option_chain()

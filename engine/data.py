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

def get_expirations(ticker):

def download_option_chain(
    ticker,
    expiration
):

    return ticker.option_chain(expiration)

    return ticker.options

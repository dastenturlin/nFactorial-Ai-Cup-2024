from openai import OpenAI
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import time
import os
import re

api_key = os.environ["OPENAI_API_KEY"]

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI(
    api_key = api_key
)


def get_chat_completion(prompt, model="gpt-4o"):
    completion = client.chat.completions.create(
    model=model,
    messages=[
            {
                "role": "system",
                "content": """Imagine you are a financial analyst reviewing stocks.
                            Answer the following query with consideration to 
                            stock price, recent news, and company fundamentals. 
                            You can disregard the real-time data concerns. Just state the relevant information about the company. 
                            Try to fit the information into 8 sentences.
                            """
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )
    return re.sub(r'\n+', '\n', completion.choices[0].message.content)


def get_company_fundamentals(ticker):
    ticker = yf.Ticker(ticker)
    financials = ticker.financials
    balance_sheet = ticker.balance_sheet
    cash_flow = ticker.cashflow

    return financials, balance_sheet, cash_flow


def get_company_prices(ticker):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?symbol={ticker}&period1=1685024564&period2=9999999999&interval=1d'

    # Implement a simple retry mechanism
    for attempt in range(5):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            break
        else:
            print(f'Attempt {attempt + 1} failed with status code {response.status_code}')
            time.sleep(2 ** attempt)  # Exponential backoff

    # Print the response
    if response.status_code == 200:
        # print(response.json())
        print('success')
    else:
        print(f'Failed to retrieve data after {attempt + 1} attempts')

    timestamps = response.json()['chart']['result'][0]['timestamp']
    prices = response.json()['chart']['result'][0]['indicators']['quote'][0]['close']
    return timestamps, prices


def get_company_news_summary(ticker, api = 'UJROXZEBYSIYL1UK', model = 'gpt-4o'):
    # api = 'UJROXZEBYSIYL1UK'
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&time_from=20220519T0130&apikey={api}'
    r = requests.get(url)
    data = r.json()

    headlines = []
    for i in range(len(data['feed'])):
        headlines.append(data['feed'][i]['summary'])

    summary = " ".join(headlines)
    prompt = f"Summarize this text and give me the main insights in relation to a {ticker} stock." + summary
    completion = client.chat.completions.create(
    model=model,
    messages=[
            {
                "role": "system",
                "content": """Imagine you are an equity research analyst. 
                Read the prompt and build main bullet points with regard to the company.
                Keep it to 10 sentences long."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    return re.sub(r'\n+', '\n', completion.choices[0].message.content)


def get_company_investment_recommendation(ticker, model = 'gpt-4o'):
    new_prompt = """Given the input information about the stock, 
                    what would you say is the general consensus among analysts 
                    based on the text above? 
                    Choose between Bearish, Neutral, and Bullish, and state it in the 
                    first sentence, and argue why this is your recommendation. Keep it to 15 sentences long.
                    """ + get_company_news_summary(ticker)

    # print(new_prompt)
    # print('----------start-----------')
    # print('----------start-----------')
    new_completion = client.chat.completions.create(
    model=model,
    messages=[
            {
                "role": "system",
                "content": """Imagine you have to make a decision based by certain arguments
                Read the given information about the company and build main bullet points with regard to the company.
                Choose between Bearish, Neutral, and Bullish. Keep it to 15 sentences long."""
            },
            {
                "role": "user",
                "content": new_prompt
            }
        ],
    )

    return re.sub(r'\n+', '\n', new_completion.choices[0].message.content)


def get_financial_statements_analytics(ticker):
    # Takes a ticker and summarizes its income statement to return a buy/sell/hold recommendation
    pass


def get_portfolio_analytics(portfolio: dict, model = 'gpt-4o'):
    portfolio = ', '.join([f'{key} ({value}%)' for key, value in portfolio.items()])
    prompt = f"""let's say my portfolio consists of {portfolio}. 
    how would you describe my portfolio and what would you suggest adding?
    """
    completion = client.chat.completions.create(
    model=model,
    messages=[
            {
                "role": "system",
                "content": """Imagine you are a portfolio analyst reviewing stocks.
                            Answer the following query with consideration to 
                            stock price, recent news, and company fundamentals. Feel free to add recent news sources.
                            """
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )
    return re.sub(r'\n+', '\n', completion.choices[0].message.content)


def generate_company_knowledge_base(ticker, prompt, model='gpt-4o'):
    general_info = get_chat_completion(ticker)
    news = get_company_news_summary(ticker)
    rec = get_company_investment_recommendation(ticker)
    knowledge_base = general_info + '\n' + news + '\n' + rec
    print(knowledge_base)

    completion = client.chat.completions.create(
    model=model,
    messages=[
            {
                "role": "system",
                "content": """Imagine you are an investment research analyst. 
                            You have to answer the following queries using available 
                            information below. Come up with some bullet points and the arguments between them.
                            Disregard that you don't have real-time data available. 
                            You will have all important information in the report below. Keep it to 10 sentences long.
                            """ + knowledge_base
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )
    return re.sub(r'\n+', '\n', completion.choices[0].message.content)


if __name__ == '__main__':
    print("----- standard request -----")
    prompt = 'Can you give me main factors accounting for AAPL stock price?'
    print(generate_company_knowledge_base('AAPL', prompt))

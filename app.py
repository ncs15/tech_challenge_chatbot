from flask import Flask, request, render_template, session
import json


app = Flask(__name__)
app.config["SECRET_KEY"] = 'secret'
app.config["SESSION_PERMANENT"] = False


def get_data():
    #handle json reading
    try:
        file_name='Chatbot - stock data.json'
        with open(file_name) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
        return None  # Or return an empty list/dict depending on your use case
    except json.JSONDecodeError:
        print(f"Error: The file '{file_name}' contains invalid JSON.")
        return None  # Or handle as appropriate


def get_stockexchange():
    exchanges = [exchange['stockExchange'] for exchange in stock_data]
    return exchanges


def get_topstocks(picked_exchange):
    for exchange in stock_data:
        if exchange['stockExchange'] == picked_exchange:
            top_stocks=[stock['stockName'] for stock in exchange['topStocks']]
            return top_stocks


def get_price(picked_exchange,picked_stock):
    for exchange in stock_data:
        if exchange['stockExchange'] == picked_exchange:
            for stock in exchange['topStocks']:
                if stock['stockName'] == picked_stock:
                    return stock['price']


def initialize_conversation(exchanges):
    #default -clean conversation used for get request or for the main meniu
    session['conversation'] = [("Info", "Hello! Welcome to LSEG. I'm here to help you."),("Info", "Please select a Stoock Exchange")]
    for exchange in exchanges:
        session['conversation'] += [("Bot", exchange)]
    session['exchange'] = None
    session['state'] = 'select_exchange'


stock_data=get_data()
exchanges=get_stockexchange()


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST' :
        user_input = request.form['message']
        if user_input in exchanges or user_input=='Go Back':  # User selected an exchange
            if session['exchange']:
                #if 'Go Back' make the user_input == the already selected exchange
                user_input=session['exchange']
            session['conversation'] += [("You", user_input)]
            top_stocks=get_topstocks(user_input)
            session['conversation'] += [("Info", "Please select a stock.")]
            for stock in top_stocks:
                session['conversation'] += [("Bot", stock)]
            session['exchange'] = user_input
            session['state'] = 'select_stock'
        elif (session['exchange'] and session['state']=='select_stock'):
            price=get_price(session['exchange'],user_input)
            session['conversation'] += [("You", user_input),('Info', f"Stock Price of {user_input} is {price}. Please select an option.")]
            session['conversation'] += [("Bot", 'Main Menu'),("Bot", 'Go Back')]
            session['state']='price'
        elif user_input=='Main Menu':
            initialize_conversation(exchanges)

    elif request.method == 'GET' or 'conversation' not in session:
        initialize_conversation(exchanges)
    return render_template('chat.html', conversation=session['conversation'])

if __name__ == '__main__':
    app.run(debug=True)

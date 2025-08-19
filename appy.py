from flask import Flask, render_template, request
import heapq

app = Flask(__name__)

# Sample stock market data (company: stock price)
stock_data = {
    "Apple": 150,
    "Google": 2800,
    "Amazon": 3400,
    "Microsoft": 299,
    "Tesla": 730,
    "Meta": 355,
    "Netflix": 590
}

@app.route("/", methods=["GET", "POST"])
def index():
    top_stocks = []
    if request.method == "POST":
        try:
            k = int(request.form["k"])
            # Use heapq to get top k stocks
            top_stocks = heapq.nlargest(k, stock_data.items(), key=lambda x: x[1])
        except:
            top_stocks = [("Error", "Invalid Input")]
    return render_template("index.html", stocks=top_stocks, all_stocks=stock_data)


if __name__ == "__main__":
    # Run locally on port 5000
    app.run(debug=True, host="0.0.0.0", port=5000)

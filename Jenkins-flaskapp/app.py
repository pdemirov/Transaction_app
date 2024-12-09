# CODE TO BE FIXED
from flask import Flask, request, url_for, redirect, render_template, jsonify
from elasticsearch import Elasticsearch, NotFoundError

# Instantiate Flask functionality
app = Flask(__name__)

#connect to Elasticsearch
es = Elasticsearch(["http://elasticsearch:9200"])


# Index name for Elasticsearch
INDEX_NAME = "transactions"

# Ensure the index exists (optional)
try:
    print('first try passed')
    try:
        es.indices.get(index=INDEX_NAME)
        print('the GET index is: ' + INDEX_NAME)
    except NotFoundError:
        es.indices.create(index=INDEX_NAME)
        print('the Created index is: ' + INDEX_NAME)
except:
    print('error in this block occured')

finally:
    print("Outer finally block executed")



# Read operation -----------------------------
@app.route("/")
def get_transactions():
# Query Elasticsearch for all transactions
    res = es.search(index=INDEX_NAME, body={"query": {"match_all": {}}})
    transactions = [hit['_source'] for hit in res['hits']['hits']]

    balanceSum = sum(transaction['amount'] for transaction in transactions)

    return render_template('transactions.html', transactions=transactions, data=balanceSum)


@app.route("/add", methods=["GET", "POST"])
def add_transaction():
    if request.method == "POST":
        res = es.search(index=INDEX_NAME, body={"query": {"match_all": {}}})
        transactions = [hit['_source'] for hit in res['hits']['hits']]

        transaction = {
            'id': len(transactions) + 1,
            'date': request.form['date'],
            'amount': float(request.form['amount'])
        }
        
        # Index the transaction in Elasticsearch
        es.index(index=INDEX_NAME, body=transaction)

        #transactions.append(transaction)

        return redirect(url_for('get_transactions'))
    
    return render_template('form.html')


@app.route("/edit/<transaction_id>", methods=["GET", "POST"])
def edit_transaction(transaction_id):
    if request.method == 'POST':
        date = request.form['date']
        amount = float(request.form['amount'])

        # Search for the document with the given transaction_id in _source['id']
        res = es.search(index=INDEX_NAME, body={
            "query": {
                "term": {"id": int(transaction_id)}
            }
        })

        # Check if any results were found
        if res["hits"]["total"]["value"] > 0:
            # Extract the actual Elasticsearch _id
            es_id = res["hits"]["hits"][0]["_id"]

            # Update the transaction in Elasticsearch
            es.update(index=INDEX_NAME, id=es_id, body={"doc": {"date": date, "amount": amount}})
            return redirect(url_for('get_transactions'))
        else:
            return "Transaction not found", 404

    # If GET request, retrieve transaction details to edit
    try:
        # Again, search by custom `id` in _source to fetch transaction for editing
        res = es.search(index=INDEX_NAME, body={
            "query": {
                "term": {"id": int(transaction_id)}
            }
        })

        # Check if any transaction is found
        if res["hits"]["total"]["value"] > 0:
            transaction = res["hits"]["hits"][0]["_source"]
            return render_template("edit.html", transaction=transaction)
        else:
            return "Transaction not found", 404
    except NotFoundError:
        return "Transaction not found", 404


# Delete operation ---------------------------------------

@app.route('/delete/<transaction_id>')
def delete_transaction(transaction_id):

    res = es.search(index=INDEX_NAME, body={
        "query": {
            "term": {"id": int(transaction_id)}
        }
    })

    es_id = res["hits"]["hits"][0]["_id"]

    try:
        # Delete the transaction from Elasticsearch
        es.delete(index=INDEX_NAME, id=es_id)
    except NotFoundError:
        return "Transaction not found", 404
    
    return redirect(url_for('get_transactions'))

# Search transactions -----------------------------------

@app.route("/search", methods=["GET", "POST"])
def search_transactions():

    if request.method == "POST":
        min_amount = float(request.form['min_amount'])
        max_amount = float(request.form['max_amount'])

        # Elasticsearch query to filter transactions based on the amount range
        query = {
            "query": {
                "range": {
                    "amount": {
                        "gte": min_amount,
                        "lte": max_amount
                    }
                }
            }
        }
        # Perform the search in Elasticsearch
        res = es.search(index=INDEX_NAME, body=query)

        # Extract transactions from the search results
        filtered_transactions = [hit['_source'] for hit in res['hits']['hits']]

        # Render the results to the template
        return render_template("transactions.html", transactions=filtered_transactions)

    # For GET request, simply render the search form
    return render_template("search.html")


# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
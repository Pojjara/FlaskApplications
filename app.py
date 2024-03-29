from flask import Flask, render_template, redirect, request, session, g
import requests, bs4
import sqlite3
from webscraping import *
from ListOfSites import sites
from priceChecking import *
import time
from apscheduler.schedulers.background import BackgroundScheduler

# Handle any errors that might occur during the scraping process. 
# Handle any errors that might occur during the insertion of the scraped data into the database.
# Handle any errors that might occur during the connection to the database.
# Handle any errors that might occur during the closing of the database connection.
# Handle any errors that might occur during the fetching of data from the database.
# Handle any errors that might occur during the updating of data.
# Handle any errors that might occur during the starting of the scheduler.
# Handle any errors that might occur during the running of the application.
# Use a variable or parameter instead of hardcoding HOW_MANY_ARTICLES 


# Function to update the data
def update_data():

    print("Updating data...")
    getArticlesFromSites(sites)
    global data
    data = fetch_data(sites)
    global prices

    prices = getPrices()

# Create a BackgroundScheduler to update the data every 10 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(update_data, 'interval', minutes=5)

# Create the Flask app
app = Flask(__name__)

# Set the secret key
app.secret_key = 'sadhah2h31h'

#app.use("/static", Flask.static('./static/'));

# Gather the data from the sites
getArticlesFromSites(sites)
data = fetch_data(sites)

# Get data for prices check
global prices
prices = getPrices()


# Index route
@app.route("/",methods=["GET", "POST"])
def index():
    
    # Render the index template and pass the data to it
    comments=get_comments()
    return render_template("index.html", data=data,comments=comments)
    
@app.route("/addComment", methods=["POST"])
def addcomment():

    if not request.form.get("comment"):
            return redirect("/")
    
    comment = request.form.get("comment")
    insert_comment_to_db(comment)

    return redirect("/")
    
@app.route("/pricechecker", methods=['GET', "POST"])
def priceChecker():
    return render_template("pricecheck.html", prices=prices)

@app.route("/addNewAmazonItem", methods=["POST"])
def addNewAmazonItem():
    
    if request.method == 'POST':
        link = request.form.get("link")
        targetprice = int(request.form.get("price"))

        insert_product_to_db(link,targetprice)

        #Nie dziala poprawnie V

        amazonDataNewProduct = get_info_about_new_product(link,targetprice)
        prices.append(amazonDataNewProduct)

        ##Nie dziala poprawnie ^
        print('New Amazon product added!')

        return redirect("/pricechecker")

    
@app.route("/removeitem" , methods=["POST"])
def removeitem():
    
    itemToDelete = str(request.form.get("link"))
    remove_product_from_db(itemToDelete)


# Create a new list to store the dictionaries that don't match the link to delete
    new_prices = []
    global prices
# Iterate through each dictionary in the prices list
    for price in prices:
        # If the link of the current dictionary matches the link to delete, skip it
        if price["link"] == itemToDelete:
            continue
        # Otherwise, add the dictionary to the new list
        new_prices.append(price)

# Replace the original prices list with the new list that doesn't contain the deleted item
    prices = new_prices


    ##Nie dziala poprawnie ^
    print('Item Deleted!')
    return redirect("/pricechecker")

@app.errorhandler(404)
def errorhandling(error):
    return "This page doesn't exist!", 404

# Start the scheduler
if __name__ == '__main__':
    scheduler.start()
    app.run()
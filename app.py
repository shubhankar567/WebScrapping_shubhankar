from flask import Flask, jsonify, request, render_template
from bs4 import BeautifulSoup as bs
import logging
from urllib.request import urlopen
import requests
from flask_cors import CORS, cross_origin
import pymongo
import csv
import json

logging.basicConfig(filename = "scrapper.log", level = logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
@cross_origin()
def home():
    return render_template("index.html")

@app.route("/review", methods = ["POST"])
@cross_origin()
def search():
    if request.method == "POST":
        try:
            item = request.form['content']
            detailsList = []
            jsonList = []

            detailsList.append(["Product", "Customer Name", "Rating", "Rating Header", "Review"])
            mClient = pymongo.MongoClient("mongodb+srv://shubhankar567:Om%24aiRam56@cluster0.vnqrdcq.mongodb.net/?retryWrites=true&w=majority")
            db = mClient['Web_Scrap']
            collect = db["mobileReviews"]

            searchLink = "https://www.flipkart.com/search?q=" + item.replace(" ","+")
            uClient = urlopen(searchLink)
            searchPage = uClient.read()
            uClient.close()
            searchPage = bs(searchPage, "html.parser")
            products = searchPage.findAll("div", {"class": "_1AtVbE col-12-12"})
            productsLink = "https://www.flipkart.com" + products[2].div.div.div.a["href"]
            productData = requests.get(productsLink)
            productData = bs(productData.text, "html.parser")
            comments = productData.find_all("div", {"class": "col _2wzgFH"})
            for comment in comments:
                rating = comment.div.div.text
                header = comment.div.p.text
                customerName = comment.find("div", {"class": "row _3n8db9"}).div.p.text
                review = comment.find("div", {"class": "t-ZTKy"}).div.div.text
                detailsList.append([item, customerName, rating, header, review])
                jsonDict = {"Item": item, "Customer Name": customerName, "Rating": rating, "Rating Header": header, "Review": review}
                jsonList.append(jsonDict)

            with open("Details.csv", 'w') as f:
                writer = csv.writer(f)
                writer.writerows(detailsList)
    
            with open("Details.json", "w") as f:
                json.dump(jsonList, f)
            collect.insert_many(jsonList)
            return render_template("result.html", jsonList = jsonList)
        except Exception as e:
            logging.info(e)
            return "something is wrong"
    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(host = "0.0.0.0")
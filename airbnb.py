from flask import Flask, render_template, flash, request, url_for, redirect

import os
import sys
from flask import Flask, request, session, g, redirect, url_for, abort, render_template,redirect
import jsonify
from pymongo import MongoClient
from flask_wtf import FlaskForm
from wtforms import SelectField
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from PIL import Image
import numpy as np
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests
import bs4

from suggested_price_regression import predict_price

client1 = MongoClient('127.0.0.1',27017)
db1 = client1.airbnb
newyorklistingCollection = db1.NewYork_listing_orig
count=0

app=Flask(__name__)
app.secret_key = 'A0Zr98slkjdf984jnflskj_sdkfjhT'

df_review = pd.read_csv('data/newyork_reviews.csv',encoding = "ISO-8859-1")
df_listing = pd.read_csv('data/newyork_listings.csv',encoding = "ISO-8859-1")

class UserParamsForm(FlaskForm):
	price = SelectField('Data Attributes', choices=[('first','0-50'),('second','50-100'),('third','100-1000')])


def get_choice(price):
	lp = 0
	up = 200
	if(price=="first"):
		lp = 0
		up = 50
	elif(price=="second"):
		lp = 51
		up = 100
	else:
		lp = 101
		up = 1000
	#query = {"#and":[{"price":{"$gte":0}} ,{"price":{"$lte":100}}],{"id":1,"price":1}}
	#datalist = list(newyorklistingCollection.find({"$and":[{"price":{"$gte":lp}} ,{"price":{"$lte":up}}]},{"id":1,"price":1,"latitude":1,"longitude":1,"_id":0}))
	tweet_fields = ['id','price','latitude','longitude']
	result = pd.DataFrame(list(list(newyorklistingCollection.find({"$and":[{"price":{"$gte":lp}} ,{"price":{"$lte":up}}]},{"id":1,"price":1,"latitude":1,"longitude":1,"_id":0}))), columns = tweet_fields)
	#return datalist[0:2]
	list_of_list = get_list_from_dict(result)
	#list_of_tuples = get_listoftuple(list_of_list)
	#return result.iloc[0:2]
	return list_of_list[0:12]

def get_list_from_dict(dt):
	temp=[]
	for row in dt.iterrows():
	    index, data = row
	    temp.append(data.tolist())
	return temp


def create_word_cloud(id_first):
	global df_review
	df = df_review
	df = df.loc[df['listing_id'] == id_first]
	airbnb_mask = np.array(Image.open('static/assets/img/Airbnb_Logo.png'))
	text_string = df.iloc[0]["comments"]
	wordcloud = WordCloud(stopwords=STOPWORDS, mask=airbnb_mask, background_color='white',width=1200,height=1000,max_words=100).generate(text_string)

	plt.imshow(wordcloud)
	plt.axis('off')
	plt.savefig('static/assets/img/word_cloud.png')
	plt.close()
	return 1

def get_sentiment(id_first):
	#df = pd.read_csv('data/newyork_reviews.csv',encoding = "ISO-8859-1")
	global df_review
	df = df_review
	df = df.loc[df['listing_id'] == id_first]
	sid = SentimentIntensityAnalyzer()
	for sentence in df['comments']:
		df['ss'] = sid.polarity_scores(sentence)['compound']
	return df['ss'].mean()

def get_real_price(listing_id):
    url='https://www.airbnb.com/rooms/'+str(listing_id)
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    try:
	    for i in soup.find_all('meta'):
	        text=i.get_text()
	        if "price_formatted" in text:
	            search1=text.split()
	    for item1 in search1:
	        if "price_formatted" in item1: 
	            search2=item1
	    n=search2.find("price_formatted")             
	    raw_price=search2[n+19:n+23]
	    raw_price_list=[]
	    for i in raw_price:
	        if 48<=ord(i)<=57:
	            raw_price_list.append(i) 
	    real_price=''.join(raw_price_list)
    except:
    	real_price = 45#"No current listing on airbnb!"
    return real_price



@app.route('/')
def home():
	return render_template("main.html")
'''
@app.route('/index', methods=['GET','POST'])
def index():
	#global count
	form = UserParamsForm()
	#if form.validate_on_submit():
	if request.method == 'POST':
		price = request.form.get('price')
		data = get_choice(price)
		id_first = data[0][0]
		real_price = get_real_price(id_first)
		create_word_cloud(id_first)
		sentiment_score = get_sentiment(id_first)
		#count = count+1
		return render_template('index_response.html', data = data, score = sentiment_score, real_price = real_price)

	
	return render_template('index.html' , form = form)
'''
@app.route('/index')
def index():
	form = UserParamsForm()
	return render_template('index.html' , form = form)

@app.route('/index_response', methods=['GET','POST'])
def index_response():
	if request.method == 'POST':
		price_t = request.form.get('price')
		data = get_choice(price_t)
		id_first = data[0][0]
		real_price = get_real_price(id_first)
		create_word_cloud(id_first)
		sentiment_score = get_sentiment(id_first)
	#return render_template('index_response_1.html', data = data, score = sentiment_score)

	return render_template('index_response_1.html', data = data, score = sentiment_score, real_price = real_price)



@app.route('/lease/')#methods=['GET','POST'])
def lease():
	return render_template("lease.html") 

@app.route('/lease_analysis/',methods=['GET','POST'])
def lease_analysis():
	if request.method == 'POST':
		x1 = int(request.form.get('accommodates'))
		x2 = request.form.get('property_type')
		x3 = request.form.get('room_type')
		x4 = int(request.form.get('minimum_nights'))
		x5 = request.form.get('cancellation_policy')
		x6 = int(request.form.get('review_scores_cleanliness'))
		x7 = int(request.form.get('review_scores_communication'))
		x8 = int(request.form.get('review_scores_location'))
		x9 = predict_price(accommodates=x1,property_type=x2,room_type=x3,minimum_nights=x4,cancellation_policy = x5,review_scores_cleanliness=x6,review_scores_communication=x7, review_scores_location=x8)
		
		
	return render_template('lease_analysis.html',accommodates=x1,property_type=x2,room_type=x3,minimum_nights=x4,cancellation_policy=x5,review_scores_cleanliness=x6,review_scores_communication=x7,review_scores_location=x8,predict_price=x9)


@app.route('/team/')
def team():
	return render_template("team.html")

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html')


if __name__ == '__main__':
   app.run(debug = True)




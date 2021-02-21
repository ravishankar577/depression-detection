from flask import Flask, request, render_template
import pandas as pd
import pickle
import re
import nltk
from nltk.corpus import stopwords
from requests.structures import CaseInsensitiveDict
import json
import requests
import preprocessor as p



app = Flask(__name__,template_folder='templates')

model = pickle.load(open("model.pkl", "rb"))
contractions = pd.read_json('contractions.json', typ='series')
contractions = contractions.to_dict()

c_re = re.compile('(%s)' % '|'.join(contractions.keys()))

def expandContractions(text, c_re=c_re):
    def replace(match):
        return contractions[match.group(0)]
    return c_re.sub(replace, text)

BAD_SYMBOLS_RE = re.compile('[^0-9a-z _]')

def clean_tweets(tweets):
    cleaned_tweets = []
    for tweet in tweets:
        tweet = str(tweet)
        tweet = tweet.lower()
        tweet = expandContractions(tweet)
        tweet = re.sub(r"http\S+", "", tweet)
        tweet = re.sub(r"www.\S+", "", tweet)
        tweet = BAD_SYMBOLS_RE.sub(' ', tweet)
        tweet = re.sub('\[.*?\]',' ', tweet)
        tweet = p.clean(tweet)
        
        # temp = re.sub("@[A-Za-z0-9_]+","", temp)
        # temp = re.sub("#[A-Za-z0-9_]+","", temp)
        

        #remove punctuation
        tweet = ' '.join(re.sub("([^0-9A-Za-z \t])", " ", tweet).split())

        #stop words
        stop_words = set(stopwords.words('english'))
        word_tokens = nltk.word_tokenize(tweet) 
        filtered_sentence = [w for w in word_tokens if not w in stop_words]
        tweet = ' '.join(filtered_sentence)
        
        cleaned_tweets.append(tweet)
        
    return cleaned_tweets


@app.route('/')
def my_form():
    return render_template('form.html')

@app.route('/', methods=['POST'])
def my_form_post():
    
    #convert to lowercase
    user_id = request.form['User ID']
    
   
    url = "https://api.twitter.com/2/users/" + str(user_id) + "/tweets"
    # url = "https://api.twitter.com/2/users/461686577/tweets"

    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Bearer AAAAAAAAAAAAAAAAAAAAAPaVZQEAAAAAn2tJjw0pKqoYAy2putvO4VLIGOY%3DNohozbEFFAee5VAibEcbF7odrhzdeRVG1dLNs5pWMFCqHOwkUd"


    resp = requests.get(url, headers=headers)

    tweet_data = (json.loads(resp.text)['data'])
    tweetlist = []
    for i in tweet_data:
        tweetlist.append(i['text'])

    cleaned_tweets = clean_tweets(tweetlist)
    print("Cleaned tweets of the user are: ",cleaned_tweets)
    predictions = list(model.predict(cleaned_tweets))

    if sum(predictions) >= 3:
        output = "Depressed"
    else:
        output = "Not Depressed"
    print("===================================================================================================================")
    print("Prediction: ", output)

    # return render_template('form.html', final=output, text1=tweetlist[0],text2=dd['pos'],text5=dd['neg'],text4=compound,text3=dd['neu'])
    try:
        t1 = tweetlist[0]
    except:
        t1 = ""
    try:
        t2 = tweetlist[1]
    except:
        t2 = ""
    try:
        t3 = tweetlist[2]
    except:
        t3 = ""
    try:
        t4 = tweetlist[3]
    except:
        t4 = ""
    try:
        t5 = tweetlist[4]
    except:
        t5 = ""
    try:
        t6 = tweetlist[5]
    except:
        t6 = ""
    try:
        t7 = tweetlist[6]
    except:
        t7 = ""
    try:
        t8 = tweetlist[7]
    except:
        t8 = ""
    try:
        t9 = tweetlist[8]
    except:
        t9 = ""
    try:
        t10 = tweetlist[9]
    except:
        t10 = ""
    return render_template('form.html', final=output, text1=t1, text2=t2, text3=t3, text4=t4,text5=t5, text6=t6,text7=t7, text8=t8,text9=t9, text10=t10)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000, threaded=True)

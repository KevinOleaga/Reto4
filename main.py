import csv
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import snscrape.modules.twitter as sntwitter
from textblob import TextBlob

# VARIABLES DEFAULT
tweets = []
count = 0
senti = 0

# PARAMETROS DE BUSQUEDA
search_query = "(Peter Obi OR Tinubu OR Atiku OR #PeterObiForPresident2023 OR #TinubuForPresident2023 OR #AtikuForPresident2023 OR #BAT2023 OR #Obi2023 OR #Atiku2023 OR #OBIdient OR #Atikulated OR Batified OR PDP OR APC OR LP OR LABOUR PARTY)"
num_tweets = 1000

print("\n ******** EXTRACCION DE TWEETS ******** \n")

# EXTRACCION DE TWEETS
for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f"{search_query} since:2015-01-01 until:2023-01-01").get_items()):
    if i >= num_tweets:
        break
    count = count + 1
    print("Obteniendo tweets: " + str(int((count*100)/num_tweets)) + "%")
    tweets.append(tweet)
    
print("\n ****** ANALISIS DE SENTIMIENTOS ****** \n")

# ANALISIS DE SENTIMIENTOS
for tweet in tweets:
    analysis = TextBlob(tweet.rawContent)
    sentiment = analysis.sentiment.polarity        
    senti = senti + 1
    print("Aplicando analisis de sentimientos: " + str(int((senti*100)/num_tweets)) + "%")
    
    # ALMACENAR EN CSV
    with open('tweets.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Tweet', 'Sentiment','Score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for tweet in tweets:
            analysis = TextBlob(tweet.rawContent)
            sentiment = analysis.sentiment.polarity
            score = sentiment
    
            if sentiment > 0:
                sentiment = "POSITIVO"
            elif sentiment == 0:
                sentiment = "NEUTRAL"
            else:
                sentiment = "NEGATIVO"

            writer.writerow({'Tweet': tweet.rawContent, 'Sentiment': sentiment, 'Score': score})

print("\n ***** GUARDADO DE DATOS EN MYSQL ***** \n")

# ALMACENAR EN LA BD
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  database="Reto4"
)

mycursor = mydb.cursor()

with open('tweets.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        sql = "INSERT INTO tweets (tweet, sentiment, score) VALUES (%s, %s, %s)"
        val = (row['Tweet'], row['Sentiment'], row['Score'])
        mycursor.execute(sql, val)

mydb.commit()

print(" *********** CREANDO GRAFICO ********** \n")

# Leer el archivo CSV en un dataframe de pandas
df = pd.read_csv('tweets.csv')

# Agrupar los sentimientos por tipo
sentimientos = df.groupby('Sentiment')['Tweet'].count()

# Crear un gráfico de barras de los recuentos de sentimientos
sentimientos.plot(kind='barh')

# Agregar título y etiquetas de eje
plt.title('Sentimientos en tweets')
plt.ylabel('Sentimiento')
plt.xlabel('Cantidad')

# Mostrar el gráfico
plt.show()

print(" **************** FIN ***************** \n")

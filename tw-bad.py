import tweepy
import json
import sys
import re
import operator

k = open('KEYS.txt','r')
keys = k.readlines()

# Consumer keys and access tokens, used for OAuth
consumer_key = keys[0][:-1]
consumer_secret = keys[1][:-1]
access_token = keys[2][:-1]
access_token_secret = keys[3]


wordPat = '(?<=\W)(?<!@)\w[\w-]+'
firstPat = '(?<=^)(?<!@)\w[\w-]+'
pat = re.compile(wordPat,flags=re.MULTILINE)
patF = re.compile(firstPat,flags=re.MULTILINE)
 
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
 
api = tweepy.API(auth)

handle = sys.argv[1]
f = open('users/' + handle + '.txt', 'w+', encoding='utf-8')

f.write('@' + handle + '\n\n')

allTweets = []

currTweets = api.user_timeline(screen_name=handle, count=200)

while len(currTweets):
  allTweets.extend(currTweets)
  lastID = allTweets[-1].id-1
  currTweets = api.user_timeline(screen_name=handle, count=200, max_id=lastID)
  print('working... ' + str(len(allTweets)) + ' tweets processed.')


allWords = {}

bw = open('badwords.txt', 'r')
bw_lines = bw.readlines()

badWords = []
for line in bw_lines:
  badWords.append(line[:-1])

invalidWords = ['RT','https','co', 'gt']

newBad = {}

def processWord(word,tweet):
  flag = False
  for i in badWords:
    if word.lower().find(i.lower())!=-1:
      flag = True
  if flag and word not in invalidWords:
    if word in allWords:
      allWords[word] += 1
      if tweet.text not in newBad[word]:
        newBad[word].append(tweet.text)

    else:
      allWords[word] = 1
      newBad[word] = []
      if tweet.text not in newBad[word]:
        newBad[word].append(tweet.text)

for tweet in allTweets:
  if tweet.text.find('RT') == -1:
    currWords = pat.findall(tweet.text)
    first = patF.search(tweet.text)
    if first: 
      processWord(first.group(),tweet)
    for word in currWords:
      processWord(word,tweet)

if len(allWords):
  i=1
  maxW = max(allWords.items(), key=operator.itemgetter(1))[0]
  while allWords[maxW]!=0:
    f.write('#' + str(i) + ': "' + maxW + '", ' + str(allWords[maxW]) + '\n')
    allWords[maxW] = 0
    maxW = max(allWords.items(), key=operator.itemgetter(1))[0]
    i+=1

for i in newBad:
  f.write('\n\n' + i + '...\n')
  for j in newBad[i]:
    f.write('\n//---------------------------------------------------------------------------//\n')
    f.write(j+'\n')

print("DONE. (" + handle + ".txt is in the users folder)")

#!/usr/bin/env python
# coding: utf-8

# In[1]:


import twint
import nest_asyncio
import pandas as pd
import re
import operator
import plotly.graph_objects as go
from networkx.algorithms import bipartite
import networkx as nx
get_ipython().run_line_magic('matplotlib', 'notebook')
import itertools
import matplotlib.pyplot as plt
import ast
nest_asyncio.apply()
from IPython.core.display import display, HTML
display(HTML("<style>.container { width:90% !important; }</style>"))


# In[2]:


#track_list
track_list = ["sustainability",
"sustainable",
"ecofriendly",
"environment",
"zerowaste",
"sustainableliving",
"climatechange",
"environment",
"gogreen",
"nature",
"recycle",
"plasticfree",
"eco",
"reuse",
"green",
"savetheplanet",
"organic",
"vegan",
"ethicalfashion",
"noplastic",
"plastic",
"renewables",
"renewableenergy",
"globalwarming",
"greenliving",
"pollution",
"reduce",
"sustainabilitymatters",
"climateaction",
"conservation",
"savetheearth",
"climate",
"energy",
"reducereuserecycle",
"sdgs",
"waste",
"emissions",
"energy",
"biodiversity",
"environmental",
"globalwarming",
"deforestation",
"plastics",
"greenhouse",
"greenhousegas",
"oceanplastics",
"sustainabilitymatters",
"ocean",
"savetheworld",
"wildlife",
"alternateenergy",
"microplastics",
"circulareconomy",
"ethicalconsumption",
"climatestrike",
"FridaysForFuture",
"CleanTech",
]

languages_list=["en"]



# "EnergyHarvesting",
# "CradletoCradle",
# "C2C",
# "cradle2cradle",
# "sustainablepackaging",
# "packagingwaste",
# "carbonemission",
# "carbonfootprint",
# "recycling",
# "socialentrepreneurship",
# "socialentrepreneur",
# "corporatecitizenship",
# "ecovadis",
# "corporatesocialresponsibility",
# "csr",
# "tellthetruth",
# "ftse4good",
# "climatecrisis",
# "palmoil",
# "footprint",
# "Industrialwaste",
# "consumerwaste",
# "environmentalprotection",
# "greencomputing",
# "greechemistry",
# "earthscience",
# "environmentalscience",
# "conservation",
# "Ecologicaleconomics",
# "Sustainabledevelopment",
# "ecovillage",
# "ecomunicipality",
# "sustainablecity",
# "permaculture",
# "greenbuilding",
# "sustainableagriculture",
# "sustainablearchitecture",
# "greentechnologies",
# "renewableenergy",
# "environmentaldegradation",
# "overconsumption",
# "populationgrowth",
# "carbondioxide",
# "Tippingpoint",
# "climatology",
# "Biogeochemical",
# "nitrogen",
# "phosphorus",
# "acidification",
# "saturation",
# "aragonite",
# "Freshwater",
# "Ozonedepletion",
# "ozone",
# "aerosols",
# "Chemicalpollution",
# "endocrinedisruptors",
# "heavymetals",
# "radioactivity",
# "contamination",
# "habitatdestruction",
# "erosion",
# "salinization",
# "fertilitylosses",
# "Watermanagement",
# "Overhunting",
# "Overfishing",
# "Overpopulation",
# "toxins",
# "Energyshortage",
# "Energyefficiency,",
# "Energyconservation",
# "Organicagriculture",
# "Regenerativeagriculture",
# "reforestation",
# "forestconservation",
# "Steadystate",
# "Sustainabledevelopment",
# "Degrowth",
# "Anticonsumerism"


# In[3]:


#get tweets
#https://github.com/twintproject/twint/wiki/Configuration
tweets = pd.DataFrame()
for track_item in track_list:
    c = twint.Config()
    c.Search = track_item
    c.Lang = 'en'
    c.Pandas =True
    c.Min_retweets=20        
    c.Limit = 50
    c.Since = '2020-06-01 00:00:01' 
    # Run
    twint.run.Search(c)
    tweets = tweets.append(twint.storage.panda.Tweets_df)


# In[4]:


tweets.to_csv('tweets170820-50.csv')
tweets = pd.read_csv('tweets170820-50.csv')


# In[5]:


duplicatelist = set(tweets[tweets.duplicated(['id'])].id)
tweets1 = tweets
tweets = tweets.drop_duplicates(['id'],keep='first')
tweets.set_index('id',inplace = True)
tweets['hashtags'] = tweets['hashtags'].str.replace('#', '')


# In[6]:


for tweetid in tweets.index:
    listofsearches = tweets1[tweets1['id'] == tweetid].search.to_list()
    try:
        tweets.at[tweetid,'hashtags'] = list(set(ast.literal_eval(tweets.at[tweetid,'hashtags']) + listofsearches))
    except:
        tweets.at[tweetid,'hashtags'] = list(set(listofsearches))
    
tweets.reset_index(inplace=True)


# In[7]:


tweets.username = tweets.username.astype(str).str.upper()


# # Top Influencers

# In[9]:


top = tweets[tweets.username.isin(tweets.groupby('username').sum().nretweets.sort_values(ascending = False).head(50).index)]
df = pd.DataFrame()
for i in top.index:
    for hashtag in top.hashtags[i]:
            new_row = {'User':top.username[i], 'hashtag': hashtag, 'weight' : 1, 'retweet':top[top.index == i].nretweets.iloc[0]}
            df = df.append(new_row, ignore_index=True)

df.groupby(['User','hashtag']).sum().reset_index().to_csv('top_influencers170820.csv')


# In[10]:


top = tweets[tweets.username.isin(tweets.groupby('username').sum().nretweets.sort_values(ascending = False).head(50).index)]
B=nx.Graph()
Hashtags = []
for i in top.index:
    for hashtag in top.hashtags[i]:
        if B.has_edge(top.username[i],hashtag):
            B[top.username[i]][hashtag]['weight'] +=1    
            B[top.username[i]][hashtag]['retweet'] += top[top.index == i].nretweets
        else:
            B.add_edge(top.username[i],hashtag,weight = 1,retweet=top[top.index == i].nretweets)
            Hashtags.append(hashtag)
            
plt.figure(figsize=(10,9))
nx.draw_networkx(
    B,
    pos = nx.drawing.layout.bipartite_layout(B, top.username.to_list()))


# In[11]:


X = set(Hashtags)
P=bipartite.weighted_projected_graph(B,X)
Edge = P.edges(data=True)

plt.figure() #which topics are more likely connected?
nx.draw_kamada_kawai(P,with_labels=True,multigraph=True,node_size =90,font_size =9,width=0.1)


# In[12]:


nx.to_pandas_edgelist(P).to_csv('Top_Projected170820.csv')


# # Every one

# In[13]:


B=nx.Graph()
Hashtags = []
for i in range(len(tweets)-1):
    for hashtag in tweets.hashtags[i]:
        if B.has_edge(tweets.username[i],hashtag):
            B[tweets.username[i]][hashtag]['weight'] +=1    
            B[tweets.username[i]][hashtag]['retweet'] += tweets.iloc[i].nretweets
        else:
            B.add_edge(tweets.username[i],hashtag,weight = 1,retweet=tweets.iloc[i].nretweets)
            Hashtags.append(hashtag)


# In[15]:


#Bipartite Graph, left side is Users, right side is Topics (ugly I know :/)
# plt.figure(figsize=(10,9))
# nx.draw_networkx(
#     B,
#     pos = nx.drawing.layout.bipartite_layout(B, tweets.username.to_list()))


# In[16]:


# X = set(Hashtags)
# P=bipartite.weighted_projected_graph(B,X)
# Edge = P.edges(data=True)

# plt.figure() #which topics are more likely connected?
# nx.draw_kamada_kawai(P,with_labels=True,multigraph=True,node_size =90,font_size =10,width=0.1)


# In[ ]:





# In[ ]:





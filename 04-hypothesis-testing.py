
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[23]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[24]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[25]:


def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''

    file = open('university_towns.txt','r')
    s = pd.Series(file.read().split('\n'))
    s = s[:-1]

    df = pd.DataFrame(s)
    df.columns = ['OriginalText']

    df['RegionName']=df['OriginalText'].apply(lambda x: x.split('(')[0].strip() if x.count('[ed')==0 else np.NaN)
    df['State']=df['OriginalText'].apply(lambda x: x.split('[ed')[0].strip() if x.count('[ed')>0 else np.NaN).fillna(method='ffill')

    return df[['RegionName','State']].dropna()

# temp=get_list_of_university_towns()
# temp.groupby('State').count()


# In[26]:


def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    
    gdp = pd.read_excel('gdplev.xls'
                           ,skiprows=8
    #                       ,skipfooter=0
                           ,usecols=[4,5,6]
                           ,header=None
    #                       ,na_values='...'
                           ,names=['Date', 'GDP current', 'GDP chained'])

    gdp = gdp.loc[gdp['Date']>='2000q1',['Date','GDP chained']]
    gdp.index = pd.to_datetime(gdp.Date)
    gdp['Growth']=gdp['GDP chained'].pct_change()

    # recession (state) defined as the first of two consecutive quarters of negative growth
    gdp['F.Growth']=gdp['Growth'].shift(periods=-1)
    gdp['Recession']=0
    gdp.loc[(gdp['Growth']<0)&(gdp['F.Growth']<0),'Recession']=1

    # get start
    gdp['L.Recession']=gdp['Recession'].shift(periods=1)
    gdp['RecessionStart'] = 0
    gdp.loc[(gdp['Recession']==1)&(gdp['L.Recession']==0),'RecessionStart']=1

    out = gdp.loc[gdp['RecessionStart']==1,['Date']].astype(str).values.tolist()[0]
    return out[0]
get_recession_start()


# In[27]:


def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
       
    gdp = pd.read_excel('gdplev.xls'
                           ,skiprows=8
    #                       ,skipfooter=0
                           ,usecols=[4,5,6]
                           ,header=None
    #                       ,na_values='...'
                           ,names=['Date', 'GDP current', 'GDP chained'])

    gdp = gdp.loc[gdp['Date']>='2000q1',['Date','GDP chained']]
    gdp.index = pd.to_datetime(gdp.Date)
    gdp['Growth']=gdp['GDP chained'].pct_change()

    # no recession (state) defined as two consecutive quarters of positive growth
    gdp['L.Growth']=gdp['Growth'].shift(periods=1)
    gdp['NoRecession']=0
    gdp.loc[(gdp['Growth']>=0)&(gdp['L.Growth']>=0),'NoRecession']=1

    # get end
    gdp['RecessionEnd'] = 0
    gdp.loc[(gdp['Date']>=get_recession_start())&(gdp['NoRecession']==1),'RecessionEnd']=1
    out = gdp.loc[gdp['RecessionEnd']==1,['Date']].astype(str).values.tolist()[0]

    return out[0]
get_recession_end()


# In[28]:


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    
    gdp = pd.read_excel('gdplev.xls'
                           ,skiprows=8
    #                       ,skipfooter=0
                           ,usecols=[4,5,6]
                           ,header=None
    #                       ,na_values='...'
                           ,names=['Date', 'GDP current', 'GDP chained'])

    gdp_bottom = gdp.loc[(gdp['Date']>=get_recession_start())&(gdp['Date']<=get_recession_end()),'GDP chained'].min()
    return gdp.loc[gdp['GDP chained']==gdp_bottom,'Date'].astype(str).values.tolist()[0]
get_recession_bottom()


# In[29]:


def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''

    df = pd.read_csv('City_Zhvi_AllHomes.csv')
    df = df.set_index(['State','RegionName'])
    df = df.filter(regex='2\d*-\d*',axis=1)

    df = df.groupby(pd.PeriodIndex(df.columns, freq='Q'), axis=1).mean().rename(columns=lambda c: str(c).lower())

    # # add long state names to housing dataset
    df = df.reset_index()
    # df['Rank'] = df.index
    df2 = pd.DataFrame.from_dict(states,orient='index')
    df2 = df2.reset_index()
    df2 = df2.rename(columns={0:'State_long','index':'State'})

    df = pd.merge(df,df2,how='left',left_on='State',right_on='State')
    df = df.drop(['State'],axis=1).rename(columns={'State_long':'State'}) #.sort_values('Rank')
    df = df.set_index(['State','RegionName'])

    return df


# In[31]:


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 

    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    df = convert_housing_data_to_quarters()

    # -------------------------------------------------------------------------------
    # calculate house price ratio
    # defined as price in pre-recession quarter / price in recession bottom

    # find pre-recession quarter. should be 2008q2
    start = get_recession_start()
    year = start[:4]
    quarter = start[-1]
    if quarter=='1': 
        newyear = str(int(year)-1)
    else:
        newyear = year
    startminusone = newyear+'q'+str(int(quarter)-1)

    # get price ratio
    df['PriceRatio'] = df[startminusone].div(df[get_recession_bottom()])

    df = df[['PriceRatio']].reset_index()

    # -------------------------------------------------------------------------------
    # merge housing prices and university towns on (long) state name
    # this should give 269 uni towns (and the remainder non uni, that's 10461) i'm missing 20 
    df3 = pd.merge(df,get_list_of_university_towns(),how='left',left_on=['State','RegionName'],right_on=['State','RegionName'],indicator=True)

    # create dummy for university town
    df3['Unidummy']=1
    df3.loc[df3['_merge']=='left_only','Unidummy']=0
    df3 = df3.drop(['_merge'],axis=1)

    # df3.loc[df3['Unidummy']==1] # should be 269
    # df3.loc[df3['Unidummy']==0] # should be 10461

    # compute "better"
    better = 'university town'
    if df3.groupby('Unidummy')['PriceRatio'].mean().idxmin()==0:
        better = 'non-university town'

    # run T test
    # null hypothesis is that PriceRatio is the same across the two groups
    # we can reject the null if p<0.01
    df_uni = df3.loc[df3['Unidummy']==1,'PriceRatio']
    df_nonuni = df3.loc[df3['Unidummy']==0,'PriceRatio']
    (t,p)=ttest_ind(df_uni,df_nonuni,nan_policy='omit')

    different = False
    if p<0.01:
        different = True

    return (different,p,better)
run_ttest()


# In[ ]:





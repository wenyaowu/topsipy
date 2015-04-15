# Topsipy - A simple Python wrapper for the Topsy web APIs.

## Description
Tosipy is a client library for the Topsy web APIs.
Topsy is a Twitter partner which resell and analyze data. 
Topsy APIs provide the comprehensive analytics or social data project.

## Dependencies
- [Requests] (https://github.com/kennethreitz/requests) - Topsipy use requests package.

## Simple Example
To get started, install topsipy, create a Topsipy object with your api key and call the method:

    import topsipy
    tp = topsipy.Topsipy(api_key = API_KEY)
  
    result = tp.top_tweet(q='#Avengers',offset=0, limit=5)
  
    for tweet in result['response']['results']['list']:
        print tweet['author']['name']+':'+tweet['tweet']['text']+'\n'
        
## Issue Report
If you find any problems or have any suggestions or such, please post them [here] (https://github.com/wenyaowu/topsipy/issues) 

## Version

- 1.0 - 04/15/2015 - Initial Commit

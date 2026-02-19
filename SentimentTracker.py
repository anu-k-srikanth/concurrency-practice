
# 1. Collect posts - Data ingestion
#    -> Collect based on keywords? Netflix + custom - Yes 
#    -> We cannot crawl the entire internet. Do we want to start with a set of influencers? 
        # -> We can get a list of influencers from an external system that tracks influencers
        # -> We could also do a query for top posts that mention netflix that are getting attention.
        # Both of these inputs probably require the use of an ML model to find and ingest data
#    -> I think it would be an invasion of privacy if we directly used our customer data
# 2. Analyze the sentiment of those posts 
    # -> Is this a score? 
    # -> Binary positive/negative? 
# 3. Combine results and show trends 
    # -> What kinds of trends are we looking for? 
    # -> Long term store results? 
    # -> Average sentiment
    # More complex ML models 


# Task based decomposition
#   - these are three sequential steps that we need to execute
#   - Parallel steps: Collect posts from various sources - 
#     We could have a separate task per influencer to fetch posts, filter by keyword and perform analysis
#     We could have separate task to fetch posts from popular forums like Reddit, X

#     Parallel tasks to get the sentiment for each post
#     Paralle task to store post-sentiment in data store in order to analyze trends over time. Time series database
# Data decomposition
#   - ThreadPool -> per forum to retreive top 
#   - Threadpool -> for various influencers to get their top posts about netflix

# Sentiment Analysis 



class SentimentTracker: 

    def __init__(self):
        pass

    def collect_posts(self):
        pass

    def get_sentiment(self):
        pass
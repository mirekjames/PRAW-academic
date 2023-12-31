import praw
from praw.models import MoreComments
import pandas as pd
import argparse
from datetime import datetime
from dateutil.tz import tzutc, tzlocal

# Get arguments from command line

parser = argparse.ArgumentParser()
parser.add_argument("-su", "--subreddit", help="Please enter the name of the subreddit you want to scrape.", default="all")
parser.add_argument("-sq", "--query", help="Please enter a query to search for in the subreddit.", required=False)
parser.add_argument("-so", "--sort", help="Which algorithm is used to determine the scraped posts. Options are 'top' 'new' 'rising' 'hot'. Default is top. Does not work if searching", default="top")
parser.add_argument("-t", "--timePeriod", help="If you're sorting by top, please enter a time period to search: all, day, hour, month, week, year. default is all", default="all")
parser.add_argument("-c", "--convertTime", help="By default, post/comment time stamps are in UTC. Enter 'true' to convert them to the offset in the --timeZone argument.", default="false")
# parser.add_argument("-tz", "--timeZone", help="Enter an integer for the UTC-offset. Ex. EST is -5. To automatically use your computer's local time, enter 'local'.", default="-5")
parser.add_argument("-n", "--numberOfPosts", help="Please enter a number of posts to scrape. Default is 1000.", default="5")
parser.add_argument("-a", "--awards", help="If you want to get the awards a post / comment has (e.g. Reddit Gold), set --awards to 'true'. Warning: the awards on some subreddits may mess up your data.", default="false")
parser.add_argument("-f", "--filename", help="Please enter a filename for the scraped data.")
args = parser.parse_args()

# Converts scraped data time stamps from UTC to your local timezone
# def utcConvert(utcFloat):
#     utcTime = datetime.fromtimestamp(utcFloat)
#     convertedTime = utcTime
#     if args.timeZone == "local":
#         convertedTime = utcTime.astimezone(tzlocal())
#     else:
#         convertedTime = utcTime.astimezone()
#     return convertedTime

# checkComments and processSub are based on code by jpreed00, and are used to print comments in a .txt file that keeps them in their conversational structure.
# def checkComments(comments):
#     with open("./ScrapedData/" + args.subreddit + "_" + str(args.filename) + "_orderedComments.txt", "a", encoding="utf-8") as txt:
#         for comment in comments:
#             if comment.parent() == comment.submission.id:
#                 txt.write("---\n")

#             if args.awards == "true":
#                 awarded = ""
#                 if comment.all_awardings:
#                     awarded = "TRUE"
#                 else:
#                     awarded = "FALSE"

#             parent = ""
#             indent = ""
#             traceID = ""
#             if comment.parent() == comment.submission.id:
#                 parent = "Top Level"
#             else:
#                 traceComment = comment
#                 while traceID != comment.submission.id:
#                     traceID = traceComment.parent().id
#                     indent = indent + "     "
#                     traceComment = traceComment.parent()
#                 parent = comment.parent().id
#             print(parent)
#             txt.write(indent + "[Comment ID:" + comment.id + " Reply to: " + parent + "]" + str(comment.author) + ": " + comment.body.replace("\n", "") + "\n")         
#             checkComments(comment.replies)

# def processSub(sub):
#     sub.replace_more(limit=0)
#     checkComments(sub)

# Retrieves up to 1000 posts using the provided subreddit, query, numberOfPosts, and timePeriod
def getPosts():
    posts = []
    if(args.query is not None):
        posts = subreddit.search(args.query, limit=int(args.numberOfPosts))
        print("scraping: " + args.query) 
    else:
        if (args.sort == "top"):
            posts = subreddit.top(time_filter=args.timePeriod, limit=int(args.numberOfPosts))
        elif (args.sort == "new"):
            posts = subreddit.new(limit=int(args.numberOfPosts))
        elif (args.sort == "rising"):
            posts = subreddit.rising(limit=int(args.numberOfPosts))
        elif (args.sort == "hot"):
            posts = subreddit.hot(limit=int(args.numberOfPosts))

    posts_dict = {"ID": [], "Subreddit": [], "Date": [], "Title": [], "Post Text": [], "Post Flair": [], 
                    "Author": [], "Author Flair": [], "Post Flair": [], "Score": [], "Upvote Ratio": [],
                    "Total Comments": [], "URL": [], "Linked URL": [], "Locked": [], "NSFW":[], "Awards": [], "Awarded": []
                }
     
    for post in posts:
        # Unique ID of each post
        posts_dict["ID"].append(post.id)
         
        #subreddit
        posts_dict["Subreddit"].append(post.subreddit)

        # Time of Post
        posts_dict["Date"].append(post.created_utc)

        # Title of each post
        posts_dict["Title"].append(post.title)

        # Text inside a post if self-post
        posts_dict["Post Text"].append(post.selftext)

        # Post Flair
        posts_dict["Post Flair"].append(post.link_flair_text)

        # Author of post
        posts_dict["Author"].append(post.author)

        # Author Flair
        posts_dict["Author Flair"].append(post.author_flair_text)

        # The score of a post
        posts_dict["Score"].append(post.score)

        # Ratio of upvotes to downvotes
        posts_dict["Upvote Ratio"].append(post.upvote_ratio)

        # Total number of comments inside the post
        posts_dict["Total Comments"].append(post.num_comments)

        # Permalink
        posts_dict["URL"].append(post.permalink)

        # URL of each post
        posts_dict["Linked URL"].append(post.url)

        # Locked or not
        posts_dict["Locked"].append(post.locked)

        # If marked Not Safe For Work (NSFW)
        posts_dict["NSFW"].append(post.over_18)

        # Awards
        if args.awards == "true":  
            if post.all_awardings:
                awardsString = []
                awardsString = '"' + ''.join(map(str,post.all_awardings)) + '"'
                posts_dict["Awards"].append(awardsString)
                posts_dict["Awarded"].append("TRUE")
            else:
                posts_dict["Awards"].append(post.all_awardings)
                posts_dict["Awarded"].append("FALSE")
        else:
            posts_dict["Awards"].append("")
            posts_dict["Awarded"].append("")

    posts_df = pd.DataFrame(posts_dict)
    posts_df.to_csv("./ScrapedData/" + args.subreddit + "_" + str(args.filename) + "_posts.csv", index=True)


# Retrieves comments from the posts scraped and writes to a .csv file.
def getUnorderedComments():
    posts = []
    if(args.query is not None):
        posts = subreddit.search(args.query, limit=int(args.numberOfPosts))
        print("scraping: " + args.query) 
    else:
        if (args.sort == "top"):
            posts = subreddit.top(time_filter=args.timePeriod, limit=int(args.numberOfPosts))
        elif (args.sort == "new"):
            posts = subreddit.new(limit=int(args.numberOfPosts))
        elif (args.sort == "rising"):
            posts = subreddit.rising(limit=int(args.numberOfPosts))
        elif (args.sort == "hot"):
            posts = subreddit.hot(limit=int(args.numberOfPosts))
    comment_submissions = []    
    comment_ids = []
    comment_dates = []
    comment_authors = []
    comment_authorflairs = []
    comment_bodies = []
    comment_scores = []
    comment_replies = []
    comment_permalinks = []
    comment_postlocked = []
    comment_NSFW = []
    comment_awards = []
    comment_awarded = []
    for submission in posts:
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            comment_submissions.append(comment.submission.id)
            comment_ids.append(comment.id)
            comment_dates.append(comment.created_utc)
            comment_authors.append((str(comment.author)))
            comment_authorflairs.append(comment.author_flair_text)
            comment_bodies.append(comment.body)
            comment_scores.append(comment.score)
            comment_replies.append(len(comment.replies))
            comment_permalinks.append(comment.permalink)
            comment_postlocked.append(submission.locked)
            comment_NSFW.append(submission.over_18)
            if args.awards == "true":  
                if(comment.all_awardings):
                    awardsString = []
                    awardsString = '"' + ''.join(map(str,comment.all_awardings)) + '"'
                    comment_awards.append(awardsString)
                    comment_awarded.append("TRUE")
                else:
                    comment_awards.append(comment.all_awardings)
                    comment_awarded.append("FALSE")
            else:
                comment_awards.append("")
                comment_awarded.append("")

    comment_dict = {"Submission ID": comment_submissions, "Comment ID": comment_ids, "Comment Date": comment_dates, "Author": comment_authors, "AuthorFlair": comment_authorflairs, "Text": comment_bodies, "Score": comment_scores, "Replies": comment_replies, "Link": comment_permalinks, "Post Locked": comment_postlocked, "Post NSFW": comment_NSFW, "Awards": comment_awards,  "Awarded": comment_awarded}       
    comments_df = pd.DataFrame(comment_dict)
    comments_df.to_csv("./ScrapedData/" + args.subreddit + "_" + str(args.filename) + "_comments.csv", index=True)

# By default, the comments are pulled from the API in an order
# that makes it difficult to follow conversations because it pulls 
# all the first-level comments, then all the second-level comments, and so on.
# This function is meant to get print the comments in a more readable format to a .txt file.
# It does not work quite right yet.
# def getOrderedComments():
#     posts = []
#     if(args.query is not None):
#         posts = subreddit.search(args.query, limit=int(args.numberOfPosts))
#     else:
#         if (args.sort == "top"):
#             posts = subreddit.top(time_filter=args.timePeriod, limit=int(args.numberOfPosts))
#         elif (args.sort == "new"):
#             posts = subreddit.new(limit=int(args.numberOfPosts))
#         elif (args.sort == "rising"):
#             posts = subreddit.rising(limit=int(args.numberOfPosts))
#         elif (args.sort == "hot"):
#             posts = subreddit.hot(limit=int(args.numberOfPosts))
#     for submission in posts:
#         awarded = ""
#         if args.awards == "true":  
#             if submission.all_awardings:
#                 awarded = "TRUE"
#             else:
#                 awarded = "FALSE"
#         else:
#             awarded = ""

#         time = str(submission.created_utc).encode("utf-8")
#         # if args.convertTime == "true":
#         #     time = uctConvert(str(time).encode("utf-8")) 

#         with open("./ScrapedData/" + args.subreddit + "_" + str(args.filename) + "_orderedComments.txt", "a") as txt:
#             txt.write("\nPost Data: [" + 'Subreddit: {}, Date: {}, Title: {}, Author: {}, AuthorFlair: {}, Score: {}, ID: {}, Link: {}, Locked: {}, NSFW: {}, Awarded: {}, Comments: {}'.format(str(submission.subreddit).encode("utf-8"),
#                                                                                   time,
#                                                                                   str(submission.title).encode("utf-8"),
#                                                                                   str(submission.author).encode("utf-8"),
#                                                                                   str(submission.author_flair_text).encode("utf-8"),
#                                                                                   str(submission.score).encode("utf-8"),
#                                                                                   str(submission.id).encode("utf-8"),
#                                                                                   str(submission.permalink).encode("utf-8"),
#                                                                                   str(submission.locked).encode("utf-8"),
#                                                                                   str(submission.over_18).encode("utf-8"),
#                                                                                   awarded,
#                                                                                   str(submission.num_comments).encode("utf-8")) + "]" + "\n\n")
        # processSub(submission.comments)

reddit = praw.Reddit("scraper")
subreddit = reddit.subreddit(args.subreddit)

getPosts()
getUnorderedComments()
# getOrderedComments()
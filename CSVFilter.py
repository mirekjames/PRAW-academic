# CSVFilter.py
# Mirek Stolee
# November 2, 2023

# Used to filter out terms from the scraped data.
# Given a .csv file in ./ScrapedData, it filters for the search query
# and generates a new .csv file in ./FilteredData
# the filepath for the scraped data .csv is: "./ScrapedData/" + subreddit + "_" + scrapeQuery + "_" + scrapeType + ".csv"
# The filepath for the new .csv file is exportName = "./FilteredData/" + subreddit + "_" + filename + ".csv"

import pandas as pd
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-su", "--subreddit", help="Please enter the name of the subreddit from the scraped data filename.", default="all")
parser.add_argument("-sq", "--searchQuery", help="Please enter the search query used to scrape.", required=False, default="None")
parser.add_argument("-fq", "--filterQuery", help="Please enter the string you want to filter by. You may also enter the filepath of a .txt file with one search term on each line.")
parser.add_argument("-st", "--scrapeType", help="Please enter the type of dataset you're filtering: posts or comments", default="comments")
parser.add_argument("-c", "--column", help="Please enter the name of the column you want to search for the query in.", required=False, default="Text")
parser.add_argument("-f", "--filename", help="Please enter a filename for the filtered data.")
parser.add_argument("-fo", "--filterOut", help="Please enter the string you want to filter out. You may also enter the filepath of a .txt file with one search term on each line.", default="None")
args = parser.parse_args()

def filterByList(df, queryTXT, filterType):
	queryList = []
	try:
		with open(queryTXT, "r") as f:
			data = f.read()
			queryList = data.split("\n")
			queryList = list(filter(None, queryList))
			print(queryList)
			f.close()
	except:
		print("ERROR: Cannot find "+ filterType + " file.")

	dfList = []
	for term in queryList:
		tempDF = df[df[column].str.lower().str.contains(term, case=False, na=False)]
		dfList.append(tempDF)
	filteredDF = pd.concat(dfList)
	filteredDF = filteredDF.drop_duplicates()
	return filteredDF

# Parse Arguments
subreddit = args.subreddit
scrapeQuery = args.searchQuery
scrapeType = args.scrapeType
column = args.column
filterOut = args.filterOut
filename = "./ScrapedData/" + subreddit + "_" + scrapeQuery + "_" + scrapeType + ".csv"
filterQuery = args.filterQuery
filterQueryName = args.filename
exportName = "./FilteredData/" + subreddit + "_" + filterQueryName + ".csv"

# Filter:
# If using a .txt file, reads from the file. Otherwise, filters using the filterQuery string
df = pd.read_csv(filename)
if ".txt" in filterQuery:
	df = filterByList(df, filterQuery, "query")
else:
	df = df[df[column].str.lower().str.contains(filterQuery, case=False, na=False)]

# Filtering out:
# Creates two datasets - one with the data you want, and one with the data you don't,
# then removes any rows from the first dataset that are also in the second
filterOut_df = ""
if filterOut != "None":
	if ".txt" in filterOut:
		filterOut_df = filterByList(df, filterOut, "filter out")
	else:
		filterOut_df = df[df[column].str.lower().str.contains(filterOut, case=False, na=False)]
	df = df[~df.isin(filterOut_df)]

# Removes duplicate rows and exports to CSV
df.dropna(how="all", inplace=True)
df.to_csv(exportName, index=False)
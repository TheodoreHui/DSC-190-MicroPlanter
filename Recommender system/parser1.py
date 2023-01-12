import requests
from bs4 import BeautifulSoup
import re
import csv
from datetime import datetime

def parse_page(url):
    page = requests.get(url)
    content = page.text
    parsed_content = BeautifulSoup(content, 'html.parser')
    return parsed_content
    
def parse_info(parsed_content):
    calendar = parsed_content.find("div", {"id": "calendar"})
    info = parsed_content.find("div", {"class": "info"})
    sowing = info.find("li", {"class": "sowing"}).text.strip()
    spacing = info.find("li", {"class": "spacing"}).text.strip()
    harvest = info.find("li", {"class": "harvest"}).text.strip()
    companion = info.find("li", {"class": "companion"})
    if companion:
        companion = companion.text.strip()
    avoid = info.find("li", {"class": "avoid"})
    if avoid:
        avoid = avoid.text.strip()
    details = parsed_content.find("div", {"id": "details"}).text.strip()
    
    deg_pattern = "([\d]+)°F.+([\d]+)°F."
    min_soil_temp = int(re.search(deg_pattern, sowing).group(1))
    max_soil_temp = int(re.search(deg_pattern, sowing).group(2))
    
    
    row = dict()
    row["scrape_date"] = datetime.today()
    row["calendar"] = calendar
    row["sowing"] = sowing
    row["spacing"] = spacing
    row["harvest"] = harvest
    row["companion"] = companion
    row["avoid"] = avoid
    row["details"] = details
    return row

def write_to_csv(data, filepath = 'data.csv'):
    """
    Writes to the csv file
    """
    fieldnames = ["scrape_date", "calendar", "sowing", "spacing", "harvest", "companion", "avoid", "details"]
    with open(filepath, mode='a+') as df:
        writer = csv.DictWriter(df, fieldnames = fieldnames, extrasaction='ignore', restval = None)
        writer.writerow(data)
import csv
import os
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from genderize import Genderize


try:
    os.mkdir("Econ_Nobel_Laureates")
    print("Directory created.")
except FileExistsError:
    print('''
          
          ************************
          Directory already exists
          ************************
          
          ''')


def harvest_data():
    url: str = "https://www.nobelprize.org/prizes/lists/all-prizes-in-economic-sciences/"

    fieldnames = ['names', 'link', 'born', 'place_of_birth', 'year', 'affiliation', 'what_for', 'gender', 'country_of_origin', 'country_of_affiliation']

    nobel_prizes_economy: bytes = requests.get(url).content

    soup = BeautifulSoup(nobel_prizes_economy, 'html.parser')

    prizes_by_year: list = soup.find_all('div')

    needed_links: list = []

    for i in prizes_by_year:
        links_in_tag: list = i.find_all('a')
        for item in links_in_tag:
            if "facts" in item.get('href'):
                needed_links.append(item)

    print('''
        
        .----.______
        |           |
        |    ___________
        |   /          /
        |  /          /
        | /          /
        |/__________/
        
        Creating csv and harvesting data
        
        ''')

    with open("Econ_Nobel_Laureates" + '\\' + "data_for_analysis.csv", 'w+', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for _ in needed_links:
            link_to_bio = _.get('href')
            name: str = _.text
            year_received = (re.search(r'\d\d\d\d', str(_.get('href'))))
            year_awarded = year_received.group(0)
            first_name: str = name.split()[1] if name.split()[0] == "A." else name.split()[0]
            gender = Genderize().get([first_name])[0]['gender']
            bio_page = BeautifulSoup(requests.get(link_to_bio).content, 'html.parser')
            bio = bio_page.find_all('p')
            for j in bio:
                if 'Born:' in j.text:
                    birthday = re.search(r'\d\d? \w* \d\d\d\d|\d\d\d\d', j.text).group(0)
                    birthplace = re.search(r'(?<=\d\d\d\d, ).*', j.text).group(0).strip()
                    country_of_origin = birthplace.split()[-1]
                if 'Affiliation' in j.text:
                    institution = re.search(r'(?<=Affiliation at the time of the award:).*', j.text).group(0)
                    country_of_affiliation = institution.split()[-1]
                if 'The Sveriges Riksbank Prize in Economic Sciences in Memory of Alfred Nobel 1974' in j.text:
                    institution = "Affiliation unknown"
                    country_of_affiliation = "Unknown"
                if 'motivation' in j.text:
                    motif = re.search(r'(?<=for).*', j.text).group(0)
                    motif = motif.replace('"', '')
                    motif = motif.replace('.', '')
            writer.writerow({'names': name, 'link': link_to_bio, 'born': birthday, 'place_of_birth': birthplace, 'year': year_awarded,
                             'affiliation': institution, 'what_for': motif, 'gender': gender, 'country_of_origin': country_of_origin,
                             'country_of_affiliation': country_of_affiliation})
        f.close()

    print("Harvesting the data is done. Program will prepare an analysis now.")

    if os.path.isfile("Econ_Nobel_Laureates" + '\\' + "data_for_analysis.csv"):
        raw_data = pd.read_csv("Econ_Nobel_Laureates" + '\\' + "data_for_analysis.csv")
        clean_data = raw_data.drop_duplicates()
        clean_data.to_csv("Econ_Nobel_Laureates" + '\\' + "data_for_analysis.csv")
        df = pd.read_csv("Econ_Nobel_Laureates" + "\\" + "data_for_analysis.csv")  # df = DataFrame; an object specific for pandas library
        motherland = df["country_of_origin"].value_counts()  # There were to many repetitions of that piece of code, so defining a variable makes more sense.
        aff_country = df["country_of_affiliation"].value_counts()  # There were to many repetitions of that piece of code, so defining a variable makes more sense.

        try:
            print('''
        Women constitute {}% of Nobel Prize Laureates in Economics.
            '''.format(df["gender"].value_counts()["female"]/len(df["gender"])))
            print('''
        Most Nobel Laureates in Economics ({} out of {}) were born in {}.
            '''.format(motherland[0], len(df["country_of_origin"]), 'the USA' if motherland.keys()[0] == 'USA'
                       else motherland.keys()[0]))
            print('''
        Most Nobel Laureates in Economics ({} out of {}) were employed by an institution in {}.
            '''.format(aff_country[0], len(df["country_of_affiliation"]), 'the USA' if aff_country.keys()[0] == 'USA'
                       else aff_country.keys()[0]))
            exit(0)

        except Exception:
            print("Something went wrong: ", Exception)


if __name__ == "__main__":
    harvest_data()

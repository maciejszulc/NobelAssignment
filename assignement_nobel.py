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


def analyze_data():
    if os.path.isfile("Econ_Nobel_Laureates" + '\\' + "data_for_analysis.csv"):
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


def harvest_data():
    url: str = "https://www.nobelprize.org/prizes/lists/all-prizes-in-economic-sciences/"

    extracted_links: list = []
    names: list = []
    year: list = []
    born: list = []
    place_of_birth: list = []
    affiliation: list = []
    motivation: list = []
    data_needed: dict = {}

    nobel_prizes_economy: bytes = requests.get(url).content

    soup = BeautifulSoup(nobel_prizes_economy, 'html.parser')

    prizes_by_year: list = soup.find_all('div', class_='by_year')

    print('''
        
        Gathering links to bio of laureates
        
        ''')

    for i in prizes_by_year:
        links_in_tag: list = i.find_all('a')
        for _ in links_in_tag:
            if "facts" in _.get('href'):
                extracted_links.append(_.get('href'))
                names.append(_.text)
                year_received = (re.search(r'\d\d\d\d', str(_.get('href'))))
                year.append(year_received.group(0))

    for i in extracted_links:
        print('''
        Gathering information on {0}
        '''.format(i))
        soupify = BeautifulSoup(requests.get(i).content, 'html.parser')
        information = soupify.find_all('p')
        for j in information:
            if 'Born:' in j.text:
                birthday = re.search(r'\d\d? \w* \d\d\d\d|\d\d\d\d', j.text)
                born.append(birthday.group(0))
                birthplace = re.search(r'(?<=\d\d\d\d, ).*', j.text)
                place_of_birth.append(birthplace.group(0).strip())
            if 'Affiliation' in j.text:
                institution = re.search(r'(?<=Affiliation at the time of the award:).*', j.text)
                institution = institution.group(0)
                affiliation.append(institution.strip())
            if 'The Sveriges Riksbank Prize in Economic Sciences in Memory of Alfred Nobel 1974' in j.text:
                affiliation.append("Affiliation unknown")
            if 'motivation' in j.text:
                motif = re.search(r'(?<=for).*', j.text)
                motif = motif.group(0)
                motif = motif.replace('"', '')
                motif = motif.replace('.', '')
                motivation.append(motif.strip())

    with open("Econ_Nobel_Laureates" + '\\' + "data_for_analysis.csv", 'w+', encoding='utf-8', newline='') as f:
        print('''
        
        .----.______
        |           |
        |    ___________
        |   /          /
        |  /          /
        | /          /
        |/__________/
        
        Creating csv from harvested data
        
        ''')
        # Fieldnames differ from those in the instruction! Proceed with caution.
        fieldnames = ['names', 'link', 'born', 'place_of_birth', 'year', 'affiliation', 'what_for', 'gender', 'country_of_origin', 'country_of_affiliation']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(0, len(names) - 1):
            first_name = names[i].split()[0]
            gender = Genderize().get([first_name])[0]['gender']  # genderize library returns a dictionary as a response, hence we need to access the key.
            country_of_origin = place_of_birth[i].split()[-1]
            country_of_affiliation = affiliation[i].split()[-1]
            data_needed[names[i]] = [names[i], born[i], year[i], affiliation[i], motivation[i], gender, country_of_origin, country_of_affiliation]  # The same information is passed onto a dictionary, as onto .csv - simplifies serialization of the data to .json, if needed.
            writer.writerow({fieldnames[0]: names[i], fieldnames[1]: extracted_links[i], fieldnames[2]: born[i], fieldnames[3]: place_of_birth[i],
                             fieldnames[4]:  year[i], fieldnames[5]:  affiliation[i], fieldnames[6]: motivation[i], fieldnames[7]: gender,
                             fieldnames[8]: country_of_origin, fieldnames[9]: country_of_affiliation})
        f.close()

    print("Harvesting the data is done. Program will exit now.")
    exit(0)


def main():
    while True:
        task_to_perform = input('''
    
    What do you want to do: [h]arvest data or [a]nalyze it?
    
    If you want to exit, press 'e'.
    
    Your input: ''')
        if task_to_perform == 'h':
            harvest_data()
        if task_to_perform == 'a':
            analyze_data()
        if task_to_perform == 'e':
            exit(0)
        else:
            print("Unknown command.")
            continue


if __name__ == "__main__":
    main()

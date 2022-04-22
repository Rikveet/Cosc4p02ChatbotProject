import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import re
import unidecode

from scraping.modules.teams import scrape_team

class TeamScraper:

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def scrape(self):
        url = 'https://cg2019.gems.pro/Result/ShowTeam_List.aspx?SetLanguage=en-CA'
        documents = {}

        DRIVER_PATH = "C:\webdriver\chromedriver.exe"
        driver = webdriver.Chrome(executable_path=DRIVER_PATH)

        driver.get(url)
        delay = 3

        try:
            #driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtName").send_keys("g")

            btnFind = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_btnFind').click()

            awaitElement = WebDriverWait(driver, delay).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'LM_ResultFlagContainer')))
            print("Ready!")

            tblTeams = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_tblTeam")
            tblElements = tblTeams.find_elements(By.CLASS_NAME, "DataCell")
            teamGUIDList = []
            for element in tblElements:
                try:
                    URL = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    GUIDDirty = URL.split("Team_GUID=")
                    GUIDClean = GUIDDirty[1].split("&")
                    teamGUIDList.append(GUIDClean[0])
                except:
                    continue

        except NoSuchElementException:
            print("Element not on this athletes page.")

        txtEvent = []
        txtTeamName = []
        txtContingent = []
        txtFinalPosition = []
        teamMembers = []
        teamMatches = []
        txtURL = []

        main_events = []
        keys = []
        #https://cg2017.gems.pro/Result/ShowTeam.aspx?Team_GUID=38d31c3f-576f-4083-bb9f-0301e73b30e0&SetLanguage=en-CA
        teamGUIDList = list(dict.fromkeys(teamGUIDList))
        teamList = []
        for team in teamGUIDList:
            teamDict = scrape_team(team, driver)

            teamEvent = teamDict.get('Team Event')
            txtEvent.append(teamEvent)

            teamContingent = teamDict.get('Team Contingent')
            txtContingent.append(teamContingent)

            teamName = teamDict.get('Team Name')
            txtTeamName.append(teamName)

            teamFinalPosition = teamDict.get('Team Final Position')
            txtFinalPosition.append(teamFinalPosition)

            varTeamMembers = teamDict.get('Team Members')
            teamMembers.append(unidecode.unidecode(varTeamMembers))

            varTeamMatches = teamDict.get('Team Competitions')
            teamMatches.append(varTeamMatches)

            url = "https://cg2017.gems.pro/Result/ShowTeam.aspx?Team_GUID=" + team + "&SetLanguage=en-CA"
            txtURL.append(url)

            teamList.append([teamName, teamEvent, teamContingent, unidecode.unidecode(varTeamMembers), varTeamMatches, teamFinalPosition, url])

        try:
            newDict = {
                'Team Name': txtTeamName,
                'Team Members': teamMembers,
                'Team Competitions': teamMatches,
                'Team Event': txtEvent,
                "Team Contingent": txtContingent,
                "Team Final Position": txtFinalPosition
            }

            table_csv = pd.DataFrame(newDict,
                                    columns=['Team Name', 'Team Members', 'Team Competitions', 'Team Event', "Team Contingent",
                                            "Team Final Position"])
            table_csv.to_csv("teams.csv", index=[0, 1, 2, 3, 4, 5])
            print(table_csv)
            print("Done.")
        except:
            print("Didn't write CSV.")
        print(documents)
        #return documents

        #key = teamName + " " + teamEvent
        #key = key.replace(" ", "_")
        #key = key.replace("/", "_")
        #key = key.replace("-", "_")
        #print("key " + key)
        key = "team_info"
        #main_events.append(key)

        documents[key] = {
            "url": "https://cg2017.gems.pro/Result/ShowTeam.aspx",
            "title": key.replace("_", " ").capitalize(),
            "section_title":     "Team Name, Team Event, Team Province, Team Members, Team Matches, Team Final Position, Team URL",
            "columns":          ["Team Name", "Team Event", "Team Province", "Team Members", "Team Matches", "Team Final Position", "Team URL"],
            "values": teamList
        }

        return documents

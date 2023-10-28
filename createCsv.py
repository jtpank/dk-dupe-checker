from __future__ import print_function
import csv
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#creates csv. This also loads salaries into the sheets.
# Need to make a flag that saves these as csv files
class SalaryLoader:
    # Class attributes (shared by all instances)
    salary_loader_class_attribute = "example shared by all instances (static)"

    def __init__(self, filename):
        self.csv_filename = filename
        self.class_name = "csv_load_salaries"
    def parse_csv(self, cptDict, playerDict, teamDict):
        # Open the CSV file for reading
        with open(self.csv_filename, 'r') as file:
            # Create a CSV reader
            csv_reader = csv.reader(file)
            header = next(csv_reader)
            #row example
            # playerName = row[9]
            # playerId = row[10]
            # playerRosterPos = row[11]
            # playerSalary = row[12]
            # starting at the 6th row
            #['', '', '', '', '', '', '', 'Position', 'Name + ID', 'Name', 'ID', 'Roster Position', 'Salary', 'Game Info', 'TeamAbbrev', 'AvgPointsPerGame']
            #['', '', '', '', '', '', '', 'C', 'Domantas Sabonis (30626000)', 'Domantas Sabonis', '30626000', 'CPT', '17100', 'GSW@SAC 10/27/2023 10:00PM ET', 'SAC', '51']
            
            #store into corresponding dicts
            doOnce = True
            for rowIdx, row in enumerate(csv_reader):
                if rowIdx > 6 and (len(row) == 16):
                    playerName = row[9]
                    playerId = row[10]
                    playerRosterPos = row[11]
                    playerSalary = row[12]
                    teamAbbrev = row[14]
                    playerObj = {
                        'id': playerId,
                        'salary': playerSalary,
                        'team': teamAbbrev,
                    }
                    if doOnce:
                        teamDict['away'] = row[13].split("@")[0]
                        teamDict['home'] = row[13].split("@")[1].split(' ')[0]
                        doOnce = False
                    # print(f"{playerName}, {playerId}, {playerRosterPos}, {playerSalary}")
                    if playerRosterPos == 'CPT':
                        cptDict[playerName] = playerObj
                    elif playerRosterPos == 'UTIL':
                        playerDict[playerName] = playerObj
                    else:
                        pass
        # Print the header
        print(header)
    def write_line_to_csv(self, lines):
        # Open the CSV file for appending
        with open(self.csv_filename, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            for line in lines:
                # Write the new_data to the CSV file
                csv_writer.writerow(line)

    def parse_into_teams(self, playerDict, homeTeamUtilDict, awayTeamUtilDict, teamDict):
        for key in playerDict.keys():
            if playerDict[key]['team'] == teamDict['home']:
                homeTeamUtilDict[key] = playerDict[key]
            elif playerDict[key]['team'] == teamDict['away']:
                awayTeamUtilDict[key] = playerDict[key]
            else:
                pass

    def update_values(self, spreadsheet_id, range_name, value_input_option,
                    _values):
        """
        Creates the batch_update the user has access to.
        Load pre-authorized user credentials from the environment.
        TODO(developer) - See https://developers.google.com/identity
        for guides on implementing OAuth2 for the application.
            """
        creds = None
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        # pylint: disable=maybe-no-member
        try:

            service = build('sheets', 'v4', credentials=creds)
            body = {
                'values': _values
            }
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, range=range_name,
                valueInputOption=value_input_option, body=body).execute()
            print(f"{result.get('updatedCells')} cells updated.")
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error

    def load_player_salary_cells(self, teamUtilDict, spreadsheet_id, range_name):
        values_array = []
        for idx, key in enumerate(teamUtilDict.keys()):
            #key is player
            # only 15 players to load
            if idx < 15:
                vals = []
                vals.append(key)
                vals.append(teamUtilDict[key]['salary'])
                values_array.append(vals)
        SAMPLE_SPREADSHEET_ID = spreadsheet_id
        RANGE_NAME = range_name
        self.update_values(SAMPLE_SPREADSHEET_ID,
                    RANGE_NAME, "USER_ENTERED",
                    values_array)

class DupeChecker:
    # Class attributes (shared by all instances)
    dupe_checker_class_attribute = "example shared by all instances (static)"

    def __init__(self):
        self.class_name = "dupe_checker_class"

    def filterRowsFromSheet(self,input):
        output = []
        for idx, row in enumerate(input):
            #skip over rows: [6,7,8,15,16,17,24,25,26]
            skipRows = set([6, 7, 8, 15, 16, 17, 24, 25, 26])
            if idx not in skipRows:
                output.append(row)
        return output

    def generateLineupArray(self, sheet, baseRangeName, captainSet):
        lineupArray = []
        cell_ranges = ["B22:B27", "D22:D27", "F22:F27", "H22:H27", "J22:J27",
                        "B31:B36", "D31:D36", "F31:F36", "H31:H36", "J31:J36",
                        "B40:B45", "D40:D45", "F40:F45", "H40:H45", "J40:J45",
                        "B49:B54", "D49:D54", "F49:F54", "H49:H54", "J49:J54" ]
        cell_ranges_new = [
                        [22,27],
                        [31,36],
                        [40,45],
                        [49,54]
                        ]
        #these are the rows
        cell_ranges_map = [
                        [0,5],
                        [9,14],
                        [18,23],
                        [27,32],
        ]
        baseCellRange = "B22:J54"
        # # Define the row and column indices for your sub-range (e.g., rows 2 to 5, columns A to B)
        # start_row = 2
        # end_row = 5
        # start_col = 0  # Assuming column A is the first column (index 0)
        # end_col = 1  # Assuming column B is the second column (index 1)

        # # Extract the sub-range from cell_values
        #  sub_range_data = [row[start_col:end_col + 1] for row in cell_values[start_row - 1:end_row]]
        inputRangeName = baseRangeName + '!' + baseCellRange
        print(f"inputRangeName: {inputRangeName}")
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=inputRangeName).execute()
        values = result.get('values', [])

        columnLetters = ['B','D','F','H','J']
        #col is 0, 2,4,6,8
        # row is 0,5
        # for idx, row in enumerate(values):
        #   print(f"idx: {idx}, row: {row}")
        # print(values)
        lineups = []
        for cellIdx, cell_map in enumerate(cell_ranges_map):
            start_row = cell_map[0]
            end_row = cell_map[1]
            for col in range(5):
                lineup = []
                for row in range(start_row, end_row+1):
                    # print(f"values: {values[row]}, {start_row} : {end_row}, len: {len(values[row])}, row: {row}, col: {col}")
                    # if values[row]:
                    #   if len(values[row]) > col*2:
                    #     print(f"values: {values[row]}, len: {len(values[row])}, row: {row}, col: {col}")
                        #bug when less than 20 lineups
                    lineup.append(values[row][col*2])
                lineups.append(lineup)

        lineupArray = []
        for idx, lineup in enumerate(lineups):
            lineupObj = {
            "sheet": baseRangeName,
            "cell_range": cell_ranges[idx],
            "id": -1,
            "captain": "",
            "lineup": set()
            }
            #zero indexed
            lineupObj["id"] = idx
            # lineupObj["lineup"] = sorted(lineup[0:4])
            for i in range(5):
                lineupObj["lineup"].add(lineup[i])
                captainSet.add(lineup[5])
                lineupObj["captain"] = lineup[5]
                lineupArray.append(lineupObj)
        return lineupArray, captainSet
            
    def findDuplicateLineupsFromSetArray(self, set_array):
        # Create a dictionary to store the counts of frozensets
        set_counts = {}
        # Create a dictionary to store the indexes of the duplicates
        duplicate_indexes = {}
        # Iterate over the array of sets

        for index, s in enumerate(set_array):
            # Convert the set to a frozenset (to make it hashable)
            frozen_s = frozenset(s)
            
            # Update the counts in the dictionary
            set_counts[frozen_s] = set_counts.get(frozen_s, 0) + 1
            
            # Update the duplicate indexes dictionary
            if frozen_s in set_counts:
                if frozen_s not in duplicate_indexes:
                    duplicate_indexes[frozen_s] = [index]
                else:
                    duplicate_indexes[frozen_s].append(index)

        # Output the duplicate sets and their indexes
        duplicateList = []
        for frozen_s, count in set_counts.items():
            if count > 1:
                indexes = duplicate_indexes[frozen_s]
                duplicateObj = {
                    "lineup": frozen_s,
                    "indexes": indexes
                }
                duplicateList.append(duplicateObj)
            print("Duplicate:", frozen_s, "indexes: ", indexes)
        return duplicateList

    def splitAllLineupObjectsIntoSubLineups(self, allLineups, cpt):
        lineupSet = []
        for lineup in allLineups:
            if lineup["captain"] == cpt:
                lineupSet.append(lineup)
        return lineupSet

    def buildSetArray(self, lineupsArray):
        setArray = []
        for lineup in lineupsArray:
            setArray.append(lineup["lineup"])
        return setArray

def main():
    filename = "/Users/justinpank/Desktop/dk-current.csv"
    SAMPLE_SPREADSHEET_ID = '1ttIu8dOBNu2n0_4Y8VkuH0hS-u1QI0XTfxKkwvGOaQc'
    HOME_RANGE_NAME = 'JUSTIN GSW AT SAC_102723!B2:C17'
    AWAY_RANGE_NAME = 'JUSTIN GSW AT SAC_102723!F2:G17'
    salaryLoader = SalaryLoader(filename)
    cptDict = {}
    playerDict = {}
    teamDict = {}
    homeTeamUtilDict = {}
    awayTeamUtilDict = {}
    home_values_array = []
    salaryLoader.parse_csv(cptDict, playerDict, teamDict)
    #now we have homeTeam and awayTeam
    salaryLoader.parse_into_teams(playerDict, homeTeamUtilDict, awayTeamUtilDict, teamDict)
    #These functions load the dict 
    # into the player and salayr cells, 
    # 15 players max
    # make a flag to set these or not
    #load home team
    salaryLoader.load_player_salary_cells(homeTeamUtilDict, SAMPLE_SPREADSHEET_ID, HOME_RANGE_NAME)
    salaryLoader.load_player_salary_cells(awayTeamUtilDict, SAMPLE_SPREADSHEET_ID, AWAY_RANGE_NAME)

    dupeChecker = DupeChecker()
    allLineupObjects = []
    captainSet = set()
    captains = {}
    contestantLineupArrayDictionaries = {}
    #This creates a long array of ALL the lineups: allLineupObjects
    # also groups the contestant's lineups in: contestantLineupArrayDictionaries
    for baseRangeName in BASE_RANGE_NAME:
        lineupArray, captains = generateLineupArray(sheet, baseRangeName, captainSet)
        contestantLineupArrayDictionaries[baseRangeName] = lineupArray
        for lineupObj in lineupArray:
            allLineupObjects.append(lineupObj)
    # here we want to load all the lineups (per sheet)
    
    
    
    
    # into uploadable csvs
    # print(homeTeamUtilDict)
    # print(awayTeamUtilDict)
    # print(len(awayTeamUtilDict))
    # print(len(homeTeamUtilDict))

    # lines = [
    #     [30626000,30625968,30625993,30625978,30625977,30625983]
    # ]
    # write_line_to_csv(filename, lines)



if __name__ == "__main__":
    main()
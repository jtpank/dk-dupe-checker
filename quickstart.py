from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1ttIu8dOBNu2n0_4Y8VkuH0hS-u1QI0XTfxKkwvGOaQc'
BASE_RANGE_NAME = ['JUSTIN GSW AT SAC_102723','ETHAN GSW AT SAC_102723', 'VIK GSW AT SAC_102723'] #VIK PHX AT LAL_102623'


def filterRowsFromSheet(input):
  output = []
  for idx, row in enumerate(input):
    #skip over rows: [6,7,8,15,16,17,24,25,26]
    skipRows = set([6, 7, 8, 15, 16, 17, 24, 25, 26])
    if idx not in skipRows:
      output.append(row)
  return output

def generateLineupArray(sheet, baseRangeName, captainSet):
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
    
def findDuplicateLineupsFromSetArray(set_array):
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

def splitAllLineupObjectsIntoSubLineups(allLineups, cpt):
  lineupSet = []
  for lineup in allLineups:
    if lineup["captain"] == cpt:
      lineupSet.append(lineup)
  return lineupSet

def buildSetArray(lineupsArray):
  setArray = []
  for lineup in lineupsArray:
    setArray.append(lineup["lineup"])
  return setArray

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
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

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()

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
        
        #TODO: 
        # iterate over each key in playerLineupArrayDictionaries
        for contestant in contestantLineupArrayDictionaries.keys():
          for lineup in contestantLineupArrayDictionaries[contestant]:
            line = create_csv_line_entry()
            lines.append(line)
          add_lines_to_csv_and_save(filename, lines, contestant)
            # lines.append(line)

        # for cpt in captainSet:
        #   lineupSetForOneCaptain = splitAllLineupObjectsIntoSubLineups(allLineupObjects,cpt)
        #   print(f"cpt: {cpt}")
        #   setArray = buildSetArray(lineupSetForOneCaptain)
        #   duplicateListForCaptain = findDuplicateLineupsFromSetArray(setArray)
        #   for dupeLineup in duplicateListForCaptain:
        #     print("\nDUPE SET: ")
        #     for idx in dupeLineup["indexes"]:
        #       sheet_found = lineupSetForOneCaptain[idx]["sheet"]
        #       cell_range_found = lineupSetForOneCaptain[idx]["cell_range"]
        #       print(f"dupe at sheet: {sheet_found}, cellRange: {cell_range_found}")
        #     print("END DUPE SET\n")


    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()
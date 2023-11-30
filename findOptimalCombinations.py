import csv
# knapsack problem with more constraints
def optimalLineupCaptainMode(playerCosts, remainingSalary, fantasyPointsValue, n, playerIds, currentRoster):
    if n == 0 or remainingSalary == 0 or len(currentRoster) == 5:
        return 0, []

    if playerCosts[n-1] > remainingSalary:
        return optimalLineupCaptainMode(playerCosts, remainingSalary, fantasyPointsValue, n-1, playerIds, currentRoster)

    exclude_points, exclude_roster = optimalLineupCaptainMode(
        playerCosts, remainingSalary, fantasyPointsValue, n-1, playerIds, currentRoster
    )

    include_points, include_roster = optimalLineupCaptainMode(
        playerCosts, remainingSalary - playerCosts[n-1], fantasyPointsValue, n-1, playerIds, currentRoster + [playerIds[n-1]])

    if include_points + fantasyPointsValue[n-1] > exclude_points:
        include_roster.append(playerIds[n-1])
        return include_points + fantasyPointsValue[n-1], include_roster
    else:
        return exclude_points, exclude_roster



def removeElementFromArrAtIndex(arr, index):
    if 0 <= index < len(arr):
        return arr[:index] + arr[index + 1:]
    else:
        return arr  # Index out of range, return the original array

def main():
    # load from csv file
    # Example usage:
    # fppg = 
    # playerCost = 
    # playerIds = 
    
    for i, player in enumerate(playerIds):
        currentRoster = []
        maxSalary =     50000
        captain = player
        cptPointsAdded = 1.5*fppg[i]
        newSalary = maxSalary - 1.5*playerCost[i]
        playerIdNew = removeElementFromArrAtIndex(playerIds, i)
        playerCostNew = removeElementFromArrAtIndex(playerCost, i)
        fppgNew = removeElementFromArrAtIndex(fppg, i)
        n = len(fppgNew)
        max_points, selected_players = optimalLineupCaptainMode(playerCostNew, newSalary, fppgNew, n, playerIdNew, currentRoster)
        print(f"\nLineup {i}")
        print(f"Captain: {captain}, Lineup \t{sorted(selected_players)}, projected pts: {max_points + cptPointsAdded}")

if __name__=="__main__":
    main()
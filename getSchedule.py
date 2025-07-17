import json
import requests

class GetSchedule:

    @staticmethod
    def getMatchups():
        leagueID = 1190268562919985152
        for i in range(1,15):
            req = requests.get(f'https://api.sleeper.app/v1/league/{leagueID}/matchups/{i}')
            req_data = json.loads(req.text)
            for matchUp in range(1,6):
                opponents = []
                for j in req_data:
                    if j['matchup_id'] == matchUp:
                        opponents.append(j['roster_id'])
                if opponents[0] == 1 or opponents[1] == 1:
                    print(f'Week {i} matchup {matchUp} is {opponents[0]} Vs {opponents[1]}')

            print('_________')


if __name__ == '__main__':
    GetSchedule.getMatchups()
import os
import sys
from datetime import datetime
import requests
import json
import DataBaseHandle
import Scoring
import argparse

league_id = None # OLD - 807659100711260160
roster_and_players = {}
roster_id_and_user_id = {}
user_id_and_display_name = {}
team_and_wins = {}
scheduleAndScores = []


class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        log_file = os.path.join(os.getcwd(), f'ProjectedRecord_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        self.log = open(log_file, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass


def logging_init():
    sys.stdout = Logger()


def projected_record():
    print('Start Projected record calculations')


    # Set up DB
    DataBaseHandle.create_db()
    DataBaseHandle.create_roster_db()
    DataBaseHandle.create_team_wl()

    if league_id is None:
        quit(-1)

    # Get Rosters
    # https://api.sleeper.app/v1/league/<league_id>/rosters
    roster_req = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/rosters')
    roster_req_data = json.loads(roster_req.text)
    for data in roster_req_data:
        roster_and_players.update({data['roster_id']: data['players']})
        roster_id_and_user_id.update({data['roster_id']: data['owner_id']})

    # Get user info
    # https://api.sleeper.app/v1/league/<league_id>/users
    user_req = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/users')
    user_req_data = json.loads(user_req.text)
    for d in roster_id_and_user_id.items():
        display = [user['display_name'] if user['user_id'] == d[1] else None for user in user_req_data]
        user_id_and_display_name.update({d[1]: next(item for item in display if item is not None)})

    # Get week by week schedule

    # Get Data by week
    # https://api.sleeper.app/projections/nfl/2022/1/?season_type=regular&position[]=DEF&position[]=QB&position[]=RB&position[]=TE&position[]=WR&order_by=pts_ppr
    for week in range(1, 15):
        req = requests.get(f'https://api.sleeper.app/projections/nfl/2025/{week}/?season_type=regular&position[]=DEF&position[]=QB&position[]=RB&position[]=TE&position[]=WR&position[]=K&order_by=pts_ppr')
        reqData = json.loads(req.text)

        ## for the player in the roster get the predicted score
        for i in range(1, 11):
            roster_data = []
            for player in roster_and_players[i]:
                # playerFound = next((item for item in player if item["player_id"] == roster_data[1]), None)
                for projection in reqData:
                    if projection.get('player_id') == player:
                        predicted_score = calculate_score(projection["stats"])
                        # sql_string = f'INSERT INTO cr_league_data (playerID, week, roster_id, predicted_score, pos) VALUES ' \
                        #              f'(\'{projection['player']['position']}\', \'{week}\', \'{i}\', \'{predicted_score}\',' \
                        #              f' \'{player}\');'
                        #
                        # DataBaseHandle.update_db(sql_string)
                        roster_data.append([player, predicted_score, projection['player']['position']])
                        break

            calculate_best_roster_score(i, roster_data, week)
        print(f'Finished week {week}')

    matchup()


def calculate_score(stats):
    # Calculate league predicted points
    score = Scoring.Scoring.get_scoring(league_id)
    player_score = []
    for stat in stats.items():
        if stat[0] in score.keys():
            player_score.append(stat[1] * score[stat[0]])
    final_score = round(sum(player_score), 2)
    return final_score


def calculate_best_roster_score(rosterID, roster_data, week):
    # Calculate best roster score by week
    the_qbs = sorted([float(player[1]) if player[2] == 'QB' else 0 for player in roster_data], reverse=True)
    qbs = the_qbs[0] + the_qbs[1]
    the_rbs = sorted([float(player[1]) if player[2] == 'RB' else 0 for player in roster_data], reverse=True)
    rbs = the_rbs[0] + the_rbs[1]
    the_wrs = sorted([float(player[1]) if player[2] == 'WR' else 0 for player in roster_data], reverse=True)
    wrs = the_wrs[0] + the_wrs[1] + the_wrs[2]
    the_tes = sorted([float(player[1]) if player[2] == 'TE' else 0 for player in roster_data], reverse=True)
    tes = the_tes[0]
    the_flexs = sorted([float(player[1]) if player[2] == 'RB' or player[2] == 'WR' or player[2] == 'TE' else 0 for player in roster_data], reverse=True)
    remove_list = [the_rbs[0], the_rbs[1], the_wrs[0], the_wrs[1], the_wrs[2]]
    for item in remove_list:
        the_flexs.remove(item)
    flex = the_flexs[0]
    the_ds = sorted([float(player[1]) if player[2] == 'DEF' else 0 for player in roster_data], reverse=True)
    d = the_ds[0]
    the_ks = sorted([float(player[1]) if player[2] == 'K' else 0 for player in roster_data], reverse=True)
    k = the_ks[0]
    roster_total = round(sum([qbs, rbs, wrs, tes, flex, d, k]), 2)
    print(f'Week {week} Roster {rosterID} completed, SCORE: {roster_total}')
    scheduleAndScores.append([rosterID, week, roster_total])


def matchup():
    # Get Roster matchups by week
    # "https://api.sleeper.app/v1/league/{/matchups/1"
    week = 1
    test = ''
    wl_sql_string = ''

    for week in range(1, 15):
        match_up_req = requests.get(f'https://api.sleeper.app/v1/league/{league_id}/matchups/{week}')
        match_up_req_data = json.loads(match_up_req.text)
        for i in range(1, 6):
            teams = sorted([int(game['roster_id']) if game['matchup_id'] == i else 0 for game in match_up_req_data], reverse=True)
            # team1_data = DataBaseHandle.get_roster_data_by_roster_id(teams[0], week)[0]
            # team1_owner_id = roster_id_and_user_id.get(int(team1_data[0]))
            # team1_display_name = user_id_and_display_name.get(team1_owner_id)
            # team2_data = DataBaseHandle.get_roster_data_by_roster_id(teams[1], week)[0]
            # team2_owner_id = roster_id_and_user_id.get(int(team2_data[0]))
            # team2_display_name = user_id_and_display_name.get(team2_owner_id)

            team1_data = [item for item in scheduleAndScores if len(item) > 1 and item[0] == teams[0] and item[1] == week]
            team1_owner_id = roster_id_and_user_id.get(int(team1_data[0][0]))
            team1_display_name = user_id_and_display_name.get(team1_owner_id)
            team2_data = [item for item in scheduleAndScores if len(item) > 1 and item[0] == teams[1] and item[1] == week]
            team2_owner_id = roster_id_and_user_id.get(int(team2_data[0][0]))
            team2_display_name = user_id_and_display_name.get(team2_owner_id)

            # Get Gameweek score
            if week == 1:
                if team1_data[0][2] > team2_data[0][2]:
                    team_and_wins.update({team1_display_name: 1})
                    team_and_wins.update({team2_display_name: 0})
                else:
                    team_and_wins.update({team2_display_name: 1})
                    team_and_wins.update({team1_display_name: 0})
            else:
                if team1_data[0][2] > team2_data[0][2]:
                    team_and_wins.update({team1_display_name: team_and_wins.get(team1_display_name) + 1})
                else:
                    team_and_wins.update({team2_display_name: team_and_wins.get(team2_display_name) + 1})

    print(f'Predicted record (W/L):')
    for team in team_and_wins.items():
        print(f'{team[0]}: {team[1]}/{14 - team[1]}')


if __name__ == '__main__':
    msg = 'Please pass in a league ID using -L or --League'

    # Initialize parser
    parser = argparse.ArgumentParser(description=msg)
    # Adding optional argument
    parser.add_argument("-L", "--League",required=True, help="Show Output")
    args = parser.parse_args()

    if args.League:
        league_id = args.League

    logging_init()
    projected_record()


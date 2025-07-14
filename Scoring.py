import json
import requests


class Scoring:

    @staticmethod
    def get_scoring(league_id):
        req = requests.get(f'https://api.sleeper.app/v1/league/{league_id}')
        req_data = json.loads(req.text)
        try:
            scoring_settings = req_data['scoring_settings']
        except KeyError as e:
            print(f'Error when getting scoring settings, using default: [{e}]')
            scoring_settings = {
            "pass_2pt": 2,
            "pass_int": -1,
            "fgmiss": -1,
            "rec_yd": 0.1,
            "xpmiss": -1,
            "fgm_30_39": 3,
            "blk_kick": 2,
            "pts_allow_7_13": 4,
            "ff": 1,
            "fgm_20_29": 3,
            "fgm_40_49": 4,
            "pts_allow_1_6": 7,
            "st_fum_rec": 1,
            "def_st_ff": 1,
            "st_ff": 1,
            "pts_allow_28_34": -1,
            "fgm_50p": 5,
            "fum_rec": 2,
            "def_td": 6,
            "fgm_0_19": 3,
            "int": 2,
            "pts_allow_0": 10,
            "pts_allow_21_27": 0,
            "rec_2pt": 2,
            "rec": 1,
            "xpm": 1,
            "st_td": 6,
            "def_st_fum_rec": 1,
            "def_st_td": 6,
            "sack": 1,
            "fum_rec_td": 6,
            "rush_2pt": 2,
            "rec_td": 6,
            "pts_allow_35p": -4,
            "pts_allow_14_20": 1,
            "rush_yd": 0.1,
            "pass_yd": 0.04,
            "pass_td": 4,
            "rush_td": 6,
            "fum_lost": -2,
            "fum": -1,
            "safe": 2
          }

        return scoring_settings

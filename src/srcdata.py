from pandas._libs.missing import NA
import srcomapi
import srcomapi.datatypes as dt
import pandas as pd
import numpy as np
import time


def getting_SRC_games(game_list, nb_games):
    for i in range(nb_games):
        try:
            print(i)
            game_list.loc[i, "SRC_game"] = api.search(
                srcomapi.datatypes.Game, {"name": game_list.loc[i]["game"]}
            )[0]
        except IndexError:
            continue
        except KeyError:
            continue
    game_list.dropna(inplace=True)
    game_list.reset_index(inplace=True, drop=True)
    nb_games = len(game_list)
    return nb_games


# collecting leaderboards for each game
def collecting_leaderboards(lb_per_game, game_list, nb_games):
    for i in range(nb_games):
        lb = {}
        game = game_list.loc[i, "SRC_game"]
        try:
            for category in game.categories:
                if category.name not in lb:
                    lb[category.name] = {}
                if category.miscellaneous:
                    pass
                elif category.type == "per-level":
                    for level in game.levels:
                        try:
                            lb[category.name][level.name] = dt.Leaderboard(
                                api,
                                data=api.get(
                                    "leaderboards/{}/category/{}/{}?embed=variables".format(
                                        game_list.loc[i, "SRC_game"].id,
                                        category.id,
                                        level.id,
                                    )
                                ),
                            )
                        except srcomapi.exceptions.APIRequestException:
                            pass
                        except KeyError:
                            pass
                else:
                    try:
                        lb[category.name] = dt.Leaderboard(
                            api,
                            data=api.get(
                                "leaderboards/{}/category/{}?embed=variables".format(
                                    game_list.loc[i, "SRC_game"].id, category.id
                                )
                            ),
                        )
                    except KeyError:
                        pass
                    except srcomapi.exceptions.APIRequestException:
                        pass
        except AttributeError:
            continue
        except KeyError:
            continue
        lb_per_game.append(lb)


# collecting WR times with its category and first features : name, released year, nb of runs
# return a data frame with all of that
def collectingTimes(lb_per_game):
    a = np.array([])
    for i in range(len(lb_per_game)):
        for j in lb_per_game[i].keys():
            try:
                game_name = lb_per_game[i][j].game.names["international"]
                category_name = j
                try:
                    WR_time = lb_per_game[i][j].runs[0]["run"].times["realtime_t"]
                except IndexError:
                    pass
                except KeyError:
                    pass
                released_year = lb_per_game[i][j].game.released
                a = np.append(
                    a,
                    [
                        game_name,
                        category_name,
                        WR_time,
                        released_year,
                        len(lb_per_game[i][j].runs),
                    ],
                )
            except AttributeError:
                pass
            except KeyError:
                pass
    return pd.DataFrame(
        a.reshape(int(len(a) / 5), 5),
        columns=["game", "category", "time(seconds)", "released_year", "nb_of_runs"],
    )


# collecting extra features for games : platform, genre...
def collectingExtraFeatures(game_list):
    features = ["platforms", "genres", "engines", "developers", "publishers"]
    for feature in features:
        for i in range(len(game_list.index)):
            print(feature)
            print(game_list.loc[i, "game"])
            try:
                game = api.search(
                    srcomapi.datatypes.Game, {"name": game_list.loc[i, "game"]}
                )[0]
            except IndexError:
                continue
            try:
                game_list.loc[i, feature] = game.__getattr__(feature)[0].name
            except IndexError:
                game_list.loc[i, feature] = NA


api = srcomapi.SpeedrunCom()
api.debug = 1

game_list = pd.read_csv("data/gamelist.csv")
nb_games = len(game_list)
lb_per_game = []

try:
    nb_games = getting_SRC_games(game_list, nb_games)
except KeyError:
    time.sleep(5)
    print("Waiting for the site to be more fluid...")
    nb_games = getting_SRC_games(game_list, nb_games)
try:
    collecting_leaderboards(lb_per_game, game_list, nb_games)
except KeyError:
    time.sleep(5)
    print("Waiting for the site to be more fluid...")
    collecting_leaderboards(lb_per_game, game_list, nb_games)
try:
    game_list = collectingTimes(lb_per_game)
except KeyError:
    time.sleep(5)
    print("Waiting for the site to be more fluid...")
    game_list = collectingTimes(lb_per_game)
try:
    collectingExtraFeatures(game_list)
except KeyError:
    time.sleep(5)
    print("Waiting for the site to be more fluid...")
    collectingExtraFeatures(game_list)


game_list.to_csv("data/dataset.csv")

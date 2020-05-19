import os
import random
import datetime
import pickle
import collections
import networkx as nx
from flask import Flask, session, request, jsonify, render_template, redirect

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# Load saved objects
G = nx.read_gpickle("G.pickle")
attributes = pickle.load(open("attributes.pickle", "rb"))
most_popular = pickle.load(open("most_popular.pickle", "rb"))
categories = pickle.load(open( "categories.pickle", "rb" ))

app = Flask(__name__)
app.config['SECRET_KEY'] = "f84f6176aa4cb7fccac55381b1f9005d97a8f6bd"


def add_to_front_of_history(game_id):
    """Adds a game id to the front of the session history list.
    Parameters:
        game_id: int The game id to add to the front of the history
    """
    history = session.get("history", list())
    # Remove the game id from the history if it is already there
    if game_id in history:
        history.remove(game_id)
    history.insert(0, game_id)
    session["history"] = history


def get_css_hash():
    """Get a Random Hash to Add to the CSS."""
    return hash(datetime.datetime.now())


def get_games_by_category(G, category):
    """Gets the list of all games in a category ordered by their likes
    Parameters:
        G: NetworkX Graph
        category: str Name of the category
    Returns:
        list_of_games: list game ids for games in the category
    """
    counts = dict()
    category_node = "category_" + category.lower().replace(" ", "_")
    for n in G.neighbors(category_node):
        game_id = int(n.replace("game_", ""))
        counts[game_id] = int(attributes[game_id]["likes"])

    list_of_games = sort_counts(counts, len(counts.keys()))
    return(list_of_games)


def get_homepage_categories(G, top_recommendations, n_categories = 7, n_games_per_category = 10):
    """Select N Categories to Highlight
    Parameters:
        G: NetworkX Graph
        top_recommendations: list the id's of the top recommendations
        n_categories: int number of categories
        n_games_per_category: int number of games to select in each category
    Returns:
        homepage_categories: dict category name for key and list of game ids for item
    """
    homepage_categories = dict()
    # Ensure the top recommendations aren't shown again
    seen = set(top_recommendations)            

    if len(session["history"]) > 0:
        # Gather the categories from very recent games in the history
        counts = dict()
        for game_id in session["history"][0:1]:
            game_id = int(game_id)
            # Provide novelty: Ensure recent history is not recommended
            seen.add(game_id)
            for category in attributes[game_id]["category"]:
                counts[category] = counts.get(category, 0) + 1
        # Sort the categories
        category_list = sort_counts(counts, len(counts.keys()))
        # Now add in the other categories in random order
        for category in random.sample(categories.keys(), len(categories.keys())):
            if category not in category_list:
                category_list.append(category)
        # Clip the list to be n categories long
        category_list = category_list[0:n_categories]       
    else:
        # Cold start: Just pick a random sample of categories
        category_list = random.sample(categories.keys(), n_categories)

    # Loop through categories and get games
    for category in category_list:
        homepage_categories[category] = list()
        games_by_category = get_games_by_category(G, category)
        add_to_list = True
        for game in games_by_category:
            if game not in seen and add_to_list:
                seen.add(game)
                homepage_categories[category].append(game)
            if len(homepage_categories[category]) == n_games_per_category:
                add_to_list = False

    return(homepage_categories)


def get_recommendations(G, game_id, n_recommendations = 10):
    """Creates recommendations for a specific game
    Parameters:
        G: NetworkX Graph
        game_id: int the id of the game to provide recommendations for
        n_recommendations: int number of recommendations (optional 10 by default)
    Returns:
        recommendations: list game ids recommended for this game
    """
    counts = dict()    
    root_node = "game_" + str(game_id)
    for n in G.neighbors(root_node):
        if n == "popular":
            weight = 1
        elif "category" in n:
            weight = 2
        elif "integrates_with_"  in n:
            weight = 20
        elif "year" in n:
            weight = 1
        elif "user" in n:
            weight = 1
        else:
            weight = 0
        for node in G.neighbors(n):
            node_id = int(node.replace("game_", ""))
            if node != root_node:
                counts[node_id] = counts.get(node_id, 0) + weight

    recommendations = sort_counts(counts, n_recommendations)
    return recommendations


def get_top_recommendations(G, n_recommendations = 10):
    """Creates the top recommendations found on the home page
    Parameters:
        G: NetworkX Graph
        n_recommendations: int number of recommendations (optional 10 by default)
    Returns:
        top_recommendations: list game ids for the home page
    """
    if len(session["history"]) > 0:
        # Factor in session history
        counts = dict()
        skip = set()
        for game_id in session["history"][0:10]:
            skip.add(int(game_id))
        weight = n_recommendations
        for game_id in session["history"][0:n_recommendations]:
            node_label = "game_" + str(game_id)
            for n in G.neighbors(node_label):
                if "user" in n:
                    for node in G.neighbors(n):
                        node_id = int(node.replace("game_", ""))
                        if node_id not in skip:
                            counts[node_id] = counts.get(node_id, 0) + weight
            weight = weight - 1
        top_recommendations = sort_counts(counts, n_recommendations)
    else:
        # Cold start: Serve up the most popular
        top_recommendations = most_popular[0:n_recommendations]

    return top_recommendations


def sort_counts(counts, n_recommendations):
    """Takes a dictionary of game ids and counts and sorts them into a list n_recommendations long
    Parameters:
        counts: dict keys are game ids and values are the counts
        n_recommendations: int number of recommendations
    Returns:
        sorted_recommendations: list game ids sorted from highest count to lowest
    """
    sorted_recommendations = [u[1] for u in sorted(((value, key) for (key,value) in counts.items()), reverse=True)]
    return sorted_recommendations[0:n_recommendations]


@app.route("/")
def home():
    # Start up the user session view history
    session["history"] = session.get("history", list())
    css_hash = get_css_hash()
    top_recommendations = get_top_recommendations(G)
    has_history = (len(session["history"]) > 0)
    homepage_categories_data = get_homepage_categories(G, top_recommendations = top_recommendations)
    homepage_categories = list(homepage_categories_data.keys())
    return render_template("home.html", css_hash = css_hash, top_recommendations = top_recommendations, attributes = attributes, has_history = has_history, homepage_categories_data = homepage_categories_data, homepage_categories = homepage_categories)


@app.route("/details/<game_id>")
def details(game_id):
    add_to_front_of_history(game_id)
    css_hash = get_css_hash()
    game_id = int(game_id)
    game = attributes[game_id]
    recommendations = get_recommendations(G, game_id)
    return render_template("details.html", css_hash=css_hash, game=game, recommendations = recommendations, attributes = attributes)


@app.route("/clear-history")
def clear_history():
    session["history"] = list()
    return redirect("/")


@app.route("/img/<img_file>")
def img(img_file):
    #196 px
    game_id = img_file.split("\\.")[0]
    return str(game_id)

@app.route("/search", methods = ["GET", "POST"])
def search():
    if request.method == "GET":
        search_terms = request.args.get("search")
    else:
        search_terms = request.form["search"]

    search_terms = search_terms.split(" ")

    search_results = dict()
    for game_id, row in attributes.items():
        game_name = row["name"]
        search_in = game_name.lower()
        for search_for in search_terms:
            if search_for.lower() in search_in:
                search_results[game_name] = game_id
    # Sort by name
    search_results = collections.OrderedDict(sorted(search_results.items()))

    return render_template("search.html", search_results = search_results)

if __name__ == '__main__':
    app.run(debug=True)
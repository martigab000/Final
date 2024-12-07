from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
from datetime import datetime
from pytz import timezone
from . import db
from sqlalchemy import text
from .models import RecentSearch, StateCount
import ast
import us
import os


main = Blueprint('main', __name__)

def batch_list(input_list, batch_size):
    """Splits a list into smaller batches of a specified size."""
    for i in range(0, len(input_list), batch_size):
        yield input_list[i:i + batch_size]


def fetch_state_counts(filter=None):
    state_counts = StateCount.query.all()
    if filter:
        if filter == 'renewable':
            return {state_count.state: state_count.renewable for state_count in state_counts}
        elif filter == 'solar':
            return {state_count.state: state_count.solar for state_count in state_counts}
        elif filter == 'wind':
            return {state_count.state: state_count.wind for state_count in state_counts}
        elif filter == 'hydro':
            return {state_count.state: state_count.hydro for state_count in state_counts}
        elif filter == 'nuclear':
            return {state_count.state: state_count.nuclear for state_count in state_counts}
        elif filter == 'coal':
            return {state_count.state: state_count.coal for state_count in state_counts}
        elif filter == 'gas':
            return {state_count.state: state_count.gas for state_count in state_counts}
        elif filter == 'petroleum':
            return {state_count.state: state_count.petroleum for state_count in state_counts}
        else:
            return {state_count.state: state_count.count for state_count in state_counts}
        
    return {state_count.state: state_count.count for state_count in state_counts}


def ensure_state_html_files():
    # Directory where the state HTML files are stored
    states_dir = './app/templates/states'
    
    # Ensure the directory exists
    os.makedirs(states_dir, exist_ok=True)
    states = us.states.STATES
    
    # Iterate through each state in the database
    for state in states:
        state = str(state).lower()
        state = state.replace(" ", "_")
        state_filename = f"{state}.html"
        state_file_path = os.path.join(states_dir, state_filename)
        
        # Check if the file already exists
        if not os.path.exists(state_file_path):
            # Create the HTML file with a basic template
            with open(state_file_path, 'w') as f:
                f.write(f"""{{% extends 'base.html' %}}
{{% block content %}}
    <h1>Welcome to {state}!</h1>
    <p>This is the {state} state page.</p>
    <a href="/">Go back to home</a>
{{% endblock %}}
""")
            print(f"Created: {state_filename}")
        else:
            print(f"Skipped: {state_filename} (already exists)")


# home page
@main.route('/')
def home():
    state_counts = fetch_state_counts("recent")
    # print(state_counts)
    update_recent()
    # ensure_state_html_files() # used to populate the states folder with html templates
    return render_template('map.html', state_counts=state_counts)

@main.route('/filter', methods=['POST'])
def filter_energy():
    data=request.json
    energy_type = data.get('energyType')
    # print(energy_type)
    state_counts = fetch_state_counts(energy_type)
    return jsonify(state_counts)



def delete_all_state_counts():
    try:
        # Delete all entries in the state_count table
        db.session.query(StateCount).delete()
        db.session.commit()
        print("All entries in state_count have been deleted.")
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.session.close()

def delete_all_recent_search():
    try:
        # Delete all entries in the state_count table
        db.session.query(RecentSearch).delete()
        db.session.commit()
        print("All entries in recent_search have been deleted.")
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.session.close()

from sqlalchemy import text

def update_recent():
    states = us.states.STATES
    for state in states:
        state = str(state).lower().replace(" ", "_")
        total_clicks = 0
        state_results = StateCount.query.filter_by(state=state).first()
        if state_results:
            id_list = [int(id_str) for id_str in state_results.list_of_ids.split(',') if id_str.strip()]

            # Drop the temporary table if it exists, then create a new one
            db.session.execute(text('DROP TABLE IF EXISTS temp_ids'))
            db.session.execute(text('CREATE TEMP TABLE temp_ids (id INTEGER)'))
            
            # Insert IDs into the temporary table in batches
            for batch in batch_list(id_list, 250):  # Adjust batch size
                db.session.execute(
                    text('INSERT INTO temp_ids (id) VALUES (:id)'),
                    [{'id': id} for id in batch]  # Pass parameters as a list of dictionaries
                )
            
            # Query clicks using the temporary table
            clicks_list = db.session.execute(
                text('SELECT clicks FROM recent_search WHERE id IN (SELECT id FROM temp_ids)')
            ).fetchall()
            
            # Drop the temporary table after use
            db.session.execute(text('DROP TABLE temp_ids'))
            
            total_clicks = sum(click[0] for click in clicks_list)
            state_results.count = total_clicks
        
        db.session.commit()
    return





# Route to delete all entries in StateCount
@main.route('/delete_all_state_counts')
def delete_state_counts_route():
    delete_all_state_counts()
    return "All state counts have been deleted."

@main.route('/delete_all_recent_search')
def delete_recent_serch_route():
    delete_all_recent_search()
    return "All recent search have been deleted."

@main.route('/temp')
def temp():
    mysearch = current_app.mysearch
    mysearch.inspect_index()
    return "Success"

# builds index for each state
@main.route('/init')
def init():
    mysearch = current_app.mysearch
    states = us.states.STATES
    energy_keywords = ["renewable", "solar", "wind", "hydro", "nuclear", "coal", "gas", "oil", "petroleum"]
    for state in states:
        # print(state)
        state = str(state).lower()
        state = state.replace(" ", "_")
        total_clicks = 0
        renewable = solar = wind = hydro = nuclear = coal = gas = petroleum = 0

        all_results = mysearch.populate_data(state)
        id_list = [item['id'] for item in all_results]
        # print(len(id_list))

        clicks_list = []
        for batch in batch_list(id_list, 250):  # Use a safe batch size
            clicks_list.extend(
                RecentSearch.query.filter(RecentSearch.id.in_(batch)).with_entities(RecentSearch.clicks).all()
            )

        total_clicks = sum([click[0] for click in clicks_list])
        # print(all_results)
        # Count occurrences of energy keywords
        for result in all_results:
            energy_raw = result.get('energy', [])
            energy_list = ast.literal_eval(energy_raw)
            if isinstance(energy_list, list):
                for energy_type in energy_list:
                    # print(energy_type)
                    if energy_type in energy_keywords:
                        if energy_type == "renewable":
                            renewable += 1
                        elif energy_type == "solar":
                            solar += 1
                        elif energy_type == "wind":
                            wind += 1
                        elif energy_type == "hydro":
                            hydro += 1
                        elif energy_type == "nuclear":
                            nuclear += 1
                        elif energy_type == "coal":
                            coal += 1
                        elif energy_type == "gas":
                            gas += 1
                        elif energy_type == "petroleum":
                            petroleum += 1

        state_count = StateCount.query.filter_by(state=state).first()

        if state_count:
            state_count.count += total_clicks
            state_count.renewable += renewable
            state_count.solar += solar
            state_count.wind += wind
            state_count.hydro += hydro
            state_count.nuclear += nuclear
            state_count.coal += coal
            state_count.gas += gas
            state_count.petroleum += petroleum
            existing_ids = set(state_count.list_of_ids.split(','))
            existing_ids.update(id_list)
            state_count.list_of_ids = ','.join(existing_ids)
        else:
            # If it doesn't exist, create a new record
            state_count = StateCount(state=state, count=total_clicks, renewable=renewable, solar=solar, wind=wind, hydro=hydro, nuclear=nuclear, coal=coal, gas=gas, petroleum=petroleum, list_of_ids=','.join(id_list))
            db.session.add(state_count)

    db.session.commit()
    return "Success"

# delete all records
@main.route('/delete')
def delete():
    return "Success"


# search query init redirect 
@main.route('/search', methods=['POST'])
def search():
    query = str(request.form.get('search'))
    return redirect(url_for('main.search_results', query=query, page=1))

# search query init redirect 
@main.route('/advanced_search', methods=['POST'])
def advanced_search():
    # mysearch = current_app.mysearch
    query = str(request.form.get('keywords'))
    state = request.form.getlist('state[]')
    energy = request.form.getlist('energy[]')
    ranking = request.form.get('ranking')
    print(ranking)
    if ranking == None:
        ranking = 'PageRank'
    # temp = mysearch.state(state)
    # temp = mysearch.energy(energy)
    # return temp
    # print(state)
    # print(energy)
    # return f"States: {state}, Energies: {energy}"
    return redirect(url_for('main.search_results', query=query, page=1, is_advanced=True, state=state, energy=energy, ranking=ranking))

# the result of the search query
@main.route('/results')
def search_results():
    mysearch = current_app.mysearch
    RESULTS_PER_PAGE = 10
    query = request.args.get('query')
    page = request.args.get('page', 1, type=int)
    
    # Get the flag to determine if this is an advanced search
    is_advanced = request.args.get('is_advanced', False, type=bool)
    if is_advanced:
        state_filter = request.args.getlist('state')
        energy_filter = request.args.getlist('energy')
        ranking = request.args.get('ranking')
        print(ranking)
        all_results = mysearch.advanced_search(query, state_filter, energy_filter, ranking)
        print(state_filter)
        print(energy_filter)
    else:
        all_results = mysearch.search(query)
    total_results = len(all_results)
    print(total_results)

    sorted_results = sorted(
        all_results,
        key=lambda result: result['score'],
        reverse=True  # Best to worst
    )

    results_with_count = [
        {"id": result['id'], "url": result['title'], "score": result['score']}
        for result in sorted_results
    ]

    start = (page - 1) * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    pagination_results = results_with_count[start:end]
    has_next = end < len(results_with_count)

    return render_template('search_results.html', query=query, results=pagination_results, page=page, has_next=has_next)

# click counter for front end display heat map
@main.route('/track_click', methods=['POST'])
def track_click():
    result = request.form.get('link_id')
    data = ast.literal_eval(result)
    print(data['id'])
    # print(data[1])
    if data:
        current_time = datetime.now(timezone("US/Pacific"))
        # current_date = current_time.strftime('%Y-%m-%d')

        link = RecentSearch.query.get(data['id'])

        if link:
            link.update_click_dates(current_time)
        else:
            new_link = RecentSearch(id=data['id'], url=data['url'], clicks=0, click_dates="")
            db.session.add(new_link)
            db.session.commit()
            new_link.update_click_dates(current_time)

        db.session.commit()
        return redirect(data['url'])
        
    return jsonify({"error": "link not found"}), 404


# redirect after click counter
@main.route('/redirect_to_link/<link_id>')
def redirect_to_link(link_id):
    mysearch = current_app.mysearch
    result = mysearch.single_search(link_id)
    print(result)
    if result:
        return redirect(result['url'])
    return "Link not found", 404

# redirect to state page after click on heat map
@main.route('/state/<state_name>')
def state_page(state_name):
    mysearch = current_app.mysearch
    # pie_data = mysearch.pie_data(state_name)
    # print(pie_data)
    pie_data = [
        {'label': 'renewable', 'value': 0, 'color': '#FF1733'},
        {'label': 'solar', 'value': 0, 'color': '#33FF51'},
        {'label': 'wind', 'value': 0, 'color': '#3357AF'},
        {'label': 'hydro', 'value': 13, 'color': '#FF5713'},
        {'label': 'nuclear', 'value': 0, 'color': '#31FF57'},
        {'label': 'coal', 'value': 25, 'color': '#3354FF'},
        {'label': 'gas', 'value': 0, 'color': '#FF5733'},
        {'label': 'oil', 'value': 0, 'color': '#33FF57'},
        {'label': 'petroleum', 'value': 0, 'color': '#3357FF'}
    ]
    return render_template(f"states/{state_name}.html", pie_data=pie_data)

# get state info from the clicked state(svg)
@main.route('/get_state_info', methods=['POST'])
def get_state_info():
    data = request.get_json()
    # get the state info from the clicked state(svg)
    state_name = str(data.get('state')).lower()
    if (state_name):
        # redirect to the state clicked on.
        return redirect(url_for('main.state_page', state_name=state_name))
    else:
        search_query = data.get('search_query')
        return jsonify({"status": "success", "state_received": state_name, "search_query": search_query})
    
@main.route('/test')
def test():
    return render_template('washington.html')
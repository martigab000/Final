from whoosh.index import create_in, open_dir
from whoosh.scoring import BM25F, TF_IDF
from whoosh.fields import Schema, TEXT, ID, NUMERIC, KEYWORD
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.query import Term, Or, And, Wildcard, NullQuery, Phrase
from whoosh import index
from datetime import timedelta
from .PageRank import Page_Rank
import os
import pickle
import string
import ast

class MyWhooshSearch(object):
    """docstring for MyWhooshSearch"""
    def __init__(self):
        super(MyWhooshSearch, self).__init__()

    def index(self):
        schema = Schema(id=ID(stored=True), title=TEXT(stored=True), description=TEXT(stored=False), state=TEXT(stored=True), energy=TEXT(stored=True), images=TEXT(stored=True), score=NUMERIC(float, stored=True))
        if not os.path.exists("./data/whooshdir"):
            os.mkdir("./data/whooshdir")
            ix = index.create_in("./data/whooshdir", schema)
            writer = ix.writer()

            pr = Page_Rank('./data/5k_crawler_state.pkl', 20)
            scores = {url: pr.ranks[i] for i, url in enumerate(pr.urls)}

            data = self.load_data('./data/5k_crawler_state.pkl')['url_outgoing_links']
            for i, (url, content) in enumerate(data.items()):
                # if(i < 100):
                raw_html = content[1]['text']
                cleant_html = self.clean_text(raw_html)
                state = self.find_states(cleant_html)
                # energy = self.find_energy(cleant_html)
                # state = content[1]['state']
                energy = content[1]['energy']
                images = content[1]['images']
                score = scores.get(url, 0)
                writer.add_document(id=u'{}'.format(i+1), title=u'{}'.format(url), description=u'{}'.format(cleant_html), state=u'{}'.format(state), energy=u'{}'.format(energy), images=u'{}'.format(images), score=u'{}'.format(score))
            writer.commit()
        else:
            ix = index.open_dir("./data/whooshdir")
        self.ix = ix

    def load_data(self, filename):
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        return data
	
    # clean text for acurate indexing
    def clean_text(self, text):
        text = text.strip().lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        return text

    # double check scraped text for state flags
    def find_states(self, text):    
        energy_keywords = ["renewable", "solar", "wind", "hydro", "nuclear", "coal", "gas", "oil", "petroleum"]
        state_keywords = {
            "alabama": ["alabama", "al"],
            "alaska": ["alaska", "ak"],
            "arizona": ["arizona", "az"],
            "arkansas": ["arkansas", "ar"],
            "california": ["california", "ca"],
            "colorado": ["colorado", "co"],
            "connecticut": ["connecticut", "ct"],
            "delaware": ["delaware", "de"],
            "florida": ["florida", "fl"],
            "georgia": ["georgia", "ga"],
            "hawaii": ["hawaii", "hi"],
            "idaho": ["idaho", "id"],
            "illinois": ["illinois", "il"],
            "indiana": ["indiana", "in"],
            "iowa": ["iowa", "ia"],
            "kansas": ["kansas", "ks"],
            "kentucky": ["kentucky", "ky"],
            "louisiana": ["louisiana", "la"],
            "maine": ["maine", "me"],
            "maryland": ["maryland", "md"],
            "massachusetts": ["massachusetts", "ma"],
            "michigan": ["michigan", "mi"],
            "minnesota": ["minnesota", "mn"],
            "mississippi": ["mississippi", "ms"],
            "missouri": ["missouri", "mo"],
            "montana": ["montana", "mt"],
            "nebraska": ["nebraska", "ne"],
            "nevada": ["nevada", "nv"],
            "new_hampshire": ["new hampshire", "nh"],
            "new_jersey": ["new jersey", "nj"],
            "new_mexico": ["new mexico", "nm"],
            "new_york": ["new york", "ny"],
            "north_carolina": ["north carolina", "nc"],
            "north_dakota": ["north dakota", "nd"],
            "ohio": ["ohio", "oh"],
            "oklahoma": ["oklahoma", "ok"],
            "oregon": ["oregon", "or"],
            "pennsylvania": ["pennsylvania", "pa"],
            "rhode island": ["rhode island", "ri"],
            "south_carolina": ["south carolina", "sc"],
            "south_dakota": ["south dakota", "sd"],
            "tennessee": ["tennessee", "tn"],
            "texas": ["texas", "tx"],
            "utah": ["utah", "ut"],
            "vermont": ["vermont", "vt"],
            "virginia": ["virginia", "va"],
            "washington": ["washington", "wa"],
            "west_virginia": ["west virginia", "wv"],
            "wisconsin": ["wisconsin", "wi"],
            "wyoming": ["wyoming", "wy"],
            
            # Add other states as needed
        }

        # Check for state mentions in the text
        found_states = set()
        for state, keywords in state_keywords.items():
            if any(keyword in text.split() for keyword in keywords):
                found_states.add(state)
        if found_states:
            return found_states  # Assign the state if matched
        else:
            return None  # Return None if no state is found
        
    # double check scraped text for energy flags
    def find_energy(self, text):    
        energy_keywords = ["renewable", "solar", "wind", "hydro", "nuclear", "coal", "gas", "oil", "petroleum"]
        # Check for energy-related keywords in the text
        found = set()
        for energy in energy_keywords:
            if energy in text.split():
                found.add(energy)
        if found:
            return found  # Assign list of found energy keywords
        else:
            return None  # Return None if no energy keywords are found

    # Function to search the index
    def search(self, query_str):
        title = list()
        description = list()
        with self.ix.searcher() as searcher:
            # query_parser = MultifieldParser(["title", "description"], schema=self.ix.schema)
            query_parser = QueryParser("description", schema=self.ix.schema)
            query = query_parser.parse(query_str)
            results = searcher.search(query, limit=None)
            for result in results:
                data = {'id': result['id'], 'title': result['title'], 'score': result['score']}
                title.append(data)
        return title
    
    def inspect_index(self):
        with self.ix.searcher() as searcher:
            # Get all the documents from the index and print the unique values of the 'state' and 'energy' fields
            states = set()
            energies = set()

            # Use searcher to iterate through all documents and extract the 'state' and 'energy' fields
            for doc in searcher.all_stored_fields():
                state = doc.get('state', '')
                energy = doc.get('energy', '')
                
                # Add state and energy values to respective sets (to avoid duplicates)
                if state:
                    states.add(state)
                if energy:
                    energies.add(energy)

            # Print out the unique states and energies
            print("Unique States in Index:")
            print(states)
            print("\nUnique Energies in Index:")
            print(energies)

    # debug function
    def state(self, states):
        res = list()
        with self.ix.searcher() as searcher:
            state_queries = [Wildcard("state", f"*{str(state)}*") for state in states]
            state_query = Or(state_queries)
            results = searcher.search(state_query, limit=None)
            for result in results:
                data = {'id': result['id'], 'title': result['title']}
                res.append(data)
        return res
    # debug function
    def energy(self, states):
        res = list()
        with self.ix.searcher() as searcher:
            state_queries = [Wildcard("energy", f"*{str(state)}*") for state in states]
            state_query = Or(state_queries)
            results = searcher.search(state_query, limit=None)
            for result in results:
                data = {'id': result['id'], 'title': result['title']}
                res.append(data)
        print(len(res))
        return res


    def advanced_search(self, query_str, state_filter, energy_filter, ranking, max_results=None):
        response = list()

        if str(ranking) == 'BM-25':
            print("HERE")
            scoring = BM25F()
        elif str(ranking) == 'TF-IDF':
            scoring = TF_IDF()
        else:
            scoring = BM25F()
        
        print(scoring)
        with self.ix.searcher(weighting=scoring) as searcher:
            # query_parser = MultifieldParser(["title", "description"], schema=self.ix.schema)
            query_str_cleaned = self.clean_text(query_str)
            query_parser = QueryParser("description", schema=self.ix.schema)
            query = query_parser.parse(query_str_cleaned)

            filters = []

            if query != NullQuery:
                print(f"Parsed Query: {query}")
                filters.append(query)
                

            if state_filter and state_filter != ['all']:
                state_queries = [Wildcard("state", f"*{str(state)}*") for state in state_filter]
                state_query = Or(state_queries)
                filters.append(state_query)

            if energy_filter and energy_filter != ['all']:
                energy_queries = [Wildcard("energy", f"*{str(energy)}*") for energy in energy_filter]
                energy_query = Or(energy_queries)
                filters.append(energy_query)

            if filters:
                final_query = And(filters)
                print(final_query)
            else:
                final_query = None
            
            if final_query:
                results = searcher.search(final_query, limit=max_results)
                print(len(results))
                for result in results:
                    if ranking == 'Page_Rank':
                        data = {'id': result['id'], 'title': result['title'], 'score': result['score']}
                    else:
                        data = {'id': result['id'], 'title': result['title'], 'score': result.score}
                    response.append(data)
                print(len(response))
            else:
                print("No query")

        return response
    
    def populate_data(self, query_str):
        res = list()
        # query_str = query_str.replace('_', ' ')
        with self.ix.searcher() as searcher:
            phrase_terms = query_str.split()
            phrase_query = Phrase("state", phrase_terms) if len(phrase_terms) > 1 else None
            wildcard_query = Wildcard("state", f"*{query_str}*")
            combined_query = Or([phrase_query, wildcard_query]) if phrase_query else wildcard_query
            results = searcher.search(combined_query, limit=None)
            for result in results:
                data = {'id': result['id'], 'title': result['title'], 'energy': result['energy']}
                res.append(data)
        return res
    
    def pie_data(self, query_state):
        res = list()
        renewable = 0
        solar = 0
        wind = 0
        hydro = 0
        nuclear = 0
        coal = 0
        gas = 0
        oil = 0
        petroleum = 0
        # print(query_state)
        energy_keywords = ["renewable", "solar", "wind", "hydro", "nuclear", "coal", "gas", "oil", "petroleum"]
        query_str = query_state.replace('_', ' ')
        with self.ix.searcher() as searcher:
            wildcard_query = Wildcard("state", f"*{query_str}*")
            results = searcher.search(wildcard_query, limit=None)
            for result in results:
                try:
                    value = result.get('energy', '')
                    energy_list = ast.literal_eval(value)
                    # print(energy_list)
                    if isinstance(energy_list, list):
                        for type in energy_list:
                            print(type)
                            if str(type) in energy_keywords:
                                if type == 'renewable':
                                    renewable += 1
                                elif type == 'solar':
                                    solar += 1
                                elif type == 'wind':
                                    wind += 1
                                elif type == 'hydro':
                                    hydro += 1
                                elif type == 'nuclear':
                                    nuclear += 1
                                elif type == 'coal':
                                    coal += 1
                                elif type == 'gas':
                                    gas += 1
                                elif type == 'oil':
                                    oil += 1
                                elif type == 'petroleum':
                                    petroleum += 1
                except:
                    print("invalid format")

        res = [{"label": "renewable", "value": renewable, "color": "#FF5733"},
               {"label": "solar", "value": solar, "color": "#33FFBD"},
               {"label": "wind", "value": wind, "color": "#FFC300"},
               {"label": "hydro", "value": hydro, "color": "#DAF7A6"},
               {"label": "nuclear", "value": nuclear, "color": "#900C3F"},
               {"label": "coal", "value": coal, "color": "#581845"},
               {"label": "gas", "value": gas, "color": "#FF33FF"},
               {"label": "oil", "value": oil, "color": "#337FFF"},
               {"label": "petroleum", "value": petroleum, "color": "#57FF33"}]
        return res
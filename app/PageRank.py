import pickle
import numpy as np
from scipy.sparse import lil_matrix

class Page_Rank(object):

    def __init__(self, filename, iterations):
        self.data = self.load_data(filename) # load data from pickle file
        self.urls = list(self.data.keys()) # list of urls
        self.V = len(self.urls) # number of urls
        self.d = 0.9 # random serfer probability
        self.ranks = np.array([1 / self.V] * self.V) # initial page rank scores

        self.adj_matrix = self.create_adj_matrix() # create inital matrix of number of outgoing links for each url scrapped
        self.outgoing_links_matrix = self.create_outgoing_links_matrix() # create matrix for total outgoing values for each url

        self.transition_matrix = self.create_transition_matrix() # normalize matrix

        self.iterate_pagerank(iterations) # iterate to get final page rank scores

    # loads data from pickle file
    def load_data(self, filename):
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        return data['url_outgoing_links'] # only return data on outgoing links
    
    # create initial matrix with number of outgoing links for each url
    def create_adj_matrix(self):
        matrix = lil_matrix((self.V, self.V), dtype=np.float64)
        url_index = {url: i for i, url in enumerate(self.urls)}

        for url, outgoing_links in self.data.items():
            for link_dict in outgoing_links.values():
                for link, _ in link_dict.items():
                    if link in url_index:
                        matrix[url_index[url], url_index[link]] = 1

        return matrix.tocsr()

    # get total number of outgoing links for each url
    def create_outgoing_links_matrix(self):
        outgoing_links = np.sum(self.adj_matrix, axis=1)
        return outgoing_links.reshape((self.V, 1))
    
    # normalize matrix based on number of outgoing links
    def create_transition_matrix(self):
    # Calculate the sum of outgoing links for each row
        row_sums = np.array(self.adj_matrix.sum(axis=1)).flatten()  # Convert to 1D array
        row_sums[row_sums == 0] = 1  # Avoid division by zero for dangling nodes

    # Normalize each row by the sum of outgoing links
        row_normalized = self.adj_matrix.multiply(1 / row_sums[:, np.newaxis])  # Sparse division

    # Apply damping factor
        transition_matrix = row_normalized * self.d

    # Handle dangling nodes (distribute uniformly if no outgoing links)
        dangling_nodes = (row_sums == 1)
        dangling_weight = self.d / self.V
        transition_matrix += dangling_weight * lil_matrix((self.V, self.V))

        return transition_matrix.tocsr()  # Ensure it remains a CSR sparse matrix

    # iterate to get final page rank scores
    def iterate_pagerank(self, num_iterations):
        for iteration in range(num_iterations):
        # Use sparse matrix multiplication
            new_ranks = self.transition_matrix.T @ self.ranks
            norm = np.sum(np.abs(new_ranks - self.ranks))
            print(f"Iteration {iteration + 1}, Norm: {norm}")
            self.ranks = new_ranks

    # query function to get top 10 urls based on keyword
    def query(self, keyword):
        results = []
        for url in self.urls:
            # check if keyword is in text
            if keyword.lower() in self.data[url][1]['text'].lower():
                index = self.urls.index(url)
                results.append((url, self.ranks[index]))
        results.sort(key=lambda x: x[1], reverse=True)
        # return top 10 urls
        return results[:10]
    
    # deubgging functions
    def print_adj_matrix(self):
        print("Adjacency Matrix:")
        print(self.adj_matrix)
    # debugging functions
    def print_outgoing_links_matrix(self):
        print("Outgoing Links Matrix:")
        print(self.outgoing_links_matrix)
    # debugging functions
    def print_transition_matrix(self):
        print("Transition Matrix:")
        print(self.transition_matrix)
    # debugging functions
    def print_ranks(self):
        print("PageRank Scores:")
        print(self.ranks)

# def main():
#     # set file name
#     filename = "./5k_crawler_state.pkl"
#     # itterations
#     iterations = 20
#     # build pagerank object
#     pr = Page_Rank(filename, iterations)
    
#     # infinite loop to query keyword
#     while True:
#         keyword = input("Enter keyword to search: ")
#         if keyword.lower() == 'exit':
#             break
#         # get top 10 urls based on keyword
#         results = pr.query(keyword)
#         for url, score in results:
#             print(f'{url}, {score}')
    
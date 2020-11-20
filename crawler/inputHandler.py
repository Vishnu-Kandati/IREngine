'''
switch smell -> refactoring (64.39 -> 81.30)
'''
def get_input():

    query = input('Enter your query (default: "wildfires california"): ').strip() or 'wildfires california'
    num_start_pages = input("Enter the number of start pages (default: 10): ").strip() or 10
    n = input("Enter the number of pages to be returned (at least 10, default: 1000): ").strip()
    page_link_limit = input("Enter the max. no. of links to be fetched from each page (at least 10, default: 25): ")\
        .strip()
    mode = input("Enter mode 'bfs' or 'focused' (default: 'bfs'): ").strip() or 'bfs'
    relevance_threshold = input('Enter the relevance threshold (min: 0, max: 4.75, default: 1): ').strip()

    print('\nObtaining start pages...\n')
    # checking if values are input correctly, otherwise use defaults

    if len(n) == 0 or int(n) < 10:
        n = 1000

    if len(page_link_limit) == 0 or int(page_link_limit) < 10:
        page_link_limit = 25

    if len(relevance_threshold) == 0 or (int(relevance_threshold) < 0 or int(relevance_threshold) > 4.75):
        relevance_threshold = 1

    return query, int(num_start_pages), int(n), int(page_link_limit), mode, int(relevance_threshold)

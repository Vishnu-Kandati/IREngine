class PageCount:
    def __init__(self):
        self.page_num = 0

    def increment(self):
        self.page_num += 1

    def get_page_num(self):
        return self.page_num


page_count = PageCount()
class PriorityQueue:
    def __init__(self):
        self.queue = []

    # find the index at which the new item will be stored
    # (using binary search)
    # descending order of page_promise is used
    def calculate_index(self, item, start, end):
        if len(self.queue) > 0:
            if start < end:
                index = int((start + end) / 2)
                if item[0] == self.queue[index][0]:
                    return index
                elif item[0] > self.queue[index][0]:
                    return self.calculate_index(item, start, index - 1)
                elif item[0] < self.queue[index][0]:
                    return self.calculate_index(item, index + 1, end)
            elif start == end:
                if end != len(self.queue):
                    if item[0] > self.queue[start][0]:
                        return start
                    else:
                        return start + 1
                else:
                    if item[0] < self.queue[end - 1][0]:
                        return end
                    else:
                        return end - 1
            else:
                return start
        else:
            return start

    # display the contents of the queue.
    def display_queue(self):
        print("Queue:")
        for item in self.queue:
            print(item)

    # add an item to the queue
    def enqueue(self, item):

        if item not in self.queue:
            index = self.calculate_index(item, 0, len(self.queue))  # calculate index for new element
            self.queue.insert(index, item)  # insert element at index

    # pop an item from the queue
    def dequeue(self):

        # while len(self.queue) <= 0:
        #     continue

        item = self.queue[0]  # item with highest promise
        del self.queue[0]  # remove item from the queue
        return item

    # Returns the size of the queue
    def get_size(self):
        return len(self.queue)

    # delete the item from the queue
    def delete(self, index):
        item = self.queue[index]
        del self.queue[index]  # delete item at index
        return item

    # find a url in the queue
    def find(self, url):
        i = -1

        for index in range(len(self.queue)):
            if self.queue[index][1] == url:
                i = index
        return i

    # update the promise of a url if it is found while parsing another page
    def update_queue(self, url, parent_relevance):

        index = self.find(url)
        if index != -1:
            item = self.queue[index]
            del self.queue[index]  # remove item from queue
            item[0] += 0.25 * parent_relevance  # update promise

            # index = self.calculate_index(item, 0, len(self.queue))  # compute new index for item
            # self.queue.insert(index, item)  # insert at index
            self.enqueue(item)  # recompute the index (using the updated promise) and insert item at index
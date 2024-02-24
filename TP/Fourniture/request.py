class Request:
    def __init__(self, timestamp, queue_name):
        self.timestamp = timestamp
        self.owner_id = queue_name

    def __repr__(self):
        return "(timestamp: %s, queue: %s)" % (self.timestamp, self.owner_id)

    # used by PriorityQueue for comparing elements
    def __lt__(self, other):
        return self.timestamp < other.timestamp

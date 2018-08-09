from DNDMapTool.Map import Map


# stores the gamestate
class Game(object):
    def __init__(self, name, overview_map=None, maps=[]):
        self.name = name
        self.overview_map = overview_map
        self.overview_map_dm = None
        self.maps = maps
        self.curr_map_index = 0

    def curr_map(self):
        return self.maps[self.curr_map_index]

    def next_map(self):
        self.curr_map_index += 1
        if self.curr_map_index >= len(self.maps):
            print("no more maps")
            self.curr_map_index -= 1

    def prev_map(self):
        self.curr_map_index -= 1
        if self.curr_map_index < 0:
            print("already first map")
            self.curr_map_index += 1


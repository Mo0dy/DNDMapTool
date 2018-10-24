from DNDMapTool.Map import Map


class Game(object):
    """Stores the gamestates """
    def __init__(self, name, overview_map=None, maps=[]):
        """

        :param name (string): the name of the current game
        :param overview_map (Map): the overview map gets stored separately from the other maps
        :param maps ([Map]): the maps for the current game
        """
        self.name = name
        self.overview_map = overview_map
        self.overview_map_dm = None  # used if a separate map is shown for the dm
        self.maps = maps
        self.curr_map_index = 0  # a pointer to the list index of the currently selected map

    def curr_map(self):
        """Returns the currently selected map"""
        return self.maps[self.curr_map_index]

    def next_map(self):
        """selects the next map. clips selection"""
        self.curr_map_index += 1
        if self.curr_map_index >= len(self.maps):
            print("no more maps")
            self.curr_map_index -= 1

    def prev_map(self):
        """selects the previous map. clips selection"""
        self.curr_map_index -= 1
        if self.curr_map_index < 0:
            print("already first map")
            self.curr_map_index += 1


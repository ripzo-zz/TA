from operator import ge
import re

class GridIndex:
    def __init__(self, grid_size, dimension, max_value, event_keys):
        self.grid_size = grid_size
        self.dimension = dimension
        self.grid_length = max_value / grid_size
        self.amount_data = 0
        self.temp_maximum = [] # use for update dominant grid if deletion happen
        self.temp_current_position = [] # use for update dominant grid if deletion happen
        self.dominant_grid = []
        self.event_keys = event_keys
        self.grid = {}

        # make grid dictionary
        for i in range(grid_size ** dimension):
            grid_key = 'G'
            for j in range(dimension-1, -1, -1):
                    number = i//(grid_size**j)
                    if(number >= grid_size):
                        number %= grid_size
                    grid_key += ' '+str(number)
            self.grid[grid_key] = {}
            self.grid[grid_key]['member'] = []
            self.grid[grid_key]['flag'] = 0
    
    # update grid per timestamp
    def update(self, events):
        for event in events:
            if event['action'] == 1:
                self.insertion(event)
            elif event['action'] == 0:
                self.deletion(event)

    # insertion function
    def insertion(self, event):
        grid_key = 'G'
        for key in event.keys():
            if key != 'id' and key != 'timestamp' and key != 'action':
                axes = int(event[key] // self.grid_length)
                if axes == self.grid_size:
                    axes -= 1
                grid_key += ' '+str(axes)
        self.grid[grid_key]['member'].append(event)
        self.amount_data += 1

        # update dominant grid
        if self.amount_data == 1:
            self.dominant_grid.append(grid_key)
        else:
            current_g = list(map(int, re.findall(r'\d+', grid_key)))
            i = 0
            while i < len(self.dominant_grid):
                dominant_index_counter = 0
                same_index_counter = 0
                dominated_index_counter = 0
                dominant_g = list(map(int, re.findall(r'\d+', self.dominant_grid[i])))
                for j in range(len(dominant_g)):
                    if current_g[j] < dominant_g[j]:
                        dominant_index_counter += 1
                    elif current_g[j] == dominant_g[j]:
                        same_index_counter += 1
                    else:
                        dominated_index_counter += 1
                if dominant_index_counter == self.dimension:
                    self.dominant_grid.pop(i)
                elif dominated_index_counter == self.dimension or same_index_counter == self.dimension:
                    return
                else:
                    i += 1
            self.dominant_grid.append(grid_key)

    # deletion function
    def deletion(self, event):
        grid_key = 'G'
        for key in event.keys():
            if key != 'id' and key != 'timestamp' and key != 'action':
                axes = int(event[key] // self.grid_length)
                if axes == self.grid_size:
                    axes -= 1
                grid_key += ' '+str(axes)
        for i in range(len(self.grid[grid_key]['member'])):
            if self.grid[grid_key]['member'][i]['id'] == event['id']:
                self.grid[grid_key]['member'].pop(i)
                self.amount_data -= 1
                break

        if grid_key in self.dominant_grid and len(self.grid[grid_key]['member']) == 0:
            self.dominant_grid.remove(grid_key)
            if self.amount_data > len(self.dominant_grid):
                current_position = list(map(int, re.findall(r'\d+', grid_key)))
                self.maximum_index_to_be_dominant(current_position)
                self.search_dominant_grid(0, 'G')

    def search_dominant_grid(self, index, parent_key):
        current_position = self.temp_current_position[index]
        current_maximum = self.temp_maximum[index]
        while current_position < current_maximum :
            if index == 0:
                self.temp_current_position[0] = current_position
            current_key = parent_key+' '+str(current_position)
            if self.dimension - index > 1:
                self.search_dominant_grid(index+1, current_key)
            else:
                if len(self.grid[current_key]['member']) :
                    current_g = list(map(int, re.findall(r'\d+', current_key)))
                    i = 0
                    while i < len(self.dominant_grid):
                        dominant_index_counter = 0
                        same_index_counter = 0
                        dominated_index_counter = 0
                        dominant_g = list(map(int, re.findall(r'\d+', self.dominant_grid[i])))
                        for j in range(len(dominant_g)):
                            if current_g[j] < dominant_g[j]:
                                dominant_index_counter += 1
                            elif current_g[j] == dominant_g[j]:
                                same_index_counter += 1
                        if dominant_index_counter == self.dimension:
                            self.dominant_grid.pop(i)
                        elif dominated_index_counter == self.dimension or same_index_counter == self.dimension:
                            return
                        else:
                            i += 1
                    self.dominant_grid.append(current_key)
                    dif_index = []
                    for ind in range(self.dimension):
                        if current_g[ind] != self.temp_current_position[ind]:
                            dif_index.append(ind)
                    if len(dif_index) == 1:
                            self.temp_maximum[j] = current_g[j]+1
            current_position += 1

    def maximum_index_to_be_dominant(self, current_position):
        self.temp_maximum = []
        self.temp_current_position = []
        for i in range(self.dimension):
            self.temp_maximum.append(self.grid_size)
            self.temp_current_position.append(current_position[i]+1)
    
    def get_current_sky(self):
        current_sky = []
        events = self.get_all_grid_members()
        # events = []

        # for grid_key in self.dominant_grid:
        #     sky_events = self.get_grid_sky(grid_key)
        #     for event in sky_events:
        #         events.append(event)

        for event in events:
            if len(current_sky) > 0:
                i = 0
                put = 1
                while i < len(current_sky):
                    if event['id'] == current_sky[i]['id']:
                        put = 0
                        break

                    dominant_index_counter = 0
                    same_value_counter = 0
                    for j in range(self.dimension):
                        if event[self.event_keys[j]] < current_sky[i][self.event_keys[j]]:
                            dominant_index_counter += 1
                        elif event[self.event_keys[j]] == current_sky[i][self.event_keys[j]]:
                            same_value_counter += 1
                    if (dominant_index_counter + same_value_counter) == self.dimension and same_value_counter < self.dimension:
                        current_sky.pop(i)
                        i -= 1
                    elif dominant_index_counter == 0 and same_value_counter != self.dimension:
                        put = 0
                        break
                    i += 1
                if put == 1:
                    current_sky.append(event)
            else:
                current_sky.append(event)
        return current_sky
    
    def get_all_grid_members(self):
        members = []
        for grid_key in self.dominant_grid:
            for event in self.grid[grid_key]['member']:
                members.append(event)
        return members

    def reset_flag(self):
        for grid_key in self.grid:
            self.grid[grid_key]['flag'] = 0
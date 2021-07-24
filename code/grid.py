from operator import ge
import re
import queue
import copy

class GridIndex:
    def __init__(self, grid_size, dimension, max_value, event_keys):
        self.grid_size = grid_size
        self.dimension = dimension
        self.grid_length = max_value / grid_size
        self.amount_data = 0
        self.temp_maximum = []  # use for update dominant grid if deletion happen
        self.temp_current_position = []  # use for update dominant grid if deletion happen
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
                dominant_g = list(
                    map(int, re.findall(r'\d+', self.dominant_grid[i])))
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
                self._search_dominant_grid(current_position)

    def generate_key_from_position(self, position):
        key = f"G {' '.join([str(n) for n in position])}"
        return key

    def _search_dominant_grid(self, current_position):
        limit = [self.grid_size] * self.dimension
        bfs = queue.Queue()
        start_position = [x + 1 for x in current_position]
        visited = {}
        bfs.put(self.generate_key_from_position(start_position))
        while not bfs.empty():
            evaluation_key = bfs.get()
            evaluation_position = list(
                map(int, re.findall(r'\d+', evaluation_key)))
            visited[evaluation_key] = True
            if len(self.grid[evaluation_key]['member']):
                for dominant_grid in self.dominant_grid:
                    dominant_index_counter = 0
                    same_index_counter = 0
                    dominated_index_counter = 0
                    dominant_g = list(
                        map(int, re.findall(r'\d+', dominant_grid)))
                    for j in range(len(dominant_g)):
                        if evaluation_position[j] < dominant_g[j]:
                            dominant_index_counter += 1
                        elif evaluation_position[j] == dominant_g[j]:
                            same_index_counter += 1
                    if dominant_index_counter == self.dimension:
                        self.dominant_grid.pop(i)
                    elif dominated_index_counter == self.dimension or same_index_counter == self.dimension:
                        return
                self.dominant_grid.append(evaluation_key)
                dif = 0
                for ind in range(self.dimension):
                    if evaluation_position[ind] != start_position[ind]:
                        dif += 1
                        if dif > 1:
                            break

                if dif == 1:
                    limit[j] = min(evaluation_position[j]+1, limit[j])

            for i in range(self.dimension):
                next_position = copy.copy(evaluation_position)
                next_position[i] += 1
                key = self.generate_key_from_position(next_position)
                if key not in visited and next_position[i] <= limit[i]:
                    bfs.put(next_position)

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
from datetime import time
from grid import GridIndex
from dataread import DataRead
from tqdm import tqdm

class Precompute:
    def __init__(self, grid_size, dataset_path):
        self.data, self.max_value, self.max_time, self.keys = DataRead(dataset_path)
        self.skybox = {}
        self.grid = GridIndex(grid_size, len(self.keys), self.max_value, self.keys)
        pbar = tqdm(total=self.max_time+1)
        for i in range(self.max_time+1):
            if(i > 0):
                self.skybox[i] = self.skybox[i-1].copy()
            else:
                self.skybox[i] = {}
            try:
                self.grid.update(self.data[i])
            except:
                self.grid.update([])
            current_skies = self.grid.get_current_sky()
            for sky in current_skies:
                id = sky['id']
                try:
                    self.skybox[i][id] += 1
                except:
                    self.skybox[i][id] = 1
            pbar.update(1)
        pbar.close()
    
    def get_durable_data(self, time_start, time_end, minimum_percent):
        if time_end < 0:
            time_end = self.max_time
        elif time_end < time_start:
            print('error: time_end must bigger than time_start')
            return []
        elif time_start > self.max_time:
            return []
        if time_start < 0:
            time_start = 0
        time_length = time_end - time_start + 1
        temp_result = self.skybox[time_end].copy()
        result = []
        for k in temp_result:
            try:
                temp_result[k] -= self.skybox[time_start-1][k]
            except:
                pass
        for k in temp_result:
            if (temp_result[k]/time_length) >= minimum_percent:
                result.append({
                    'id' : k,
                    'kemunculan' : temp_result[k],
                    'persentase_kemunculan' : "%.2f" % (temp_result[k]/time_length*100) + '%',
                    })
        return result
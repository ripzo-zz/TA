from dataread import DataRead

class Naive:
    def __init__(self, dataset_path):
        self.data, self.max_value, self.max_time, self.event_keys = DataRead(dataset_path)
        self.computing_data = []
        self.skybox = {}
        self.dimension = len(self.data[1][0].keys())-3
        print(self.max_time)
        for i in range(self.max_time+1):
            if(i > 0):
                self.skybox[i] = self.skybox[i-1].copy()
            else:
                self.skybox[i] = {}
            try:
                for d in self.data[i]:
                    if d['action'] == 1:
                        self.computing_data.append(d)
                    else:
                        for j in range(len(self.computing_data)):
                            if self.computing_data[j]['id'] == d['id']:
                                self.computing_data.pop(j)
                                break
            except:
                pass
            
            try:
                current_skies = self.get_current_sky(self.computing_data)
                for sky in current_skies:
                    id = sky['id']
                    try:
                        self.skybox[i][id] += 1
                    except:
                        self.skybox[i][id] = 1
            except:
                pass

    def get_current_sky(self, data):
        current_sky = []
        for event in data:
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
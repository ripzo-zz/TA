import pandas as pd

def DataRead(path, reverse_axes=[]):
    df = pd.read_csv(path, sep=',')
    data = {}
    event_keys = []
    max_value = 0
    max_time = 0

    for col_name in df.columns:
        if col_name != 'id' and col_name != 'ts_in' and col_name != 'ts_out':
            event_keys.append(col_name)

    for index, row in df.iterrows():
        a_dict_in = {}
        a_dict_out = {}
        for column in df.columns:
            if column == 'ts_in':
                a_dict_in['timestamp'] = int(row[column])
                a_dict_in['action'] = 1 #masuk
                if row[column] > max_time:
                    max_time = row[column]
            elif column == 'ts_out':
                a_dict_out['timestamp'] = int(row[column])
                a_dict_out['action'] = 0 #keluar
                if row[column] > max_time:
                    max_time = row[column]
            else:
                if column == 'name':
                    column = 'id'
                a_dict_in[column] = row[column]
                a_dict_out[column] = row[column]
                
                if column != 'id':
                    if row[column] > max_value:
                        max_value = row[column]
        try:
            data[a_dict_in['timestamp']].append(a_dict_in)
        except:
            data[a_dict_in['timestamp']] = []
            data[a_dict_in['timestamp']].append(a_dict_in)

        try:
            data[a_dict_out['timestamp']].append(a_dict_out)
        except:
            data[a_dict_out['timestamp']] = []
            data[a_dict_out['timestamp']].append(a_dict_out)
    
    if len(reverse_axes):
        keys = []
        for k in data[1][0].keys():
            keys.append(k)
        for d in data:
            for e in data[d]:
                for axes in reverse_axes:
                    e[keys[axes+1]] = max_value - e[keys[axes+1]]
    
    return data, max_value, int(max_time), event_keys
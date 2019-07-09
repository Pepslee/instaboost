from os.path import join

import pandas as pd
import config

base_path = config.data_base_path

path = join(base_path, 'p.i.n.k.m.a.n', 'g.r.u.p.p.i.r.o.v.k.a.2.0_active')

frame = pd.read_csv(path, header=None)

new_frame = frame[0].value_counts()
df_value_counts = new_frame.reset_index()
df_value_counts.columns = ['unique_values', 'counts']
new_df_value_counts = df_value_counts[df_value_counts['counts'] > 5]
active_list = new_df_value_counts['unique_values']

followers_df = pd.DataFrame(active_list)
followers_df.to_csv(path + '_filtered', encoding='utf-8', mode='w', index=False,
                    header=False)
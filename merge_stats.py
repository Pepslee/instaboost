import pandas as pd


home = pd.read_csv('g.r.u.p.p.i.r.o.v.k.a.2.0_followed_stats_home')
work = pd.read_csv('g.r.u.p.p.i.r.o.v.k.a.2.0_followed_stats_work')

new_df = pd.DataFrame(columns=['name', 'id', 'followers', 'follow', 'posts', 'like', 'time'])


work_name_list = list(work['name'])
for index, row in home.iterrows():
    if row['name'] not in work_name_list:
        new_df = new_df.append(row, ignore_index=True)

new_df = new_df.append(work, sort=False, ignore_index=True)
new_df.to_csv('g.r.u.p.p.i.r.o.v.k.a.2.0_followed_stats_merged', index=False)


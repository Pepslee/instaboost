import pandas as pd


def intersection(lst1, lst2):
    return set(lst1).intersection(lst2)


path_1 = './p.i.n.k.m.a.n/p.i.n.k.m.a.n_follows'
path_2 = './p.i.n.k.m.a.n/g.r.u.p.p.i.r.o.v.k.a'

target_list_1 = list(pd.read_csv(path_1, header=None)[0])
target_list_2 = list(pd.read_csv(path_2, header=None)[0])


result = intersection(target_list_1, target_list_2)

print(result.__len__())
print(result)

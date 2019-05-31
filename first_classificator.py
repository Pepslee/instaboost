import pandas as pd
import math
import numpy as np

path = 'g.r.u.p.p.i.r.o.v.k.a.2.0_followed_stats'

df = pd.read_csv(path)

val = df.loc[df['name'] == 'annaivanova_1102', :].values[0]
nfd = val[2]
nf = val[3]
n_p = val[4]
P = -0.19*np.log10(nfd) + 0.42 * np.log10(nf) - 0.18 * np.log10(n_p)
print(P)
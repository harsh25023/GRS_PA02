import numpy as np
import matplotlib.pyplot as plt


plt.rcParams.update({
    "font.size": 12,
    "figure.figsize": (7,5),
    "axes.grid": True,
    "lines.linewidth": 2,
    "lines.markersize": 7
})

SYSTEM_INFO = "Intel i7-12700 | Linux | TCP | 5s duration"

sizes = np.array([64,512,4096,65536])
threads = np.array([1,2,4,8])


A1_thr = np.array([
 [0.073583,0.076157,0.074293,0.074423],
 [0.572926,0.572355,0.591591,0.587251],
 [4.215354,4.191250,4.255973,4.210347],
 [24.767470,24.324971,24.833635,24.607143]
])

A2_thr = np.array([
 [0.071879,0.071632,0.072761,0.073419],
 [0.584526,0.570515,0.569787,0.573577],
 [4.173116,4.163345,4.142943,4.096793],
 [25.665261,25.390219,25.977841,26.463542]
])

A3_thr = np.array([
 [0.073934,0.073525,0.075043,0.072956],
 [0.550928,0.550176,0.549688,0.574604],
 [4.197738,4.144018,4.190031,4.147288],
 [25.742121,26.145299,24.762332,25.864700]
])


A1_lat = np.array([
 [6.933046,6.698010,6.866619,6.854533],
 [7.123936,7.130935,6.898859,6.949882],
 [7.748586,7.793126,7.674455,7.757701],
 [21.143135,21.528253,21.086688,21.281124]
])

A2_lat = np.array([
 [7.097782,7.122110,7.011731,6.948587],
 [6.982460,7.153924,7.162379,7.115861],
 [7.827125,7.845782,7.884295,7.973238],
 [20.402502,20.623744,20.156951,19.786457]
])

A3_lat = np.array([
 [6.900194,6.938303,6.798127,6.992860],
 [7.408945,7.419372,7.425917,7.103302],
 [7.781283,7.882016,7.795700,7.876166],
 [20.341730,20.027394,21.146897,20.245112]
])


A1_cycles = np.array([
 [9249682073,9623879537,9167699808,9443950311],
 [9093511338,9179181331,9259870994,9298202016],
 [10872591278,10806161567,10725986075,10899546131],
 [9344738486,9065794612,9290247703,9172237187]
])

A2_cycles = np.array([
 [9153526169,9338806143,9146334608,9299867083],
 [8939745642,9169113927,9070737133,9035541918],
 [10283377172,10560672419,10626914258,10388902003],
 [9533967957,9537650615,9524435096,9741243951]
])

A3_cycles = np.array([
 [8957101701,9119431609,9046767720,9156909984],
 [9161911999,9031364240,8949858738,8957523538],
 [10384352549,10342509704,10465310882,10448676629],
 [9322236913,9730420341,9482671721,9653968082]
])


A1_l1 = np.array([
 [128846171,127073921,135325814,130116033],
 [156923166,144646507,132981215,144464836],
 [270809851,276782091,284957237,274958805],
 [587535459,590644955,605743101,598865877]
])

A2_l1 = np.array([
 [135646659,137014858,133370800,127175345],
 [138437661,152045252,141688092,151005520],
 [274663792,264987761,265785222,265282036],
 [616969206,604914537,637941769,659081154]
])

A3_l1 = np.array([
 [120299929,140853507,126135694,122292493],
 [152872245,138346356,131988717,139968992],
 [276390471,275583349,254545397,269934283],
 [631914778,636221832,633669184,651784411]
])

A1_cs = np.array([
 [718563,743770,725507,726777],
 [699359,698727,722153,716831],
 [643059,639380,649308,642500],
 [236258,231995,237031,234748]
])

A2_cs = np.array([
 [701925,699580,710550,716955],
 [713517,696419,695540,700124],
 [636701,635160,632030,624989],
 [244878,242206,247790,252426]
])

A3_cs = np.array([
 [722000,717986,732823,712601],
 [672504,671582,671128,701428],
 [640439,632230,639258,632759],
 [245560,249403,236273,246706]
])


def save(name):
    plt.title(name.replace("_"," ") + "\n" + SYSTEM_INFO)
    plt.tight_layout()
    plt.savefig(name + ".png", dpi=300)
    plt.close()

def speedup(mat):
    return mat / mat[:,0][:,None]

def efficiency(mat):
    return speedup(mat) / threads

def cycles_per_byte(cycles):
    return cycles / (sizes[:,None]*5)


for n,m in [("A1",A1_thr),("A2",A2_thr),("A3",A3_thr)]:
    plt.plot(sizes,m[:,3],marker='o',label=n)
plt.xscale('log')
plt.xlabel("Message Size (bytes)")
plt.ylabel("Throughput (Gbps)")
plt.legend(title="Impl")
save("throughput_vs_size")

for n,m in [("A1",A1_lat),("A2",A2_lat),("A3",A3_lat)]:
    plt.plot(threads,m[2],marker='o',label=n)
plt.xlabel("Threads")
plt.ylabel("Latency (µs)")
plt.legend(title="Impl")
save("latency_vs_threads")

for n,m in [("A1",A1_l1),("A2",A2_l1),("A3",A3_l1)]:
    plt.plot(sizes,m[:,3],marker='o',label=n)
plt.xscale('log')
plt.xlabel("Message Size (bytes)")
plt.ylabel("L1 Cache Misses")
plt.legend(title="Impl")
save("L1_vs_size")

for n,m in [("A1",A1_cycles),("A2",A2_cycles),("A3",A3_cycles)]:
    plt.plot(sizes,cycles_per_byte(m)[:,3],marker='o',label=n)
plt.xscale('log')
plt.xlabel("Message Size (bytes)")
plt.ylabel("Cycles / Byte")
plt.legend(title="Impl")
save("cycles_per_byte")


for n,m in [("A1",A1_thr),("A2",A2_thr),("A3",A3_thr)]:
    plt.plot(threads,m[2],marker='o',label=n)
plt.xlabel("Threads")
plt.ylabel("Throughput (Gbps)")
plt.legend(title="Impl")
save("throughput_vs_threads")

for n,m in [("A1",A1_thr),("A2",A2_thr),("A3",A3_thr)]:
    plt.plot(threads,speedup(m)[2],marker='o',label=n)
plt.xlabel("Threads")
plt.ylabel("Speedup")
plt.legend(title="Impl")
save("speedup")

for n,m in [("A1",A1_cs),("A2",A2_cs),("A3",A3_cs)]:
    plt.plot(threads,m[2],marker='o',label=n)
plt.xlabel("Threads")
plt.ylabel("Context Switches")
plt.legend(title="Impl")
save("context_switches")

for n,m in [("A1",A1_thr),("A2",A2_thr),("A3",A3_thr)]:
    plt.plot(threads, efficiency(m)[2], marker='o', label=n)

plt.xlabel("Threads")
plt.ylabel("Parallel Efficiency")
plt.ylim(0, 1.05)
plt.legend(title="Impl")

save("efficiency")


print("All plots generated.")


CPU_N=2

mkdir EVT && cd EVT
prun_evts.py -c "gen_zee.py" -nt $CPU_N -o zee.EVT.root --nov 500 --novPerJob 100 -m

cd ../
mkdir HIT && cd HIT
simu_trf.py -i ../EVT/zee.EVT.root -nt $CPU_N -o zee.HIT.root

cd ../
mkdir ESD && cd ESD
digit_trf.py -i ../HIT/* -o zee.ESD.root

cd ../
mkdir AOD && cd AOD
reco_trf.py -i ../ESD/* -o zee.AOD.root

cd ../
mkdir NTUPLE && cd NTUPLE
prun_jobs.py -c "ntuple_trf.py -i %IN -o %OUT" -i ../AOD/ -o zee.NTUPLE.root  -m
cd ../
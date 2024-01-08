CPU_N=$(grep -c ^processor /proc/cpuinfo)
CPU_N=8
cd /data/LZT/data_prod/ZEE/prod01/
################ prod01 ###################
# cd /home/edesouza/workspace/data_production/zee/

# mkdir prod01 && cd prod01
# mkdir EVT && cd EVT

# # Generate events 
# prun_evts.py -c "gen_zee.py" -nt $CPU_N -o zee.EVT.root --nov 50000 --novPerJob 100 -m

# cd ../

# mkdir HIT && cd HIT

# simu_trf.py -i ../EVT/zee.EVT.root -nt $CPU_N -o zee.HIT.root

# cd ../

mkdir ESD && cd ESD

digit_trf.py -i ../HIT/* -o zee.ESD.root

cd ../

mkdir AOD && cd AOD

reco_trf.py -i ../ESD/* -o zee.AOD.root

cd ../

mkdir NTUPLE && cd NTUPLE
prun_jobs.py -c "ntuple_trf.py -i %IN -o %OUT" -i ../AOD/ -o zee.NTUPLE.root  -m
cd ../

# ################ prod02 ###################
cd /data/LZT/data_prod/ZEE/

mkdir prod02 && cd prod02
mkdir EVT && cd EVT

# # Generate events 
prun_evts.py -c "gen_zee.py" -nt $CPU_N -o zee.EVT.root --nov 100000 --novPerJob 100 -m

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


# ################ prod03 ###################
cd /data/LZT/data_prod/ZEE/

mkdir prod03 && cd prod03
mkdir EVT && cd EVT

# # Generate events 
prun_evts.py -c "gen_zee.py" -nt $CPU_N -o zee.EVT.root --nov 100000 --novPerJob 100 -m

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

# ################ prod04 ###################
cd /data/LZT/data_prod/ZEE/

mkdir prod04 && cd prod04
mkdir EVT && cd EVT

# Generate events 
prun_evts.py -c "gen_zee.py" -nt $CPU_N -o zee.EVT.root --nov 100000 --novPerJob 100 -m

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


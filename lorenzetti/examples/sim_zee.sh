

NOV=50000
seed=516

# mkdir -p Zee/EVT
# mkdir -p Zee/HIT
# mkdir -p Zee/ESD
# mkdir -p Zee/AOD
# mkdir -p Zee/NTUPLE

# generate 10k Zee events with pythia
# cd Zee/EVT
# prun_evts.py -c "gen_zee.py --pileupAvg 0 -o %OUT" -nt 10 --nov $NOV --seed $seed --novPerJob 200 -o Zee.EVT.root
# cd ..

# generate hits around the truth particle seed
cd HIT
prun_jobs.py -c "simu_trf.py -i %IN -o %OUT -nt 10 --enableMagneticField -t 10" -nt 4 -i ../EVT -o Zee.HIT.root
cd ..

# digitalization
cd ESD
prun_jobs.py -c "digit_trf.py -i %IN -o %OUT" -i ../HIT/ -o Zee.ESD.root 
cd ..

# reconstruction
cd AOD
prun_jobs.py -c "reco_trf.py -i %IN -o %OUT" -i ../ESD/ -o Zee.AOD.root  -m
cd ..

# ntuple prod
cd NTUPLE
prun_jobs.py -c "ntuple_trf.py -i %IN -o %OUT" -i ../AOD/ -o Zee.NTUPLE.root  -m
cd ..


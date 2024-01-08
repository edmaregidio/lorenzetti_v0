

# NOV=1000
# seed=512

# mkdir -p JF17/EVT
mkdir -p HITa
mkdir -p ESD
mkdir -p AOD

# # generate 10k JF17 events with pythia
# cd JF17/EVT
# # prun_evts.py -c "gen_jets.py --pileupAvg 0 --nov %NOV --eventNumber %OFFSET -o %OUT -s %SEED" -nt 10 --nov $NOV --seed $seed --novPerJob 200 -o JF17.EVT.root
# prun_evts.py -c "gen_jets.py" -nt 4 -o JF17.EVT.root --nov 1000 -m
# cd ..

# generate hits around the truth particle seed
cd HITa
# prun_jobs.py -c "simu_trf.py -i %IN -o %OUT -nt 20 --enableMagneticField -t 10" -nt 1 -i ../EVT -o JF17.HIT.root
simu_trf.py -i ../EVT/JF17.EVT.root -o JF17.HIT.root
cd ..

# digitalization
cd ESD
# prun_jobs.py -c "digit_trf.py -i %IN -o %OUT" -i ../HIT/ -o JF17.ESD.root -nt 10
digit_trf.py -i ../HIT/* -o JF17.ESD.root
cd ..

# reconstruction
cd AOD
# prun_jobs.py -c "reco_trf.py -i %IN -o %OUT" -i ../ESD/ -o JF17.AOD.root -nt 10 -m
reco_trf.py -i ../ESD/JF17.ESD.root -o JF17.AOD.root
cd ..


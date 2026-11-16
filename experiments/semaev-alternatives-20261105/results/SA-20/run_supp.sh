export OMP_NUM_THREADS=1
cd /home/user/semaev-runs/SA-20
D5=0.14,0.145,0.15,0.155,0.16,0.165,0.17
D6=0.145,0.15,0.155,0.16,0.165
nice -n 10 python3 plant20.py edwards 64 5 20 $D5 11 > results/supp_edwards_64_t5.log 2>&1
nice -n 10 python3 plant20.py weier 64 5 20 $D5 11 > results/supp_weier_64_t5.log 2>&1
nice -n 10 python3 plant20.py edwards 64 6 20 $D6 12 > results/supp_edwards_64_t6.log 2>&1
nice -n 10 python3 plant20.py weier 64 6 20 $D6 12 > results/supp_weier_64_t6.log 2>&1
echo ALLDONE > results/supp_done

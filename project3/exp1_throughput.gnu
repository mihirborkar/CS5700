# Gnuplot script file for plotting data in file "force.dat"
# This file is called   force.p
set   autoscale                        # scale axes automatically
unset log                              # remove any log-scaling
unset label                            # remove any previous labels
set xtic auto                          # set xtics automatically
set ytic auto                          # set ytics automatically
set title "Experiment1"
set xlabel "CBR Rate (Mbps)"
set ylabel "Throughput (Mbps)"
set xr [0.0:0.022]
set yr [0:325]
plot    "exp1-throught.dat" using 1:2 title 'Column' with linespoints , \
        "exp1-throught.dat" using 1:3 title 'Beam' with points
set term png
set output "exp2_NewReno_Reno_throughput.png"
set title "Experienmnet 2 NewReno-Reno Throughtput"
set xlabel "CBR[Mbps]"
set ylabel "Throughput[Mbps]"
set grid
plot 'exp2_NewReno_Reno_throughput.dat' using 1:2 with lp pt 2 lw 1 linecolor rgb "red" title 'NewReno',\
 'exp2_NewReno_Reno_throughput.dat' using 1:3 with lp pt 8 lw 1 lt 1 linecolor rgb "blue" title 'Reno'

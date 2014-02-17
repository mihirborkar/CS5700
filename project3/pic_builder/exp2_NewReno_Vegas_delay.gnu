set term png
set output "exp2_NewReno_Vegas_delay.png"
set title "Experienmnet 2 NewReno-Vegas Latency"
set xlabel "CBR[Mbps]"
set ylabel "Delay[ms]"
set grid
set key left
plot 'exp2_NewReno_Vegas_delay.dat' using 1:2 with lp pt 2 lw 1 linecolor rgb "red" title 'NewReno',\
 'exp2_NewReno_Vegas_delay.dat' using 1:3 with lp pt 8 lw 1 lt 1 linecolor rgb "blue" title 'Vegas'

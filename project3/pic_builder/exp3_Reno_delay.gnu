set term png
set output "exp3_Reno_delay.png"
set title "Experienmnet 3 Reno Latency"
set xlabel "Time[s]"
set ylabel "Latency[ms]"
set grid
plot 'exp3_Reno_RED_delay.dat' using 1:3 with lp pt 2 lw 1 linecolor rgb "red" title 'RED',\
 'exp3_Reno_DropTail_delay.dat' using 1:3 with lp pt 8 lw 1 lt 1 linecolor rgb "blue" title 'Droptail'

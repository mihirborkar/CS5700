set term png
set output "exp3_Reno_RED_delay.png"
set title "Experienmnet 3 Reno RED Latency"
set xlabel "Time[s]"
set ylabel "Latency[ms]"
set grid
set key left
plot 'exp3_Reno_RED_delay.dat' using 1:2 with lp pt 2 lw 1 linecolor rgb "red" title 'CBR',\
 'exp3_Reno_RED_delay.dat' using 1:3 with lp pt 8 lw 1 lt 1 linecolor rgb "#006400" title 'Reno'

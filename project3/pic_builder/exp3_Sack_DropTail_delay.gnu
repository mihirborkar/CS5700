set term png
set output "exp3_Sack_Droptail_delay.png"
set title "Experienmnet 3 SACK Droptail Latency"
set xlabel "Time[s]"
set ylabel "Latency[ms]"
set grid
set key left
plot 'exp3_SACK_DropTail_delay.dat' using 1:2 with lp pt 2 lw 1 linecolor rgb "red" title 'CBR',\
 'exp3_SACK_DropTail_delay.dat' using 1:3 with lp pt 8 lw 1 lt 1 linecolor rgb "#006400" title 'SACK'

set term png
set output "exp3_Sack_delay.png"
set title "Experienmnet 3 SACK Latency"
set xlabel "Time[s]"
set ylabel "Latency[ms]"
set grid
plot 'exp3_SACK_RED_delay.dat' using 1:3 with lp pt 2 lw 1 linecolor rgb "red" title 'RED',\
 'exp3_SACK_DropTail_delay.dat' using 1:3 with lp pt 8 lw 1 lt 1 linecolor rgb "blue" title 'Droptail'

#! /usr/bin/awk -f
BEGIN {
  highest_packet_id = 0;
}
{
  event = $1
  time = $2
  from_node = $3
  to_node = $4
  pkt_type = $5
  pkt_size = $6
  flow_id = $8
  src_addr = $9
  dst_addr = $10
  seq_num = $11
  pkt_id = $12

  if (flow_id = "1"){
    if (pkt_id > highest_packet_id)
      highest_packet_id = pkt_id;
    if (event == "-" && from_node == 0){
      send_time[pkt_id] = time;
    }
    else if (event == "r" && to_node == 3){
      rcv_time[pkt_id] = time;
    }
  }
}
END {
  packet_no = 0; 
  total_delay = 0;
  for (i = 0; i < highest_packet_id; i++){
    if ((send_time[i] != 0) && (rcv_time[i] != 0)){
      start = send_time[i];
      end = rcv_time[i];
      packet_duration = end - start;

    }
    else
      packet_duration = -1;
    if (packet_duration > 0){
      packet_no++;
      total_delay = total_delay + packet_duration;
      }
    }
    printf("%d\t%f\t%f\n", packet_no, total_delay, total_delay/packet_no);
}

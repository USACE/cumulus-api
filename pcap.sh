# Utility script to capture TCP packet information for a given container
# packet capture data can then be evaluated using a tool like wireshark to
# gain insight into low-level network traffic between services for security
# or performance improvements
docker run --tty --net=container:cumulus-api-packager-1 -v $PWD/_volumes/tcpdump:/tcpdump kaazing/tcpdump -v -i any -w /tcpdump/packager_vsi_chunk_20000000.pcap

# Run network_emulator.py
Please use the following scripts:
```console
./run.sh network_emulator <Forward receiving port> <Receiver's network address> <Reciever’s receiving UDP port number> <Backward receiving port> <Sender's network address> <Sender's receiving UDP port number> <Maximum Delay> <drop probability> <verbose>
```
For example:
```console
./run.sh network_emulator 9991 host2 9994 9993 host3 9992 1 0.2 0
```

# Run sender.py
Please use the following scripts:
```console
./run.sh sender "ne_host" "ne_port" "port" "timeout" "filename"
```
For example:
```console
./run.sh sender host1 9991 9992 50 <input file>
```

# Run receiver.py
Please use the following scripts:
```console
./run.sh receiver "ne_addr" "ne_port" "recv_port" "dest_filename"
```
For example:
```console
./run.sh receiver host1 9993 9994 <output file>
```


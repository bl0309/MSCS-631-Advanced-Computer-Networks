# Python Lab 4: ICMP Ping Client

## Run

Raw ICMP sockets usually require administrator privileges on macOS and Linux.

```bash
cd Python_Lab_4
sudo python3 ICMPPingClient.py
```

The default targets are on four different continents:

- `google.com`: North America
- `bbc.co.uk`: Europe
- `u-tokyo.ac.jp`: Asia
- `abc.net.au`: Australia

You can also provide your own hosts:

```bash
sudo python3 ICMPPingClient.py google.com bbc.co.uk u-tokyo.ac.jp abc.net.au
```

## Files

- `ICMPPingClient.py`: completed raw-socket ICMP ping client.
- `experience.txt`: two-paragraph reflection for the lab submission.
- `icmp-pinger-four-hosts-output.png`: screenshot showing pinger output for four target hosts on different continents.

## Expected Result

The client sends ICMP Echo Request packets and waits for ICMP Echo Reply packets. For each reply, it prints the number of bytes, source IP address, ICMP sequence number, TTL, and round-trip time. At the end of each target, it prints transmitted packets, received packets, packet loss, and min/avg/max round-trip time.

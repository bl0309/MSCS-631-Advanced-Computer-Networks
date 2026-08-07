# Python Lab 6: ICMP Traceroute

## Run

Raw ICMP sockets usually require administrator privileges on macOS and Linux.

```bash
cd Python_Lab_6
sudo python3 ICMPTraceroute.py
```

The default targets are:

- `google.com`
- `bbc.co.uk`
- `www.yahoo.co.jp`
- `abc.net.au`

You can also provide your own four hosts:

```bash
sudo python3 ICMPTraceroute.py google.com bbc.co.uk www.yahoo.co.jp abc.net.au
```

## Files

- `ICMPTraceroute.py`: completed raw-socket ICMP traceroute client.
- `experience.txt`: two-paragraph reflection for the lab submission.
- `traceroute-output-four-targets.png`: screenshot showing traceroute output for the target hosts.

## Expected Result

The client sends ICMP Echo Request packets with increasing TTL values. Routers along the path return ICMP Time Exceeded replies, and the destination returns an ICMP Echo Reply. The output prints each hop number, router IP address or hostname, and round-trip times for each probe.

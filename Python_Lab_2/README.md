# Python Lab 2: UDP Pinger

## Run

Start the UDP server first:

```bash
python3 UDPPingerServer.py
```

In a second terminal, run the client:

```bash
python3 UDPPingerClient.py
```

## Files

- `UDPPingerServer.py`: UDP ping server used for testing.
- `UDPPingerClient.py`: completed UDP ping client.
- `client-screenshot.png`: screenshot-style artifact of the client output.

## Expected Result

The client sends 10 UDP ping messages. Some receive replies with RTT values, and some show `Request timed out` because the server intentionally simulates packet loss.

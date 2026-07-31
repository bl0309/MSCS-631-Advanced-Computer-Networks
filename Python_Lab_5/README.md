# Python Lab 5: HTTP Web Proxy Server

## Run

Start the proxy server:

```bash
cd Python_Lab_5
python3 ProxyServer.py 8888
```

Use a browser or `curl` through the proxy:

```bash
curl -x http://localhost:8888 http://example.com/
```

To test browser access, configure the browser's HTTP proxy to:

```text
Host: localhost
Port: 8888
```

Then open an HTTP URL such as:

```text
http://example.com/
```

The first request should print `Cache miss`, and a repeated request for the same URL should print `Cache hit`.

## Files

- `ProxyServer.py`: completed caching HTTP proxy server.
- `experience.txt`: two-paragraph reflection for the lab submission.
- `proxy-curl-cache-output.png`: screenshot showing the client receiving `http://example.com/` through the proxy and the proxy terminal showing cache hits.

## Notes

This lab proxy handles normal HTTP traffic, not HTTPS traffic. Use URLs that start with `http://` for testing.

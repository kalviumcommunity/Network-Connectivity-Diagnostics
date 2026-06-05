# DNS Simulator Notes

This lab uses a broken resolver configuration to simulate a DNS outage for `api.weather.example`.

## Broken state

The file `dns/broken-resolv.conf` contains:

```text
nameserver 10.255.255.1
search example
```

This nameserver is unreachable, so `dig api.weather.example` will fail even though the application is configured correctly.

## Fix guidance

To restore DNS resolution, replace `/etc/resolv.conf` with a valid resolver entry such as:

```text
nameserver 1.1.1.1
search example
```

Then verify with:

```bash
dig api.weather.example
```

A correct DNS resolution should show `status: NOERROR` and a valid A record.

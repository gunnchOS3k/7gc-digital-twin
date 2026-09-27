# Graham Land Scenario Card

| Attribute | Detail |
|-----------|--------|
| **Node** | Graham Land |
| **Research purpose** | Extreme connectivity — satellite-only, polar conditions, minimal infrastructure |
| **Connectivity stress case** | Polar: LEO satellite windows only, extreme cold, limited power, no terrestrial backup |
| **Primary device workload** | Edge IO (environmental monitoring), Student 14.5" (researcher workstation) |
| **Expected network conditions** | LEO satellite passes only; high latency; intermittent availability; store-and-forward |
| **Digital-twin variables** | Satellite orbit/visibility, weather, temperature, power generation capacity |
| **Data sources** | Published satellite constellation data (Starlink/OneWeb/Iridium orbital parameters) |
| **Ethics risks** | Low for pure simulation; partner-gated for any real deployment |
| **Partner/permission status** | No partners; no field access; simulation-only |
| **What is simulated** | NTN-only operation, delay-tolerant networking, satellite pass scheduling |
| **What is measured** | Data delivery latency, availability windows, energy per transmission, cache hit rates |
| **What is not claimed** | Antarctic access, research station partnerships, field deployment |
| **Current status** | Prototype-pending — simulation-only; partner-gated |
| **Remaining work** | Document satellite pass models; define DTN simulation parameters |

# Use case — current

Actors: researcher, independent reproducer, maintainer. This repo does **not** operate a community network.

```mermaid
flowchart LR
  subgraph actors
    R[Researcher]
    I[Independent reproducer]
    M[Maintainer]
  end
  subgraph twin [7gc-digital-twin]
    UC1[Validate site YAML]
    UC2[Build synthetic scene]
    UC3[Run RQ1 experiment manifest]
    UC4[Emit workload/compute/radio/failure/mobility metrics]
    UC5[Map sibling-repo contracts]
    UC6[Optional Edge-IO ingest]
  end
  R --> UC1
  R --> UC2
  R --> UC3
  R --> UC4
  R --> UC5
  I --> UC1
  I --> UC3
  M --> UC5
  M --> UC6
```

Gary is the only flagship scenario. Other 7GC names are scenario environments.

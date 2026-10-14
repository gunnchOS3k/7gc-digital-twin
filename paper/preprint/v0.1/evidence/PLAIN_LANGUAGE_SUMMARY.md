# When a connection fails, can the task continue?

A phone can lose its internet connection while still opening a downloaded note. A connected laptop can fail to finish a job. These examples explain why this paper distinguishes a connection from useful service. The paper asks what a small service-continuity benchmark actually establishes when its stored labels and generated numbers are checked closely.

## How the evidence was produced

The study has two separate parts. First, 21 stored examples describe four device profiles and their declared ability to handle workloads offline. Eight offline examples retain a declared useful workload; an unsupported wearable coding request fails. These are authored examples, not tests on physical devices. A scenario called degraded Wi-Fi still stores a connected state, so the current classifier calls it target service. That exposes a coverage weakness rather than proof that weak Wi-Fi is harmless.

Second, a seeded generator creates 48 abstract steps for each of four synthetic device classes. Thirty seeds give 30 overall results. Useful state is drawn from configured probabilities; successful task state is drawn only when useful state exists. The average generated task-completion fraction is about 42.7%, while the average useful-state fraction is about 59.1%. The confidence intervals describe uncertainty in the mean of this generator, not a population of real users, laptops or neighborhoods. The better edge-node result follows its more favorable configured priors; it does not establish a hardware ranking.

## A worked reading example

Suppose an offline profile declares that it can open a saved document. The classifier assigns minimum useful service. If it declares no ability to do the requested job, it assigns failed. If its stored state is connected, the classifier assigns target without testing whether the application works. A careful reader can now explain both the rule and the limit. The correct question is whether the required task succeeds under the required conditions.

## What remains uncertain

No application completion, packet traffic, RF channel, battery behavior, recovery time or human experience was measured. Several reported metrics are the same quantity with different names or scaling. For example, the reliability field is exactly useful occupancy, and packet-loss proxy is its complement. They are not independent findings. A recovery-event counter records entry into an outage, not successful recovery. Those details matter when a dashboard has many impressive-looking columns.

Read the manuscript with SCIENTIFIC_REVIEW.md, DATA_DICTIONARY.md and REPRODUCIBILITY.md. The author must still review accuracy, originality and rights before deciding whether to release the exploratory preprint.

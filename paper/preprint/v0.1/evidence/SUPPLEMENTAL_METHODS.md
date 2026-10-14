# Paper I methods and worked calculations

For a stored state o and offline capability F, the classifier returns target for connected, degraded for degraded/transitioning, minimum useful for offline with F=true, and failed otherwise. Offline local creation with support therefore passes; offline unsupported coding fails; a connected snapshot passes without application checks. This last branch is an explicit coverage limitation.

For stochastic class c let a be useful-state base probability, q task base probability, h stress sensitivity and b=.35h. Draw S uniform on [0,1]. Useful probability is a(1-bS); conditional task probability is q(1-.2S). Their expected fractions are:

```text
E[tau] = a*(1-b/2)
E[C] = a*q*(1-(b+.2)/2+.2*b/3)
```

The product integrates `(1-b*S)*(1-.2*S)`; the cross-term uses E[S²]=1/3. For the smartphone prior a=.72,q=.78,h=1, expected tau=.594 and C=.420264. The expected class ordering is already encoded by these authored priors. It is not an observed hardware ranking. Demand affects an energy proxy and does not change the useful or task indicators.

For each seed average 48 steps within a class, then weight four classes equally. Across 30 stored seed means use sample SD (ddof=1) and t(.975,29)=2.0452296421. Completion mean .4272570333, SD .0416101842, interval [.4117195352,.4427945314]. Useful mean .5914930667, SD .0402434247, interval [.5764659249,.6065202084]. These post-hoc independent checks preserve historical rounding. Counting 5,760 class-steps as 5,760 independent field observations would be incorrect.

A connected-only semantic comparison changes all nine offline snapshots to failed. The corpus classifier instead preserves eight declared supported workloads. This comparison assesses label semantics, without executing a fallback controller or assigning a measured benefit. A future controller study needs workload completion/deadline definitions, equal action/information access, resource state, physical calibration and a new frozen protocol. None of that future evidence is inserted into the present result.

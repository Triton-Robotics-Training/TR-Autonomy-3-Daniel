# Part 2 observations

The error is the detected position minus the nearest ground-truth panel position,
in the `map` frame. Values are in meters. These are short, single-run observations,
not a complete accuracy evaluation. The test sent simulated teleop commands
directly to the secondary robot.

| Condition | Wall-clock duration | Error samples | x range (m) | y range (m) | z range (m) |
| --- | ---: | ---: | --- | --- | --- |
| Stationary target | 25 s | 8 | 0.160 to 0.212 | -0.063 to -0.027 | 0.014 to 0.020 |
| Target spinning at 1.125 rad/s | 30 s | 8 | 0.038 to 0.184 | -0.036 to 0.064 | 0.016 to 0.031 |
| Target moving at 0.6 m/s | 30 s | 11 | -0.044 to 0.148 | -0.110 to 0.110 | -0.007 to 0.030 |

The signed x and y errors changed more during these short motion trials than in
the stationary trial. The z error stayed closer to zero in these samples. The
sample sizes are small, and delayed processing can shift samples across condition
boundaries, so the table does not establish a general motion effect.

The simulated clock advanced about 0.75 seconds during each 30-second motion
trial. The VM was running at about 2.5% of real time, and detections were sparse.
The Plot panel connects samples with lines, so a line across a gap does not mean
the detector produced measurements throughout that gap.

The x error changed by about 0.19 m across the moving trial. This short run did
not reproduce the large x-error jump shown in the assignment. The nearest-panel
rule can change which panel is compared, but this run did not record panel IDs,
so it does not establish whether any observed jump came from a panel switch.

The calculator only queues messages containing a detection. An automated check
confirmed that an empty detection does not queue a measurement or publish an
error. The test also checked nearest-panel selection and common lookup timestamps.

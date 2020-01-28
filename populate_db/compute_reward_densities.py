import numpy as np
from scipy.stats import truncnorm

dmean   = 20
mean1   = 50 - dmean/2.
mean2   = 50 + dmean/2.
epsilon = 0.02

def generate_rewards(sd=15, nb_samples=int(1e5), verbose = 0):

	myclip_a = 1
	myclip_b = 99
	a1, b1   = (myclip_a - mean1) / sd, (myclip_b - mean1) / sd
	a2, b2   = (myclip_a - mean2) / sd, (myclip_b - mean2) / sd
	assert(sd in [10, 15, 20, 25]), 'standard deviation must be in [10, 15, 20, 25]'
	bound    = (sd==10) * 0.08 +  (sd == 20) * 0.25 + (sd == 25) * 0.3 + (sd == 15) * 0.17

	while True:
		sampleslow  = np.array(truncnorm.rvs(a1, b1, loc=mean1, scale=sd, size=nb_samples), dtype=np.int)
		sampleshigh = np.array(truncnorm.rvs(a2, b2, loc=mean2, scale=sd, size=nb_samples), dtype=np.int)
		if np.abs((sampleslow > sampleshigh).mean() - bound) < epsilon and np.abs(np.std(sampleshigh) - sd) < 1 and np.abs(np.std(sampleslow) - sd) < 1 and np.abs(sampleslow.mean() - mean1) < 2 and np.abs(sampleshigh.mean() - mean2) < 2:
			break

	if verbose:
		from matplotlib import pyplot as plt
		print((sampleslow > sampleshigh).mean())
		plt.figure()
		x_range = np.arange(0, 100, 0.1)
		plt.plot(x_range, truncnorm.pdf(x_range, a1, b1, loc=mean1, scale=sd))
		plt.plot(x_range, truncnorm.pdf(x_range, a2, b2, loc=mean2, scale=sd))
		plt.plot(x_range, .5 * truncnorm.pdf(x_range, a2, b2, loc=mean2, scale=sd) + .5 * truncnorm.pdf(x_range, a1, b1, loc=mean1, scale=sd))

	return sampleslow, sampleshigh


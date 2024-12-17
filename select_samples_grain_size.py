import numpy as np
from scipy.ndimage import center_of_mass
from enum import Enum

class GrainSizeSetting(str, Enum):
	HIGHEST = "highest"
	LOWEST = "lowest"


def select_samples_grain_size(mask: np.ndarray, no_of_bins: int, num_samples: int = 1, setting: GrainSizeSetting = GrainSizeSetting.HIGHEST)) -> list[list[int]]:
    # Find the sizes of the different particles
    sizes = np.zeros(np.max(mask)+1)

    for bin_num in range(np.max(mask)+1):
        sizes[bin_num] = np.count_nonzero(mask==bin_num)

    # Remove the zeroth element (the background)
    sizes_new = sizes[1:]

    # Bin these clusters by size
    hist = np.histogram(sizes_new, no_of_bins=no_of_bins)
    bin_boundaries = hist[1]

    # Find the corresponding indices
    size_args: list[list[int]] = []

    for bin_num in range(no_of_bins):
        bounds = (bin_boundaries[bin_num], bin_boundaries[bin_num+1])
        bool_arr = np.array([sizes_new>=bounds[0], sizes_new<bounds[1]])
        size_args.append(list(np.argwhere(bool_arr.all(0)).T[0]))

    # Take samples from each bin
    sample_list: list[list[int]] = []

    for bin_num in range(no_of_bins):
        #print(bin_num)
        if len(size_args[bin_num])>num_samples:
            sample_list.append(list(np.random.choice(size_args[bin_num], size=num_samples, replace=False)))
        else:
            sample_list.append(size_args[bin_num])

    # Find the pixel co-ordinates of these samples
    coords = []

    if setting == GrainSizeSetting.HIGHEST:
        bin_num = 0
    elif setting == GrainSizeSetting.LOWEST:
        bin_num = no_of_bins-1
       
    sl = sample_list[bin_num]

    coord_ii = []
    for sample_num in range(len(sl)):
        mask_ii = mask==(bin_num+1)
        coord_ii.append(center_of_mass(mask_ii))
    coords.append(coord_ii)

    

    return coords
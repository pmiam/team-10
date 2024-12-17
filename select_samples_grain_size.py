import numpy as np
from scipy.ndimage import center_of_mass


def select_samples_grain_size(mask, bins, num_samples=1, setting='highest'):
    # Find the sizes of the different particles
    sizes = np.zeros(np.max(mask)+1)

    for ii in range(np.max(mask)+1):
        sizes[ii] = np.count_nonzero(mask==ii)

    # Remove the zeroth element (the background)
    sizes_new = sizes[1:]

    # Bin these clusters by size
    hist = np.histogram(sizes_new, bins=bins)
    bin_boundaries = hist[1]

    # Find the corresponding indices
    size_args = []

    for ii in range(bins):
        bounds = (bin_boundaries[ii], bin_boundaries[ii+1])
        bool_arr = np.array([sizes_new>=bounds[0], sizes_new<bounds[1]])
        size_args.append(list(np.argwhere(bool_arr.all(0)).T[0]))

    # Take samples from each bin
    sample_list = []

    for ii in range(bins):
        #print(ii)
        if len(size_args[ii])>num_samples:
            sample_list.append(list(np.random.choice(size_args[ii], size=num_samples, replace=False)))
        else:
            sample_list.append(size_args[ii])

    # Find the pixel co-ordinates of these samples
    coords = []

    if setting == 'highest':
        ii = 0
    if setting == 'lowest':
        ii = bins-1
       
    sl = sample_list[ii]

    coord_ii = []
    for jj in range(len(sl)):
        mask_ii = mask==(ii+1)
        coord_ii.append(center_of_mass(mask_ii))
    coords.append(coord_ii)

    

    return coords
import numpy as np
from scipy.stats import norm  
from scipy.ndimage import gaussian_filter                           

def intensity_normalization(struct_img, scaling_param):

    '''
    Mode 1:  scaling_param = [0]
    Mode 2:  scaling_param = [lower std range, upper std range]
    Mode 3:  scaling_param = [lower std range, upper std range, lower abs intensity, higher abs intensity]
    '''
    assert len(scaling_param)>0

    if len(scaling_param)==1:
        print('intensity normalization: using min-max normalization')
        strech_min = struct_img.min()
        strech_max = struct_img.max()
        struct_img = (struct_img - strech_min + 1e-8)/(strech_max - strech_min + 1e-8)
    elif len(scaling_param)==2:
        print(f'intensity normalization: normalize into [mean - {scaling_param[0]} x std, mean + {scaling_param[1]} x std] ')
        m,s = norm.fit(struct_img.flat)
        strech_min = max(m - scaling_param[0]*s, struct_img.min())
        strech_max = min(m + scaling_param[1] *s, struct_img.max())
        struct_img[struct_img>strech_max]=strech_max
        struct_img[struct_img<strech_min]=strech_min
        struct_img = (struct_img- strech_min + 1e-8)/(strech_max - strech_min + 1e-8)
    elif len(scaling_param)==4:
        img_valid = struct_img[np.logical_and(struct_img>scaling_param[2],\
            struct_img<scaling_param[3])]
        m,s = norm.fit(img_valid.flat)
        strech_min = max(scaling_param[2] - scaling_param[0]*s, struct_img.min())
        strech_max = min(scaling_param[3] + scaling_param[1] *s, struct_img.max())
        struct_img[struct_img>strech_max]=strech_max
        struct_img[struct_img<strech_min]=strech_min
        struct_img = (struct_img- strech_min + 1e-8)/(strech_max - strech_min + 1e-8)
   
    print('intensity normalization completes')
    return struct_img

def image_smoothing_gaussian_3d(struct_img, sigma, truncate_range=3.0):

    structure_img_smooth = gaussian_filter(struct_img, sigma=sigma, mode='nearest', truncate=truncate_range)

    return structure_img_smooth

def image_smoothing_gaussian_slice_by_slice(struct_img, sigma, truncate_range=3.0):

    structure_img_smooth = np.zeros_like(struct_img)
    for zz in range(struct_img.shape[0]):
        structure_img_smooth[zz,:,:] = gaussian_filter(struct_img[zz,:,:], sigma=sigma, mode='nearest', truncate=truncate_range)

    return structure_img_smooth

def suggest_normalization_param(structure_img0):
    m, s = norm.fit(structure_img0.flat)
    print(m)
    print(s)

    p99 = np.percentile(structure_img0, 99.99)
    print(p99)

    pmin = structure_img0.min()
    print(pmin)

    pmax = structure_img0.max()
    print(pmax)

    up_ratio = 0 
    for up_i in np.arange(0.5, 1000, 0.5):
        if m+s*up_i > p99:
            if m+s*up_i>pmax:
                print(f'suggested upper range is {up_i-0.5}, which is {m+s*(up_i-0.5)}')
                up_ratio = up_i-0.5
            else:
                print(f'suggested upper range is {up_i}, which is {m+s*up_i}')
                up_ratio = up_i
            break

    low_ratio =0
    for low_i in np.arange(0.5, 1000, 0.5):
        if m-s*low_i < pmin:
            print(f'suggested upper range is {low_i-0.5}, which is {m-s*(low_i-0.5)}')
            low_ratio = low_i-0.5
            break

    print(f'So, suggested parameter for normalization is [{low_ratio}, {up_ratio}]')
    print('You may also increase the first value (may loss some dim parts), or decrease the second value (may loss some texture in super bright regions) to further enhance the contrast')
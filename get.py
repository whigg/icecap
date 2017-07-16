import glob
import icecap as icp
import numpy as np
import os
import string
import fnmatch
import subradar as sr


def params():
    """get various parameters defining the season
    """
    out = {'code_path':os.getcwd()}
    out['season'] = out['code_path'].split('/')[-3]
    out['process'] = out['code_path'].split('/')[-1]
    out['root_path'] = string.join(out['code_path'].split('/')[0:-5], '/')
    out['norm_path'] = out['root_path'] + '/targ/norm'
    out['rsr_path'] = string.replace(out['code_path'], 'code', 'targ')
    out['cmp_path'] = string.replace(out['rsr_path'], 'RSR', 'CMP')
    out['pik_path'] = out['root_path'] + '/orig/xtra/'+out['season']+'/PIK/' + out['process']
    out['foc_path'] = out['root_path'] + '/targ/xtra/' + out['season']+ '/FOC/Best_Versions/S1_POS'
    out['season_flight_pst'] = out['root_path'] + '/syst/linux/lib/dbase/season_flight_pst'
    return out


def pik(pst, process=None, **kwargs):
    """Get available PIK files for a PST
    """
    p = icp.get.params()
    if process is None:
        process = p['process']
    folder = string.join([string.replace(p['pik_path'],'/'+p['process'],''), process, pst], '/')
    files = glob.glob(folder + '/*.*')
    names = [string.split(i, '/')[-1] for i in files]
    products = [string.split(i, '.')[0] for i in names]
    pik = [string.split(i, '.')[1] for i in names]

    return products, pik


def cmp(pst, process=None, **kwargs):
    """Get available radar data in CMP for a PST
    """
    p = icp.get.params()
    if process is None:
        process = p['process']
    folder = string.join([string.replace(p['cmp_path'],'/'+p['process'],''), process, pst], '/')
    files = glob.glob(folder + '/*[!.meta]')
    products = [string.split(i, '/')[-1] for i in files]
    return products


def pst(pattern, **kwargs):
    """Get PSTs for the current season that match a given pattern (regex)
    """
    p = icp.get.params()
    data = np.genfromtxt(p['season_flight_pst'], delimiter=' ', dtype='string')
    i = np.where(data[:,2] == p['season'])
    pst = data[i,0]
    return fnmatch.filter(pst.flatten(), pattern)


def flight(pst, **kwargs):
    """Get Flight for a PST
    """
    p = icp.get.params()
    data = np.genfromtxt(p['season_flight_pst'], delimiter=' ', dtype='string')
    i = np.where(data[:,0] == pst)
    return data[i,:].flatten()[1]


def surface_range(pst):
    """Range to surface interpolated alon the foc_time
    """
    p = icp.get.params()
    t, val = icp.read.norm(pst, 'LAS', 'las_rng', interp=True)
    tref = icp.read.ztim(p['foc_path']+'/'+pst+'/ztim_DNhH')['htim']
    return np.interp(tref, t, val)


def longitude(pst):
    p = icp.get.params()
    t, val = icp.read.norm(pst, 'AVN', 'lon_ang', interp=True)
    tref = icp.read.ztim(p['foc_path']+'/'+pst+'/ztim_DNhH')['htim']
    return np.interp(tref, t, val)


def latitude(pst):
    p = icp.get.params()
    t, val = icp.read.norm(pst, 'AVN', 'lat_ang', interp=True)
    tref = icp.read.ztim(p['foc_path']+'/'+pst+'/ztim_DNhH')['htim']
    return np.interp(tref, t, val)


def roll(pst):
    p = icp.get.params()
    t, val = icp.read.norm(pst, 'AVN', 'roll_ang', interp=True)
    tref = icp.read.ztim(p['foc_path']+'/'+pst+'/ztim_DNhH')['htim']
    return np.interp(tref, t, val)


def signal(pst, pik, scale=1/1000., calib=True, air_loss=True, gain=0, **kwargs):
    """Extract signal from a pik file and apply various corrections
    """
    y, val = icp.read.pik(pst, pik, **kwargs)

    h = icp.get.surface_range(pst)
    # Pad the end of piks with nans to equal regular data length
    val = np.pad(val.astype(float), (0,np.size(h)-np.size(val)), 
                 'constant', constant_values=np.nan)

    val = val*scale

    if calib is True:
        calval = 0.
        val = val +calval

    if air_loss is True:
        L = 10*np.log10( sr.utils.geo_loss(2*h) )
        gain = gain-L
    
    return val + gain


def Rsc(pst, pik, **kwargs):
    pass


def Rsn(pst, pik, **kwargs):
    pass
import numpy as np
import sys
import neo
from neo.io.nixio import NixIO
from neo.core import (
    SpikeTrain)
from quantities import uV, Hz, ms, s
from tqdm import tqdm
import h5py
import pandas as pd


def get_circus_auto_result_DF(result_base, merged=True, fs=20000*Hz):
    """
    Returns a dataframe of the automatic SpykingCircus results (i.e., before changes made in GUI)

    Parameters
    ----------
    result_base: string
        A formattable string containing the file directory and prefix, with placeholder for the specific file
        e.g.,  "D:\Odor quality\1-17-20\1-17-20___slice3_merged\1-17-20___slice3_mergedtimes.{file}.hdf5"
    merged: boolean
        If true, accesses meta-merged results (in "file-merged.hdf5"); if false, accesses main results ("file.hdf5")
    fs: quantity
        Sampling rate
        e.g., 20000*Hz

    Returns
    ----------
    circus_df: Pandas dataframe
        Dataframe containing the SpykingCircus results. Each row is an individual cluster, with spikes in the "Data"
        column.
    """

    period = (1./fs).rescale(ms)

    if merged:
        results_filename = result_base.format(file='result-merged')
        clusters_filename = result_base.format(file='clusters-merged')
    else:
        results_filename = result_base.format(file='result')
        clusters_filename = result_base.format(file='clusters')

    results_file = h5py.File(results_filename, 'r')
    clusters_file = h5py.File(clusters_filename, 'r')
    electrodes = np.array(clusters_file.get('electrodes'))
    circus_df = pd.DataFrame({"ID": range(len(electrodes)), "Electrode": electrodes, "Data": np.nan})
    circus_df = circus_df.astype(object)

    pbar = tqdm(total=len(circus_df["ID"]), file=sys.stdout, desc="Getting SpykingCircus results")
    for id_ in circus_df["ID"]:
        print("AAAA")
        print(circus_df["ID"])
        temp_id = "temp_" + str(id_)
        id_st = list(results_file["spiketimes"][temp_id])
        id_st = [period * sample for sample in id_st]
        id_st = np.array(id_st)
        id_st.reshape(id_st.shape[0],)
        print(id_st)
        print(len(id_st))
        circus_df.loc[id_, 'Data'] = id_st
        pbar.update(1)
    pbar.close()

    return circus_df


def get_circus_manual_result_DF(gui_base, get_electrodes=True, get_groups=True, fs=20000*Hz):
    """
    Returns a dataframe of manually-sorted SpykingCircus results (i.e., w/ changes made in GUI)

    Parameters
    ----------
    gui_base: string
        A formattable string containing the GUI file directory, with placeholders for the specific file and extension
        e.g.,  "D:\Odor quality\1-17-20\1-17-20___slice3_merged\1-17-20___slice3_mergedtimes.GUI\{file}.{ext}"
    get_electrodes: boolean
        If true, dataframe will contain "Electrode" column with electrode IDs
    get_groups: boolean
        If true, dataframe will contain "Group" column with manually-sorted groups (e.g., "noise", "good")
    fs: quantity
        Sampling rate
        e.g., 20000*Hz

    Returns
    ----------
    circus_df: Pandas dataframe
        Dataframe containing the SpykingCircus results. Each row is an individual cluster, with spikes in the "Data"
        column.
    """
    period = (1./fs).rescale(ms)
    times = np.load(gui_base.format(file="spike_times", ext="npy"))
    clusters = np.load(gui_base.format(file="spike_clusters", ext="npy"))
    cluster_ids = np.unique(clusters)

    if get_electrodes:
        clusters_h5 = gui_base.split('.')[0] + ".clusters.hdf5"
        clusters_h5 = h5py.File(clusters_h5, 'r')
        electrodes = list(clusters_h5.get('electrodes'))

    circus_df = pd.DataFrame({"ID": cluster_ids, "Electrode": np.nan, "Group":np.nan, "Data": np.nan})
    circus_df = circus_df.astype(object)
    pbar = tqdm(circus_df.iterrows(), total=circus_df.shape[0], file=sys.stdout, desc="Getting SpykingCircus results")

    i = 0
    for index, cluster in pbar:
        id_ = cluster["ID"]
        cluster_indices = np.where(clusters == id_)
        id_st = times[cluster_indices]
        id_st = [period * x for x in id_st]
        id_st = np.array(id_st)
        id_st.reshape(id_st.shape[0], )
        cluster["Data"] = id_st

        if get_electrodes:
            channel_map = np.load(gui_base.format(file="channel_map", ext="npy"))
            if id_ in range(0, len(electrodes)):
                electrode_index = electrodes[id_]
                cluster["Electrode"] = channel_map[electrode_index]
        i += 1
    pbar.close()

    if get_groups:
        tsv_file = open(gui_base.format(file="cluster_group", ext="tsv"))
        group_df = pd.read_csv(tsv_file, sep='\t')

        for _, group in group_df.iterrows():
            id = group["cluster_id"]
            group = group["group"]
            circus_df.loc[circus_df['ID'] == id, 'Group'] = group
    return circus_df


def get_spikes_by_cluster(gui_base, cluster_num, fs, t_stop):
    """
    Returns a single cluster as a SpikeTrain object

    Parameters
    ----------
    gui_base: string
        A formattable string containing the GUI file directory, with placeholders for the specific file and extension
        e.g.,  "D:\Odor quality\1-17-20\1-17-20___slice3_merged\1-17-20___slice3_mergedtimes.GUI\{file}.{ext}"
    cluster_num: int
        Number of the desired cluster
    fs: quantity
        Sampling rate
        e.g., 20000*Hz
    t_stop: quantity
        Stop time (required by Neo for Spiketrain object)
        e.g., 60*s
    Returns
    ----------
    spikes_converted: Neo SpikeTrain object
        A SpikeTrain object corresponding to a given cluster
    """
    period = (1./fs).rescale(ms)
    times = np.load(gui_base.format(file="spike_times", ext="npy"))
    clusters = np.load(gui_base.format(file="spike_clusters", ext="npy"))
    cluster_indices = np.where(clusters == cluster_num)
    spikes = times[cluster_indices]
    spikes_converted = [period * x for x in spikes]
    spikes_converted = np.array(spikes_converted)
    spikes_converted.reshape(spikes_converted.shape[0], )
    spikes_converted = SpikeTrain(spikes_converted*ms, t_stop)
    return spikes_converted


if __name__ == "__main__":

    # Example - my SpykingCircus results are in a directory "D:\Odor quality\1-17-20\1-17-20___slice3_merged", which
    # contains lots of files, as well as another folder "1-17-20___slice3_mergedtimes.GUI"
    # Change the names to fit the directory on your comp

    date = "1-17-20"
    slice = 3
    fs = 20000*Hz
    t_stop = 60*s  # t_stop = the duration, or last time point. You may set it manually, or read from your file

    # Access automatic results w/ get_circus_auto_result_DF()
    result_base = r'D:\\Odor quality\\' + date + r'\\' + date + '___slice' + str(slice) + r'_merged\\' + date + \
                  '___slice' + str(slice) + r'_mergedtimes.{file}.hdf5'
    # result_base = "D:\Odor quality\1-17-20\1-17-20___slice3_merged\1-17-20___slice3_mergedtimes.{file}.hdf5
    result_base2 = r'S:\Ayaan\Data\Numpy Arrays\Spyking\U1, U2, U3 combined - ParameterTest_OE8_091119_Preinfusion and ParameterTest_OE8_091119_Postinfusion.{file}.hdf5'
    get_circus_auto_result_DF(result_base2, fs=fs)


    # Access manual/GUI results w/ get_circus_manual_result_DF()
    slice_folder = date + '___slice' + str(slice) + '_merged'
    # slice_folder = "1-17-20___slice3_merged"
    gui_folder = slice_folder + r'\\' + slice_folder + 'times.GUI'
    # gui_folder = "1-17-20___slice3_merged\1-17-20___slice3_mergedtimes.GUI"
    gui_base = r'D:\\Odor quality\\' + date + r'\\' + gui_folder + "\{file}.{ext}"
    # gui_base = "D:\Odor quality\1-17-20\1-17-20___slice3_merged\1-17-20___slice3_mergedtimes.GUI\{file}.{ext}"
    sc_df = get_circus_manual_result_DF(gui_base, get_electrodes=False, get_groups=True, fs=fs)

    # Iterate through dataframes to get each individual cluster
    sts = sc_df["Data"].tolist()
    clusters = sc_df["ID"].tolist()
    for i, st in enumerate(sts):
        st_id = clusters[i]
        st = neo.SpikeTrain(st, t_stop=t_stop, units=ms)
        # Do something with st

    # Or access an individual cluster on its own w/ get_spikes_by_cluster
    st1 = get_spikes_by_cluster(gui_base, 1, fs, t_stop)


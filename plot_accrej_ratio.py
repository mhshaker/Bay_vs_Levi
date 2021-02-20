import sys
import mysql.connector as db
import os
import math
import numpy as np
import matplotlib.pyplot as plt
import UncertaintyM as unc
import warnings

base_dir = os.path.dirname(os.path.realpath(__file__))
pic_dir = f"{base_dir}/pic/unc"
if not os.path.exists(pic_dir):
    os.makedirs(pic_dir)

unc_value_plot = False
local = True
color_correct = False
vertical_plot = True

# data_list  = ["parkinsons","vertebral","breast","climate", "ionosphere", "blod", "bank", "QSAR", "spambase", "wine_qw"] 
# data_list = ["breast", "climate", "ionosphere", "spambase"]
data_list = ["parkinsons"]
modes     = "eat"

for data in data_list:
    
    # prameters ############################################################################################################################################

    run_name  = "ens_size_UAI" # "ens_size_UAI"
    plot_name = "RenslGH-" + data # "RensEnt-" + data 
    # query       = f"SELECT results, id , prams, result_type FROM experiments Where task='unc' AND dataset='Jdata/{data}' AND run_name='{run_name}'"
    query1       = f"SELECT results, id , prams, result_type FROM experiments Where task='unc' AND dataset='Jdata/{data}' AND run_name='{run_name}' AND result_type='bays'"
    query2       = f"SELECT results, id , prams, result_type FROM experiments Where task='unc' AND dataset='Jdata/{data}' AND run_name='{run_name}' AND result_type='levi.GH'"


    ########################################################################################################################################################
    xlabel      = "Rejection %"
    ylabel      = "Ratio"

    plot_value1 = []
    legend_value1 = []

    if vertical_plot:
        fig, axs = plt.subplots(len(modes),1)
        fig.set_figheight(15)
        fig.set_figwidth(5)
    else:
        fig, axs = plt.subplots(1,len(modes))
        fig.set_figheight(4)
        fig.set_figwidth(15)

    # get input from command line
    mydb = db.connect(host="131.234.250.119", user="root", passwd="uncertainty", database="uncertainty")
    mycursor = mydb.cursor()
    mycursor.execute(query1) # run_name ='uni_exp'
    results = list(mycursor.fetchall())
    jobs = []
    for job in results:
        jobs.append(job)

    plot_list = []
    legend_list = []

    for job in jobs:
        dir = job[0]
        if dir[0] == ".":
            dir = base_dir + dir[1:]
        if local:
            dir = f"/home/mhshaker/Projects/Database/DB_files/job_{job[1]}"
            isFile = os.path.isdir(dir)
            if not isFile:
                print("[Error] file does not exist")
                print(dir)
                exit()
        plot_list.append(job[1])
        flap = True

        job_plots = []
        job_legends = []
        for mode_index, mode in enumerate(modes):
            # print(f"mode {mode} dir {dir}")
            dir_p = dir + "/p"
            dir_l = dir + "/l"
            dir_mode = dir + "/" + mode

            legend = ""

            # prams = str(job[2])
            # pram_name = "n_estimators"
            # search_pram = f"'{pram_name}': "
            # v_index_s = prams.index(search_pram)
            # v_index_e = prams.index(",", v_index_s)
            # max_depth = int(prams[v_index_s+len(search_pram) : v_index_e])
            # legend += "n_estimators: " + str(max_depth)

            for text in job[3:]:
                legend += " " +str(text) 
            # legend += mode   

            # get the list of file names
            file_list = []
            for (dirpath, dirnames, filenames) in os.walk(dir_mode):
                file_list.extend(filenames)


            # read every file and append all to "all_runs"
            all_runs_unc = []
            for f in file_list:
                run_result = np.loadtxt(dir_mode+"/"+f)
                all_runs_unc.append(run_result)

            all_runs_p = []
            for f in file_list:
                run_result = np.loadtxt(dir_p+"/"+f)
                all_runs_p.append(run_result)

            all_runs_l = []
            for f in file_list:
                run_result = np.loadtxt(dir_l+"/"+f)
                all_runs_l.append(run_result)

            avg_acc, avg_min, avg_max, avg_random , steps = unc.accuracy_rejection(all_runs_p,all_runs_l,all_runs_unc, unc_value_plot)

            # print(">>>>>>>>", avg_acc)
            linestyle = '-'
            if "set" in legend:
                linestyle = '--'
            if "conv" in legend:
                linestyle = ':'

            if color_correct:
                color = "black"
                if "ent" in legend:
                    color = "black"
                if "levi.GH" in legend:
                    color = "blue"
                if "levi.ent" in legend:
                    color = "orange"
                if "gs" in legend:
                    color = "green"
                if "set" in legend:
                    color = "green"
            else:
                color = None

            # legend = legend.replace("set14.convex", "Levi-GH-conv")
            # legend = legend.replace("set15.convex", "Levi-Ent-conv")
            # legend = legend.replace("set14", "Levi-GH")
            # legend = legend.replace("set15", "Levi-Ent")
            # legend = legend.replace("ent", "Bayes")
            legend = legend.replace("gs", "GS")

            # axs[mode_index].plot(steps, avg_acc, linestyle=linestyle, color=color)
            job_plots.append(avg_acc)
            job_legends.append(legend)

            if flap:
                legend_list.append(legend)
                
            if mode == "a":
                mode_title = "AU"
            if mode == "e":
                mode_title = "EU"
            if mode == "t":
                mode_title = "TU"
            axs[mode_index].set_title(mode_title)
            flap =False
        plot_value1.append(job_plots)
        legend_value1.append(job_legends)



    # get input from command line
    mydb = db.connect(host="131.234.250.119", user="root", passwd="uncertainty", database="uncertainty")
    mycursor = mydb.cursor()
    mycursor.execute(query2) # run_name ='uni_exp'
    results = list(mycursor.fetchall())
    jobs = []
    for job in results:
        jobs.append(job)

    plot_list = []
    legend_list = []

    for job, plot_value, legend_value in zip(jobs, plot_value1, legend_value1):
        dir = job[0]
        if dir[0] == ".":
            dir = base_dir + dir[1:]
        if local:
            dir = f"/home/mhshaker/Projects/Database/DB_files/job_{job[1]}"
            isFile = os.path.isdir(dir)
            if not isFile:
                print("[Error] file does not exist")
                print(dir)
                exit()
        plot_list.append(job[1])
        flap = True
        for mode_index, mode in enumerate(modes):
            # print(f"mode {mode} dir {dir}")
            dir_p = dir + "/p"
            dir_l = dir + "/l"
            dir_mode = dir + "/" + mode

            legend = ""

            prams = str(job[2])
            pram_name = "n_estimators"
            search_pram = f"'{pram_name}': "
            v_index_s = prams.index(search_pram)
            v_index_e = prams.index(",", v_index_s)
            max_depth = int(prams[v_index_s+len(search_pram) : v_index_e])
            legend += "#Estimators: " + str(max_depth)

            # prams = str(job[2])
            # pram_name = "credal_size"
            # search_pram = f"'{pram_name}': "
            # v_index_s = prams.index(search_pram)
            # v_index_e = prams.index(",", v_index_s)
            # max_depth = int(prams[v_index_s+len(search_pram) : v_index_e])
            # legend += "credal_size: " + str(max_depth)


            

            # for text in job[3:]:
            #     legend += " " +str(text) 
            # legend += mode   

            # get the list of file names
            file_list = []
            for (dirpath, dirnames, filenames) in os.walk(dir_mode):
                file_list.extend(filenames)


            # read every file and append all to "all_runs"
            all_runs_unc = []
            for f in file_list:
                run_result = np.loadtxt(dir_mode+"/"+f)
                all_runs_unc.append(run_result)

            all_runs_p = []
            for f in file_list:
                run_result = np.loadtxt(dir_p+"/"+f)
                all_runs_p.append(run_result)

            all_runs_l = []
            for f in file_list:
                run_result = np.loadtxt(dir_l+"/"+f)
                all_runs_l.append(run_result)

            avg_acc, avg_min, avg_max, avg_random , steps = unc.accuracy_rejection(all_runs_p,all_runs_l,all_runs_unc, unc_value_plot)

            # print(">>>>>>>>", avg_acc)
            linestyle = '-'
            if "set" in legend:
                linestyle = '--'
            if "conv" in legend:
                linestyle = ':'

            if color_correct:
                color = "black"
                if "ent" in legend:
                    color = "black"
                if "levi.GH" in legend:
                    color = "blue"
                if "levi.ent" in legend:
                    color = "orange"
                if "gs" in legend:
                    color = "green"
                if "set" in legend:
                    color = "green"
            else:
                color = None

            # legend = legend.replace("set14.convex", "Levi-GH-conv")
            # legend = legend.replace("set15.convex", "Levi-Ent-conv")
            # legend = legend.replace("set14", "Levi-GH")
            # legend = legend.replace("set15", "Levi-Ent")
            # legend = legend.replace("ent", "Bayes")
            legend = legend.replace("gs", "GS")

            axs[mode_index].plot(steps, avg_acc/plot_value[mode_index], linestyle=linestyle, color=color)
            # plot_value1.append(avg_acc)
            # legend_value1.append(legend)

            if flap:
                legend_list.append(legend) #+ "/" + legend_value[mode_index])
                
            if mode == "a":
                mode_title = "AU"
            if mode == "e":
                mode_title = "EU"
            if mode == "t":
                mode_title = "TU"
            axs[mode_index].set_title(data + " " + mode_title)
            flap =False



    acc_lable_flag = True
    job_plots_list = list(axs.flat)
    if vertical_plot:
        job_plots_list = reversed(list(axs.flat))
    for ax in job_plots_list:
        if acc_lable_flag:
            ax.set(xlabel=xlabel, ylabel=ylabel)
            # ax.set(xlabel=xlabel)
            acc_lable_flag = False
        else:
            if vertical_plot:
                ax.set(ylabel=ylabel)
                # pass
            else:
                ax.set(xlabel=xlabel)
    title = plot_list
    # fig.suptitle(title)
    # with warnings.catch_warnings():
    #     warnings.simplefilter("ignore", category=RuntimeWarning)
    
    fig.legend(axs,labels=legend_list, loc="lower center", ncol=6)

    fig.savefig(f"./pic/unc/{plot_name}.png",bbox_inches='tight')
    # fig.close()
    print(f"Plot {plot_name} Done")
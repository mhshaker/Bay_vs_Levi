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
local = False
color_correct = True
vertical_plot = False
single_plot = False
legend_flag = False

# data_list  = ["parkinsons","vertebral","breast","climate", "ionosphere", "blod", "bank", "QSAR", "spambase", "iris", "heartdisease"] 
# data_list  = ["vertebral","breast", "ionosphere", "blod", "QSAR", "wine_qw"] 
# data_list = ["climate", "parkinsons", "spambase"]
# data_list = ["climate", "vertebral"]
data_list = ["QSAR"]
modes     = "eat"

for data in data_list:
    
    # prameters ############################################################################################################################################

    run_name  = "DSpaper2"
    plot_name = "/DSpaper/" + data + ""
    query       = f"SELECT results, id , prams, result_type FROM experiments Where task='unc' AND dataset='Jdata/{data}' AND run_name='{run_name}' AND status='done'"
    # query       = f"SELECT results, id , prams, result_type FROM experiments Where task='unc' AND dataset='Jdata/{data}' AND run_name='{run_name}' AND result_type='levi.GH'"
    # query       = f"SELECT results, id , prams, result_type FROM experiments Where task='unc' AND id>=4894"

    ########################################################################################################################################################

    # fix dataset official name
    data = data.replace("parkinsons", "Parkinsons")
    data = data.replace("vertebral", "Vertebral Column")
    data = data.replace("breast", "Breast Cancer Wisconsin (Diagnostic)")
    data = data.replace("climate", "Climate Model Simulation Crashes")
    data = data.replace("ionosphere", "Ionosphere")
    data = data.replace("blod", "Blood Transfusion Service Center")
    data = data.replace("bank", "Banknote Authentication")
    data = data.replace("QSAR", "QSAR biodegradation")
    data = data.replace("spambase", "Spambase")
    data = data.replace("iris", "Iris")
    data = data.replace("heartdisease", "Heart Disease")

    xlabel      = "Rejection %"
    ylabel      = "Accuracy %"

    if single_plot:
        fig, axs = plt.subplots(1,1)
        fig.set_figheight(5)
        fig.set_figwidth(5)
    else:
        if vertical_plot:
            fig, axs = plt.subplots(len(modes),1)
            fig.set_figheight(10)
            fig.set_figwidth(5)
        else:
            fig, axs = plt.subplots(1,len(modes))
            fig.set_figheight(4)
            fig.set_figwidth(15)
    legend_list = []
    



    # get input from command line
    mydb = db.connect(host="131.234.250.119", user="root", passwd="uncertainty", database="uncertainty")
    mycursor = mydb.cursor()
    mycursor.execute(query) # run_name ='uni_exp'
    results = list(mycursor.fetchall())
    jobs = []
    for job in results:
        jobs.append(job)

    plot_list = []

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
            if "set19" in legend:
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
                    color = "red"
                if "levi3.GH" in legend:
                    color = "blue"
                if "levi3.ent" in legend:
                    color = "red"
                if "levidir.GH" in legend:
                    color = "blue"
                if "levidir.ent" in legend:
                    color = "red"
                if "gs" in legend:
                    color = "green"
                if "set14" in legend:
                    color = "blue"
                if "set15" in legend:
                    color = "red"
                if "set18" in legend:
                    color = "blue"
                if "set19" in legend:
                    color = "red"
            else:
                color = None

            legend = legend.replace("levi.GH.conv", "Levi-GH-conv")
            legend = legend.replace("levi.ent.conv", "Levi-Ent-conv")
            legend = legend.replace("levi.GH", "Levi-GH")
            legend = legend.replace("levi.ent", "Levi-Ent")
            legend = legend.replace("levi3.GH", "Levi-GH-MANY")
            legend = legend.replace("levi3.ent", "Levi-Ent-MANY")
            legend = legend.replace("bays", "Bayes")
            legend = legend.replace("set14", "Levi-GH-boot")
            legend = legend.replace("set15", "Levi-Ent-boot")
            legend = legend.replace("set18", "Levi-GH")
            legend = legend.replace("set19", "Levi-Ent")
            legend = legend.replace("gs", "GS")



            avg_acc = avg_acc * 100 # to have percentates and not decimals

            if single_plot:
                axs.plot(steps, avg_acc, linestyle=linestyle, color=color)
            else:
                axs[mode_index].plot(steps, avg_acc, linestyle=linestyle, color=color)
                # axs[mode_index].grid(which='minor') # to show grids in the plot
            
            if mode == "a":
                mode_title = "AU"
            if mode == "e":
                mode_title = "EU"
            if mode == "t":
                mode_title = "TU"
            
            if single_plot:
                legend_list.append(legend + " " + mode_title)
            elif flap:
                legend_list.append(legend)
                
            
            if single_plot:
                axs.set_title(data)
            else:
                axs[mode_index].set_title(data + " " + mode_title)
            flap =False

    if single_plot == False:
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
    # title = plot_list
    # fig.suptitle(data)
    # with warnings.catch_warnings():
    #     warnings.simplefilter("ignore", category=RuntimeWarning)
    if legend_flag:
        fig.legend(axs,labels=legend_list, loc="lower center", ncol=6)

    fig.savefig(f"./pic/unc/{plot_name}.png",bbox_inches='tight')
    # fig.close()
    print(f"Plot {plot_name} Done")
import mysql.connector as db
import os

auto_run = False

data_names     = ["Jdata/parkinsons", "Jdata/vertebral","Jdata/ionosphere", "Jdata/climate", "Jdata/blod", "Jdata/breast","Jdata/bank", "Jdata/QSAR", "Jdata/spambase", "Jdata/iris", "Jdata/heartdisease"] # 
# data_names     = ["Jdata/parkinsons","Jdata/ionosphere", "Jdata/blod", "Jdata/breast", "Jdata/QSAR", "Jdata/wine_qw"] # 
# data_names     = ["Jdata/vertebral", "Jdata/climate","Jdata/bank", "Jdata/spambase"] # 
# data_names     = ["Jdata/iris"] 
# data_names     = ["Jdata/parkinsons"] 
algos          = ["DF"] # ,"LR"
modes          = ["bays", "set18", "set19"] #  "levi.ent", "levi.GH.conv", "levi.ent.conv"  "levi.ent" ["ent_e","ent_a","ent_t", "random"]  # ent_e","ent_a","ent_t  "set14", "set15", "set14.convex", "set15.convex", "ent.levi"
# modes          = [] 
task           = "unc"
runs           = 100
prams = {
'max_depth'          : 10,
'n_estimators'       : 10,

'epsilon'            : 2,

# 'credal_size'        : 10,
# 'credal_L'           : 1.5,
# 'credal_sample_size' : 200,
'laplace_smoothing'  : 1,
'split'              : 0.30,
'run_start'          : 0,
}


for algo in algos:
    for data_name in data_names:
        for mode in modes:
            run_name       = "DSpaper2" #f"{mode}_{algo}" + "noctua_test" # if you want a specific name give it here
            description    = "acc_hist"

            mydb = db.connect(host="131.234.250.119", user="noctua", passwd="uncertainty", database="uncertainty")
            mycursor = mydb.cursor()

            mycursor.execute("SELECT id FROM experiments ORDER BY id DESC LIMIT 1") #get last id in DB
            results = mycursor.fetchall()
            job_id = results[0][0] + 1 # set new id
            result_address = f"/home/mhshaker/Projects/Database/DB_files/job_{job_id}" # set results address
            sqlFormula = "INSERT INTO experiments (id, task, run_name, algo, prams, dataset, runs, status, description, result_type, results) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            jobs = [(job_id, task, run_name, algo, str(prams), data_name, runs, "pending", description, mode, result_address)]
            mycursor.executemany(sqlFormula, jobs) # insert new job to DB
            mydb.commit() # save


if auto_run:
    if task == "unc":
        os.system("bash /home/mhshaker/projects/uncertainty/bash/run_unc.sh")
        os.system(f"python3 /home/mhshaker/projects/uncertainty/bash/plot_accrej.py auto_unc tea {job_id}")
    elif task == "sampling":
        os.system("bash /home/mhshaker/projects/uncertainty/bash/run_sampling.sh")
        os.system(f"python3 /home/mhshaker/projects/uncertainty/bash/plot_sampling.py auto_samp {job_id}")

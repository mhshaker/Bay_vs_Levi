import os
import sys
import time
from ast import literal_eval
import numpy as np
import Data.data_provider as dp
import Data.data_generator as dg
import Algo.a_DF as df
# import Algo.a_eRF as erf
# import Algo.a_Tree as tree
import mysql.connector as db
import sklearn
import ray


@ray.remote
def uncertainty_quantification(seed, features, target, prams, mode, algo, dir):
    s_time = time.time()
    x_train, x_test, y_train, y_test = dp.split_data(features, target, split=prams["split"], seed=seed)
    
    if algo == "DF":
        predictions , t_unc, e_unc, a_unc, model = df.DF_run(x_train, x_test, y_train, y_test, prams, unc_method, seed)
    # elif algo == "eRF":
    #     predictions , t_unc, e_unc, a_unc, model = erf.eRF_run(x_train, x_test, y_train, y_test, prams, unc_method, seed)
    # elif algo == "Tree":
    #     predictions , t_unc, e_unc, a_unc, model = tree.Tree_run(x_train, x_test, y_train, y_test, prams, unc_method, seed)
    # elif algo == "BN":
    #     y_train_BN, y_test_BN, model = bn.BN_init(x_train, x_test, y_train, y_test, prams, unc_method, seed)
    #     acc , t_unc, e_unc, a_unc, model = bn.BN_run(x_train, x_test, y_train, y_test, 0, 0, prams, unc_method, seed, model, active_step=0) 
    #     predictions , t_unc, e_unc, a_unc, model = tree.Tree_run(x_train, x_test, y_train, y_test, prams, unc_method, seed)
    else:
        print("[ERORR] Undefined Algo")
        exit()
        
    # print(f"run {seed} score: train {model.score(x_train, y_train):0.2f} | test {model.score(x_test, y_test):0.2f}")

    # check for directories
    p_dir = f"{dir}/p"
    t_dir = f"{dir}/t"
    e_dir = f"{dir}/e"
    a_dir = f"{dir}/a"
    l_dir = f"{dir}/l"
    
    if not os.path.exists(p_dir):
        os.makedirs(p_dir)
        os.makedirs(t_dir)
        os.makedirs(e_dir)
        os.makedirs(a_dir)
        os.makedirs(l_dir)

    # save the results
    np.savetxt(f"{p_dir}/{seed}.txt", predictions.astype(int))
    np.savetxt(f"{t_dir}/{seed}.txt", t_unc)
    np.savetxt(f"{e_dir}/{seed}.txt", e_unc)
    np.savetxt(f"{a_dir}/{seed}.txt", a_unc)
    np.savetxt(f"{l_dir}/{seed}.txt", y_test.astype(int))

    e_time = time.time()
    run_time = int(e_time - s_time)

    print(f"{seed} :{run_time}s")


if __name__ == '__main__':
    # prameter init default
    job_id = 0 # for developement
    seed   = 1
    runs = 1
    data_name = "Jdata/parkinsons"
    algo = "DF"
    unc_method = "set19"
    prams = {
    # 'criterion'        : "entropy",
    'max_depth'        : 10,

    'n_estimators'     : 3,

    'epsilon'          : 2,

    # 'credal_size'      : 10,
    # 'credal_sample_size' : 5,
    # 'credal_L'           : 3,

    # 'dropconnect_prob' : 0.2,
    # 'epochs'           : 1,
    # 'init_epochs'      : 10,
    # 'MC_samples'       : 5,

    'laplace_smoothing': 1,
    'split'            : 0.025,

    }

    base_dir = os.path.dirname(os.path.realpath(__file__))
    dir = f"{base_dir[:-12]}/Database/DB_files/job_{job_id}"

    # get input from command line
    if len(sys.argv) > 1:
        job_id = int(sys.argv[1])
        mydb = db.connect(host="131.234.250.119", user="noctua", passwd="uncertainty", database="uncertainty")
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT dataset, prams, results, algo, runs, result_type FROM experiments Where id ={job_id}")
        results = mycursor.fetchone()
        data_name = results[0]
        prams = literal_eval(results[1])
        dir = f"{base_dir[:-12]}/Database/DB_files/job_{job_id}"
        algo = results[3]
        runs = results[4]
        unc_method = results[5]
        mycursor.execute(f"UPDATE experiments SET results='{dir}' Where id={job_id}")
        mydb.commit()

    # run the model
    if "test_" in data_name:
        n = prams["n_estimators"]
        m = prams["unc_method"]
        print(f"{data_name} n_estimators {n} unc_method {m}")
        x_train, x_test, y_train, y_test = dg.create(data_name)
        predictions , t_unc, e_unc, a_unc, model = df.DF_run(x_train, x_test, y_train, y_test, prams, unc_method, seed)
        t = np.round(t_unc, decimals=2)
        a = np.round(a_unc, decimals=2)
        e = np.round(e_unc, decimals=2)
        rt = np.argsort(-t_unc)
        re = np.argsort(-e_unc)
        ra = np.argsort(-a_unc)
        rt += 1
        ra += 1
        re += 1
        print(x_test)
        print("------------------------------------")
        print("t_unc ", t, " relative index:", rt)
        print("e_unc ", e, " relative index:", re)
        print("a_unc ", a, " relative index:", ra)
        print(f"All score: {model.score(x_train, y_train)}")
        exit()

    else:
        features, target = dp.load_data(data_name)

        print(f"job_id {job_id} start")

        ray.init()
        ray_array = []
        for seed in range(0,runs):
            ray_array.append(uncertainty_quantification.remote(seed, features, target, prams, unc_method, algo, dir))
        res_array = ray.get(ray_array)

        # uncertainty_quantification(seed, features, target, prams, unc_method, algo, dir)

    if len(sys.argv) > 1:
        mycursor.execute(f"UPDATE experiments SET status='done' Where id={job_id}")
        mydb.commit()
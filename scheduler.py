# This script creates multiple instances of a program to allow usage of all cores at once
# There is a single config stored in base_config that is used for all runs
# gptables can be pulled from a gptable folder
import os
import shutil
import subprocess
from multiprocessing.pool import ThreadPool

def get_chunks(lst,n):
    return [lst[i:i+n] for i in range(0,len(lst),n)]

def run_instance(inst_id):
    working_dir = "./temp_instances/instance_%d" % inst_id
    subprocess.run(["python3","main.py"],cwd=working_dir,stdout=subprocess.DEVNULL)


def main():
    binst_folder = "./base_instance"
    bconfig_folder = "./base_config"
    repls = 5

    cpu_count = os.cpu_count()
    print(">> %d CPUs found. Creating %d instances..." % (cpu_count,cpu_count))

    # Create folder for storing temporary instances
    if os.path.exists('temp_instances'):
        shutil.rmtree('temp_instances')
        os.makedirs('temp_instances')
    else:
        os.makedirs('temp_instances')


    # Create folder for storing results
    if os.path.exists('collected_data'):
        shutil.rmtree('collected_data')
        os.makedirs('collected_data')
    else:
        os.makedirs('collected_data')

    # Create instance folders
    for instance_id in range(cpu_count):
        shutil.copytree(binst_folder,"./temp_instances/instance_%d" % instance_id)

    gptable_id_list = [int(word.split(".")[0].split("_")[1]) for word in os.listdir("./gptables")]
    for gpid in gptable_id_list:
        os.mkdir("./collected_data/gptable_%d" % gpid)

    chunks = get_chunks(gptable_id_list,cpu_count) # Divide into chunks of size os.cpu_count()
    
    for chunk_id,chunk in enumerate(chunks):
        inst_required = len(chunk)
        instdict = {}
        for instid,gpid in enumerate(chunk):
            shutil.copyfile("./gptables/gptable_%d.csv" % gpid,"./temp_instances/instance_%d/config/host_gptable.csv" % instid)
            shutil.copyfile("./gptables/gptable_%d.csv" % gpid,"./temp_instances/instance_%d/config/para_gptable.csv" % instid)
            instdict[instid] = gpid
        
        print(">> Running chunk %d of %d containing %d instances..." % (chunk_id,len(chunks),inst_required))
        for repl in range(repls):
            print("    - Replicate %d | " % repl,end="",flush=True)
            ThreadPool().map(run_instance,range(inst_required))
            print(" Moving output...")
            # Move outputs
            for instid in range(inst_required):
                shutil.move("./temp_instances/instance_%d/output" % instid,"./collected_data/gptable_%d/output_%d" % (instdict[instid],repl))

        
    # Also move config used to collected_data
    print(">> Moving used configuration files to collected_data...")
    shutil.copytree("./base_instance/config","./collected_data/config_used")

    # Remove temp_instance
    print(">> Cleaning up instances...")
    shutil.rmtree('temp_instances')
    print(">> DONE!")
    








if __name__=="__main__":
    main()

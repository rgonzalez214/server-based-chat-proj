from pathlib import Path
from pprint import pprint

"""
User sends message
- server receives message
- server defines timestamp of message arrival
- server creates log file with clientIDs as filename
- server appends message and timestamp to log file

"""
# designate path to chat history
file_path = "history/"

p = Path(file_path).glob('*.txt')
files = [x.name for x in p if x.is_file()]
print("current files available", "".join(files))


def file_name(clients):
    # store a current list of all txt files found in 'files'
    p = Path(file_path).glob('*.txt')
    files = [x.name for x in p if x.is_file()]
    print("current files available", "".join(files))

    # build the filename and validate the existence against the 'files' list.
    f_name = f"{clients[0]}{clients[1]}.txt" if f"{clients[0]}{clients[1]}.txt" in files \
        else f"{clients[1]}{clients[0]}.txt" if f"{clients[1]}{clients[0]}.txt" in files \
        else f"no_file"
    if f_name == 'no_file':
        f_name = f"{clients[0]}{clients[1]}.txt"
        f1 = open(f"{file_path}{f_name}", "w")
        # build payload
        payload = f"Date\t\tTime\t\tSession ID\tclient\t\tData\n"
        print(payload)
        # write payload
        f1.write(payload)
        # close file
        f1.close()
        print(f'new file {f_name} created')
    return f_name

#  open file
def access_log(curr_time, session_id, clients, data):
    # build the filename and validate the existence against the 'files' list.
    f_name = file_name(clients)
    # build the filename and path to pass as argument
    f1 = f"{file_path}{f_name}"

    # pass the arguments along to create and or update log data
    res = write_log(f1, curr_time, session_id, f_name[:9], f_name[9:18], data)
    print(res)
    return f"accessed {f_name}"

# write chat to log
def write_log(file, curr_time, session_id, client_a, client_b, data):
    # open file with append rights
    f1 = open(file, "a+")
    # build payload
    # payload = f"{curr_time} {session_id} {client_a} {client_b}:\n {data}\n"
    payload = f"{curr_time}\t{session_id}\t\t{client_a}\t{data}\n"
    # print(payload)
    # write payload
    f1.write(payload)
    # close file
    f1.close()
    return f'wrote to {file[8:]}'


# read file to end user based on provided client name
def read_log(clienta, clientb):
    clients = [clienta, clientb]
    f1 = open(f"{file_path}{file_name(clients)}", "r")
    log = f1.readlines()
    for line in log:
        print(line)
    f1.close()
    return

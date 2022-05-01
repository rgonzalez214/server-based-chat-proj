from pathlib import Path

"""
User sends message
- server receives message
- server defines timestamp of message arrival
- server creates log file with clientIDs as filename
- server appends message and timestamp to log file

"""
# designate path to chat history
p = Path("history/")
p.mkdir(0o755, True, True)


def file_name(clients):
    # store a current list of all txt files found in 'files'
    txt_files = p.glob('*.txt')
    files = [x.name for x in txt_files if x.is_file()]

    # build the filename and validate the existence against the 'files' list.
    f_name = f"{clients[0]}_{clients[1]}.txt" if f"{clients[0]}_{clients[1]}.txt" in files \
        else f"{clients[1]}_{clients[0]}.txt" if f"{clients[1]}_{clients[0]}.txt" in files \
        else f"no_file"
    if f_name == 'no_file':
        f_name = f"{clients[0]}_{clients[1]}.txt"
        f1 = open(f"{p}/{f_name}", "w+")

        # build payload
        payload = ""

        # write payload
        f1.write(payload)

        # close file
        f1.close()

        # return the filename
    return f_name


# write chat to log
def write_log(session_id, clients, data):
    f = file_name(clients)
    # open file with append rights
    f1 = open(f"{p}/{f}", "a+")

    # build payload
    # payload = f"{curr_time} {session_id} {client_a} {client_b}:\n {data}\n"
    payload = f"{session_id}\tfrom: {clients[1]}\t\t{data}\n"

    # write payload
    f1.write(payload)

    # close file
    f1.close()

    # return wrote to file name
    return f'wrote to {f1.name}'


# read file to end user
def read_log(clients):
    print("chat-history ", clients)
    f = file_name(clients)
    print(f"{p}/{f}")

    f1 = open(f"{p}/{f}", "r")

    log = f1.readlines()

    f1.close()

    return log

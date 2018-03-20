import xmltodict, os
import csv
from tensorflow.python.platform import gfile

vocab_dict = dict()


def filter_queries_by_category(transcript, category_dict):
    transcript_dict = transcript["transcript"]
    precense_arr = transcript_dict["presence"]
    agent_detail_dict = precense_arr[0]
    customer_detail_dict = precense_arr[1]
    agent_id = agent_detail_dict["@from"]
    customer_id = customer_detail_dict["@from"]
    # agent_name = agent_id.split("/")[1]
    # customer_name = customer_id.split("/")[1]
    message_arr = transcript_dict["message"]
    category_str = message_arr[0].get("body")
    category_str = category_str.split("-")[2]
    if not category_dict.get(category_str):
        category_dict[category_str] = []
    specific_category = category_dict[category_str]
    message_arr = message_arr[1:]

    # customer_msg_list = []
    # agent_msg_list = []
    customer_msg = ""
    agent_msg = ""

    conversation = {"customer_messages": [], "agent_messages": []}
    for msg in message_arr:
        if msg["@from"] == customer_id:
            customer_msg += msg["body"]
            if agent_msg != "":
                conversation["agent_messages"].append(agent_msg)
                agent_msg = ""
        if msg["@from"] == agent_id:
            agent_msg += msg["body"]
            if customer_msg != "":
                conversation["customer_messages"].append(customer_msg)
                customer_msg = ""
    specific_category.append(conversation)
    return conversation


def transcript_list(fn, target_columns):
    category_dict = dict()
    with gfile.Open(fn, 'r') as csv_file:
        data_file = csv.reader(csv_file)
        data = []
        heading = True
        for row in data_file:
            if heading:
                heading = False
                continue
            cols = sorted(target_columns.items(), key=lambda tup: tup[1], reverse=True)
            for target_col_name, target_col_i in cols:
                if not len(row) > 3:
                    continue
                transcript_xml = row.pop(target_col_i)
                if transcript_xml is not None and transcript_xml != "":
                    try:
                        transcript_dict = xmltodict.parse(transcript_xml)
                        filter_queries_by_category(transcript_dict, category_dict)
                        data.append(transcript_dict)
                    except Exception as e:
                        print("ignored", e)
        return data, category_dict


def write_csv(category_dict):
    for category, conv_list in category_dict.items():
        with open('category/{}.csv'.format(category), 'a', newline='') as csvfile:
            seqwriter = csv.writer(csvfile, delimiter='|')
            seqwriter.writerow(['seq1', 'seq2'])
            for conv in conv_list:
                conv_zip_list = list(zip(conv["customer_messages"], conv["agent_messages"]))
                for seq in conv_zip_list:
                    seqwriter.writerow([seq[0].replace('\n', ' ').replace('\r', ''), seq[1].replace('\n', ' ').replace(
                        "\r", '')])


def write_txt(category_dict):
    for category, conv_list in category_dict.items():

        if os.path.exists("category/{0}".format(category)):
            append_write = 'a'  # append if already exists
        else:
            append_write = 'w'  # make a new file if not

        with open('category/{}.txt'.format(category), append_write) as txtfile:
            for conv in conv_list:
                conv_zip_list = list(zip(conv["customer_messages"], conv["agent_messages"]))
                for seq in conv_zip_list:
                    txtfile.write("Q: " + seq[0].replace('\n', '').replace('\r', '') + "\n")
                    txtfile.write(
                        "A: " + seq[1].replace('\n', '').replace('\r', '') + "\n")
                txtfile.write("===\n")
            txtfile.close()


def write_vocab_file(category_dict):
    for category, conv_list in category_dict.items():
        vocab_file = open('vocab.txt', 'a')
        with open('category/{}.txt'.format(category), 'w') as txtfile:
            for conv in conv_list:
                conv_zip_list = list(zip(conv["customer_messages"], conv["agent_messages"]))
                for seq in conv_zip_list:
                    seq_str = seq[0].replace('\n', '').replace('\r', '') + seq[1].replace('\n', '').replace('\r', '')
                    for v in seq_str.replace(",", " ").replace(".", " ").split(" "):
                        v = v.strip()
                        if vocab_dict.get(v, 0) == 3:
                            if not v == "":
                                vocab_file.write(v + "\n")
                                vocab_dict[v] = vocab_dict[v] + 1
                        else:
                            if vocab_dict.get(v) is None:
                                vocab_dict[v] = 1
                            else:
                                vocab_dict[v] = vocab_dict[v] + 1
            vocab_file.close()


def seq_to_seq(zip_list):
    seq_list = []
    for s in list(zip_list):
        s1 = s[0]
        s2 = s[1]
        seq_list.append(s1 + s2)
    return seq_list


data, category_dict = transcript_list("chatdata.csv", target_columns={"TRANSCRIPT": 3})
write_txt(category_dict)

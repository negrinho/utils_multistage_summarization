# processes the XML files to JSONL format.

from xml.dom import minidom
import research_toolbox.tb_filesystem as tb_fs
import research_toolbox.tb_io as tb_io
import numpy as np

grouping_type = "speaker_timeout"
timeout = 1.0
word_ps = tb_fs.list_files('data/ami_public_manual_1.6.2/words')
summary_ps = tb_fs.list_files('data/ami_public_manual_1.6.2/abstractive')

f = minidom.parse("data/ami_public_manual_1.6.2/corpusResources/meetings.xml")
speaker_rs = f.getElementsByTagName('speaker')
speaker2role = {}
for r in speaker_rs:
    meeting_id = r.getAttribute('nite:id').split("_")[0]
    speaker_id = r.getAttribute('nxt_agent')
    speaker2role[(meeting_id, speaker_id)] = r.getAttribute('role')

# word_ps = [
#     "data/ami_public_manual_1.6.2/words/EN2001a.%s.words.xml" % x
#     for x in ["A", "B", "C", "D"]
# ]
# summary_ps = [
#     "data/ami_public_manual_1.6.2/abstractive/EN2001a.%s.words.xml" % x
#     for x in ["A", "B", "C", "D"]
# ]

def quantiles(vs, alphas):
    sorted_vs = sorted(vs)
    num_values = len(vs)
    indices = [int(q * num_values) for q in alphas]
    return [sorted_vs[i] for i in indices]


def statistics(meeting2out):
    pass


def show_transcript(xs):
    for x in xs:
        print("%s: %s" % (x[0], " ".join(x[1])))

# read the words in
data = []
for i, path in enumerate(word_ps):
    out = {}
    name = tb_fs.path_last_element(path)
    print(i, name)
    fields = name.split('.')
    # NOTE: there are different summaries for these
    out["meeting_id"] = fields[0]
    out["speaker_id"] = fields[1]
    # speaker_role =  # TODO: this can be grasped from the correct dataset.

    f = minidom.parse(path)
    word_recs = f.getElementsByTagName('w')
    words = []
    start_times = []
    end_times = []
    for r in word_recs:
        try:
            w = r.firstChild.data
            start_t = float(r.getAttribute('starttime'))
            end_t = float(r.getAttribute('endtime'))
        except ValueError:
            print(name, w, start_t, end_t)

        words.append(w)
        start_times.append(start_t)
        end_times.append(end_t)

    out["words"] = words
    out["start_times"] = np.array(start_times, dtype='float')
    out["end_times"] = np.array(end_times, dtype='float')
    assert len(words) == len(start_times) and len(words) == len(end_times)
    out["time_to_next_word"] = out["start_times"][1:] - out["end_times"][:-1]
    data.append(out)

# group by speaker
meeting2data = {}
for d in data:
    out = []
    if d["meeting_id"] not in meeting2data:
        meeting2data[d["meeting_id"]] = []
    meeting2data[d["meeting_id"]].append(d)

# change the speaker as soon as some other speaker talks.
if grouping_type == "speaker_change":
    meeting2out = {}
    for meeting_id, lst in meeting2data.items():
        # print(meeting_id)
        rs = meeting2data[meeting_id]

        utterances = []
        u = []
        prev_speaker_id = None
        indices = [0] * len(rs)
        while any([indices[i] < len(r["words"]) for i, r in enumerate(rs)]):
            min_time = np.inf
            for rec_idx, r in enumerate(rs):
                word_idx = indices[rec_idx]
                if word_idx < len(r["words"]):
                    t = r["end_times"][word_idx]
                    if t < min_time:
                        min_rec_idx = rec_idx
                        min_time = t
                        min_word = r["words"][word_idx]

            min_speaker_id = rs[min_rec_idx]["speaker_id"]
            if min_speaker_id != prev_speaker_id:
                if len(u) > 0:
                    utterances.append([prev_speaker_id, u])
                u = [min_word]
                prev_speaker_id = min_speaker_id
            else:
                u.append(min_word)

            # out.append((min_word, rs[min_rec_idx]["speaker_id"]))
            indices[min_rec_idx] += 1

        if len(u) > 0:
            utterances.append([prev_speaker_id, u])

        meeting2out[meeting_id] = utterances
# show_transcript(meeting2out["EN2001a"][:16])
# print(
#     quantiles([len(x) for x in meeting2out.values()],
#               [0.0, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.9999]))

elif grouping_type == "speaker_timeout":
    meeting2out = {}
    for meeting_id, lst in meeting2data.items():
        # print(meeting_id)
        rs = meeting2data[meeting_id]
        utterances = []
        for r in rs:
            num_words = len(r["words"])
            u = []
            for i, w in enumerate(r["words"]):
                if len(u) == 0:
                    u_start_time = r["start_times"][i]
                u.append(w)
                if i == num_words - 1 or r['time_to_next_word'][i] >= timeout:
                    utterances.append([r["speaker_id"], u_start_time, u])
                    u = []

        if len(u) > 0:
            utterances.append([prev_speaker_id, u_start_time, u])

        sorted_utterances = sorted(utterances, key=lambda x: x[1])
        meeting2out[meeting_id] = [[u[0], u[2]] for u in sorted_utterances]

    # join consecutive utterances if they have the same speaker id.

# print("--------------------------------------------------------")
# show_transcript(meeting2out["EN2001a"][:16])
else:
    raise ValueError("Unknown option: %s" % grouping_type)

# NOTE: it has to update the problem.

print(
    quantiles([len(x) for x in meeting2out.values()],
              [0.0, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.9999]))

out_data = []
punct = {'.', ',', '!', '?'}
for meeting_id, lst in meeting2out.items():
    utterances = []
    for x in lst:
        s = "".join([' ' + tk if tk not in punct else tk for tk in x[1][1:]])
        u = x[1][0] + s
        d = {"utterance": u, "speaker_id": x[0]}
        utterances.append(d)

    roles = {}
    for x in ["A", "B", "C", "D", "E", "F"]:
        k = (meeting_id, x)
        if k in speaker2role:
            roles[x] = speaker2role[k]
    out_d = {"meeting_id": meeting_id, "utterances": utterances, "roles": roles}
    out_data.append(out_d)

index = {x["meeting_id"]: x for x in out_data}
for path in summary_ps:
    f = minidom.parse(path)
    meeting_id = tb_fs.path_last_element(path).split('.')[0]
    sentence_recs = f.getElementsByTagName('sentence')
    summary = " ".join([r.firstChild.data for r in sentence_recs])
    index[meeting_id]["summary"] = summary

tb_io.write_jsonlogfile('data.jsonl', out_data)
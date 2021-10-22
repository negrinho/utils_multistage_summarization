
# breaks the sentence guaranteeing at least a certain amount of overlap
def compute_break_index(utterance_lengths, start_idx, end_idx, overlap):
    assert overlap >= 0.0 and overlap <= 1.0
    num_utterances = end_idx - start_idx
    fragment_length = sum(utterance_lengths[start_idx:end_idx])
    running_length = 0
    idx = end_idx
    for i in range(num_utterances):
        running_overlap = running_length / float(fragment_length)
        if running_overlap >= overlap:
            return idx
        idx -= 1
        running_length += utterance_lengths[idx]
    return start_idx

def chunk_conversation(x, header_length, fragment_length, fragment_overlap):
    num_utterances = len(x)
    utterance_lengths = []
    for i in range(len(x)):
        v = len(x[i]["utterance"])
        utterance_lengths.append(v)
    total_length = sum(utterance_lengths)
    header_utterances = []
    fragments = []
    if total_length <= header_length + fragment_length:
        header_utterances = x
    else:
        idx = 0
        h_length = 0
        # getting the header.
        while h_length + utterance_lengths[idx] <= header_length:
            header_utterances.append(x[idx])
            h_length += utterance_lengths[idx]
            idx += 1

        # TODO: check that I'm not off by one.
        # getting the fragments
        while idx < num_utterances:
            f_length = 0
            start_idx = idx
            fragment_utterances = []
            while idx < num_utterances and f_length + utterance_lengths[idx] <= fragment_length:
                fragment_utterances.append(x[idx])
                f_length += utterance_lengths[idx]
                idx += 1
            if len(fragment_utterances) >= 1:
                fragments.append(fragment_utterances)

            # prevent complete overlap.
            if idx < num_utterances:
                break_idx = compute_break_index(utterance_lengths, start_idx, idx, fragment_overlap)
                assert break_idx != start_idx
                idx = break_idx

    return header_utterances, fragments

def stringfy_utterance_with_role(u, doctor_str, patient_str):
    if u["role"] == "dr":
        s = doctor_str + u["utterance"]
    elif u["role"] == 'pt':
        s = patient_str + u["utterance"]
    else:
        raise ValueError("Unknown role id: %s" % u["role"])
    return s


def serialize_conversation_fragments(header_utterances, fragments, doctor_str, patient_str, utterance_separator_str, header_fragment_separator_str, continuation_str):
    header_strs = []
    for u in header_utterances:
        s = stringfy_utterance_with_role(u, doctor_str, patient_str)
        header_strs.append(s)

    fragment_strs_lst = []
    for f in fragments:
        f_strs = []
        for u in f:
            s = stringfy_utterance_with_role(u, doctor_str, patient_str)
            f_strs.append(s)
        fragment_strs_lst.append(f_strs)

    out_strs = []
    header_str = utterance_separator_str.join(header_strs)
    if len(fragment_strs_lst) == 0:
        out_strs.append(header_str)
    else:
        num_fragments = len(fragment_strs_lst)
        assert num_fragments > 1

        for i, f_strs in enumerate(fragment_strs_lst):
            fragment_str = utterance_separator_str.join(f_strs)

            # first fragment
            if i == 0:
                out_s = utterance_separator_str.join([header_str, fragment_str])
                if len(fragment_strs_lst) > 1:
                    out_s = utterance_separator_str.join([out_s, continuation_str])
            # inner fragments
            elif i < num_fragments - 1:
                out_s = utterance_separator_str.join([header_str, header_fragment_separator_str, fragment_str, continuation_str])
            # last fragment
            else:
                out_s = utterance_separator_str.join([header_str, header_fragment_separator_str, fragment_str])

            out_strs.append(out_s)
    return out_strs

# a continuation of the model.

# x = [
#     {"utterance": "hey, how are you doing?", "role": 'dr'},
#     {"utterance": "good", "role": 'pt'},
#     {"utterance": "you?", "role": 'dr'},
#     {"utterance": "also good, but do you realize that this is filler.", "role": 'pt'},
#     {"utterance": "1. I do, but I don't care.", "role": 'dr'},
#     {"utterance": "1. neither do I", "role": 'pt'},
#     {"utterance": "1. great", "role": 'dr'},
#     {"utterance": "2. I do, but I don't care.", "role": 'dr'},
#     {"utterance": "2. neither do I", "role": 'pt'},
#     {"utterance": "2. great", "role": 'dr'},
# ]
x = [{"utterance" : "Hello! What can I do for you?", "role" : "dr"},
{"utterance" : "Good Morning Doctor. I don’t feel good.", "role" : "pt"},
{"utterance" : "Come and sit here. Open your mouth. Since how long are you not feeling well?", "role" : "dr"},
{"utterance" : "Since yesterday.", "role" : "pt"},
{"utterance" : "No problem. Did you have motions yesterday?", "role" : "dr"},
{"utterance" : "No Doctor. Not so freely. Doctor I feel weak and do not feel like eating.", "role" : "pt"},
{"utterance" : "Ok. And what else?", "role" : "dr"},
{"utterance" : "I feel like vomiting.", "role" : "pt"},
{"utterance" : "Do you drink a lot of water?", "role" : "dr"},
{"utterance" : "No Doctor, I don’t have water too much.", "role" : "pt"},
{"utterance" : "Did you took any medicine?", "role" : "dr"},
{"utterance" : "Yes Doctor, I took a Crocin.", "role" : "pt"},
{"utterance" : "Who asked you to take it?", "role" : "dr"},
{"utterance" : "No one Doctor. I took it myself.", "role" : "pt"},
{"utterance" : "why did you take it?", "role" : "dr"},
{"utterance" : "Because I felt a headache.", "role" : "pt"},
{"utterance" : "Nothing to be worried at. Do you need quick relief?", "role" : "dr"},
{"utterance" : "No Doctor. It is enough you give me medicines for now.", "role" : "pt"}]

print([len(u["utterance"]) for u in x])

# no overlap
print("** no overlap **")
header_utterances, fragments = chunk_conversation(x, 256, 256, 0.0)
# print(len(fragments))
# print(fragments)
# print(header_utterances, fragments)
out_strs = serialize_conversation_fragments(header_utterances, fragments, '[dr]: ', patient_str='[pt]: ', utterance_separator_str=' | ', header_fragment_separator_str='...', continuation_str='...')
for s in out_strs:
    print(s)

# 50 percent overlap
print("** 50 percent overlap **")
header_utterances, fragments = chunk_conversation(x, 256, 256, 0.5)
# print(len(fragments))
# print(fragments)
# print(header_utterances, fragments)
out_strs = serialize_conversation_fragments(header_utterances, fragments, '[dr]: ', patient_str='[pt]: ', utterance_separator_str=' | ', header_fragment_separator_str='...', continuation_str='...')
for s in out_strs:
    print(s)

# assert compute_break_index([1, 2, 3], 0, 3, 1.0) == 0
# assert compute_break_index([1, 2, 3], 0, 3, 0.0) == 3
# assert compute_break_index([1, 2, 3], 0, 3, 0.5) == 2
# assert compute_break_index([1, 2, 3], 0, 3, 0.8) == 1
# assert compute_break_index([1, 2, 3], 0, 2, 0.3) == 1
# assert compute_break_index([1, 2, 3], 0, 2, 0.1) == 1

# print(compute_break_index([1, 2, 3], 0, 3, 1.0))
# print(compute_break_index([1, 2, 3], 0, 3, 0.0))
# print(compute_break_index([1, 2, 3], 0, 3, 0.5))

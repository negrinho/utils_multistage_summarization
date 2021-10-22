
import research_toolbox.tb_io as tb_io

def write_output(data, out_filepath):
    lines = []
    lines.extend(["<html>", "<body>"])
    lines.extend([
        '<head>',
        '<style>',
        '.container {display: flex}',
        '.flex-item {flex: 1 1 0px; padding: 5px}',
        '.header {text-align: center; font-weight: bold;}',
        '</style>'
        '</head>'
    ])
    labels = data["labels"]
    sentences = [data["sentences"][label] for label in data["labels"]]
    num_columns = len(labels)
    num_rows = len(sentences[0])

    lines.append("<div class=container>")
    for j in range(num_columns):
        lines.append('  <div class="flex-item header">%s</div>' % labels[j])
    lines.append("</div>")
    for i in range(num_rows):
        lines.append("<div class=container>")
        for j in range(num_columns):
            lines.append("  <div class=flex-item>%s</div>" % sentences[j][i])
        lines.append("</div>")
    lines.extend(["</body>", "</html>"])
    tb_io.write_textfile(out_filepath, lines)

if __name__ == "__main__":
    # TODO: pass the right number of files.
    filepath_lst = [
        "preliminary_exampes (1)/val_sent_trans_cons_label_oak.target", "/Users/negrinho/Downloads/preliminary_exampes (1)/val_best_single_attn_oak_1_.hypo"
    ]
    filepath_lst = [
        'dev_oak_bertscore_stage2_maxsymp.target',
        'dev_oak_hpis_maxsymp_l512_epoch3.hypo',
        'dev_oak_bertscore_stage2.hypo',
    ]
    labels = [""]

    labels = ["gold", "model"]
    sentences = [tb_io.read_textfile(path) for path in filepath_lst]
    data = {
        "labels" : labels,
        "sentences": {label: lst for (label, lst) in zip(labels, sentences)}
    }
    write_output(data, "outgen.html")
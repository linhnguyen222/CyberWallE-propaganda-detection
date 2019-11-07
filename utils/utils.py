import os
from spacy.lang.en import English

TC_LABELS_FILE = "../datasets/train-task2-TC.labels"
TRAIN_DATA_FOLDER = "../datasets/train-articles/"

def get_spans_from_text(labels_file, raw_data_folder, file_to_write):
    """
    Subtract spans from raw texts and create a new file
    which contains both labels and spans.
    
    :param labels_file: dir of the tab-separated file of form 
                        document_id - propaganda_label - beginning of span - end of span 
    :param raw_data_folder: dir of folder with texts
    :param file_to_write: directory of the file to write
    """
    with open(labels_file) as f:
        table = f.readlines()
        table = [row.split() for row in table]

    open_doc_id = ""
    open_doc_txt = ""
    output_table = []

    for row in table:
        doc_id = row[0]
        from_id = int(row[2])        # idx of the beginning of the span
        to_id = int(row[3])          # idx of the end of the span

        # read the file if it's not opened yet
        if str(doc_id) != open_doc_id:
            with open(os.path.join(raw_data_folder, "article{}.txt".format(doc_id))) as f:
                open_doc_txt = f.read()
                open_doc_id = doc_id

        span = open_doc_txt[from_id:to_id].strip()
        output_table.append(row + [span])

    with open(file_to_write, 'w') as f:
        for row in output_table:
            f.write('\t'.join(row) + "\n")


def annotate_text(raw_data_folder, labels_data_folder, file_to_write):
    nlp = English()
    tokenizer = nlp.Defaults.create_tokenizer(nlp)
    output_table = []
    file_counter = 0


    print("Total number of files - {}".format(len(os.listdir(raw_data_folder))))

    # Reading all the files from the raw text directory
    article_file_names = [file_name for file_name in os.listdir(raw_data_folder)
                          if file_name.endswith(".txt")]
    article_file_names.sort()

    for file_name in article_file_names:
        label_file_name = file_name.replace(".txt", ".task2-TC.labels")

        print("raw_article: {}\tlabel_file: {}".format(file_name, label_file_name))

        # Read the labels file with 4 columns of format
        # doc_id : label_of_span : idx_span_begin : idx_span_end
        with open(os.path.join(labels_data_folder, label_file_name), encoding="utf-8") as file:
            rows = file.readlines()
            rows = [row.strip().split("\t") for row in rows if len(row.split("\t")) == 4]

            #Saving mappings char_idx->labels into the dictionary
            char_idx2label = dict()
            for row in rows:
                _, label, idx_from, idx_to = row[0], row[1], int(row[2]), int(row[3])

                for idx in range(idx_from, idx_to):
                    if idx not in char_idx2label.keys():
                        char_idx2label[idx] = []
                    char_idx2label[idx].append(label)

        # Read the article and process the text
        with open(os.path.join(raw_data_folder, file_name), encoding="utf-8") as file:
            file_text = file.readlines()
            file_text = " ".join([line.strip() for line in file_text])

            tokens = tokenizer(file_text)
            tokens = [str(token) for token in tokens if not str(token).isspace()]

            if len(tokens) < 100:
                print(len(tokens))


            doc_length = len(file_text)
            char_idx = 0

            while char_idx < doc_length:
                if file_text[char_idx].isspace():
                    char_idx += 1
                else:
                    token = tokens[0]
                    if file_text[char_idx:].startswith(token) and not file_text[char_idx].isspace():
                        # Check the label of the corresponding char_idx
                        if char_idx in char_idx2label.keys():
                            label = char_idx2label[char_idx]
                        else:
                            label = ["None"]

                        output_table.append([file_name.replace("article", "").replace(".txt", ""),
                                             str(char_idx),
                                             str(char_idx+len(token)),
                                             token, "|".join(label)])
                    char_idx += len(token)
                    tokens.pop(0)

        file_counter += 1
        print("Finished {} files\n".format(file_counter))

        with open(file_to_write, 'w', encoding="utf-8") as f:
            for row in output_table:
                f.write('\t'.join(row) + "\n")

if __name__ == '__main__':
    LABELS_DATA_FOLDER = "../datasets/train-labels-task2-technique-classification/"
    # get_spans_from_text(TC_LABELS_FILE, TRAIN_DATA_FOLDER, "../data/train-task2-TC-with-spans.labels")
    # annotate_text(TRAIN_DATA_FOLDER, LABELS_DATA_FOLDER, "../data/train-data.tsv")
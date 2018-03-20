# Copyright 2017 Bo Shao. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import os

AUG0_FOLDER = "category"
VOCAB_FILE = "vocab.txt"


def generate_vocab_file(corpus_dir):
    """
    Generate the vocab.txt file for the training and prediction/inference. 
    Manually remove the empty bottom line in the generated file.
    """
    vocab_list = []

    # Special tokens, with IDs: 0, 1, 2
    for t in ['_unk_', '_bos_', '_eos_']:
        vocab_list.append(t)

    # The word following this punctuation should be capitalized in the prediction output.
    for t in ['.', '!', '?']:
        vocab_list.append(t)

    # The word following this punctuation should not precede with a space in the prediction output.
    for t in ['(', '[', '{', '``', '$']:
        vocab_list.append(t)

    file_dir = os.path.join(corpus_dir, AUG0_FOLDER)
    for data_file in sorted(os.listdir(file_dir)):
        full_path_name = os.path.join(file_dir, data_file)
        if os.path.isfile(full_path_name) and data_file.lower().endswith('.txt'):
            with open(full_path_name, 'r') as f:
                for line in f:
                    l = line.strip()
                    if not l:
                        continue
                    if l.startswith("Q:") or l.startswith("A:"):
                        tokens = l[2:].strip().split(' ')
                        for token in tokens:
                            if len(token) and token != ' ':
                                t = token.lower()
                                if t not in vocab_list:
                                    vocab_list.append(t)

    print("Vocab size after all files under category are scanned: {}".format(len(vocab_list)))

    with open(VOCAB_FILE, 'a') as f_voc:
        for v in vocab_list:
            f_voc.write("{}\n".format(v))

    print("The final vocab file generated. Vocab size: {}".format(len(vocab_list)))

if __name__ == "__main__":
    from settings import PROJECT_ROOT

    corp_dir = os.path.join(PROJECT_ROOT, 'parser')
    generate_vocab_file(corp_dir)

"""feature_vectors.py: Generates feature vecs from text docs and annotations."""

import os
import os.path
import logging
import random
import csv
import re
import numpy as np

random.seed(7)
np.random.seed(7)

logging.basicConfig(level=logging.INFO)

# constants and config
DIR_DOC = "jset"  # directory containing text docs and annotations


def fns(d):
	""" loads filenames for txt files and corresponding annotation files """

	# list of all txt files in doc directory
	all_txt_fns = [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".txt")]
	
	logging.info("found {} txt fns in doc directory".format(len(all_txt_fns)))

	txt_fns = []
	annot_fns = []

	# build up list of corresponding txt and annotation files
	for txt_fn in all_txt_fns:
		annot_fn = os.path.join(txt_fn + ".annot")

		# current txt_fn has an annotation file
		if os.path.isfile(annot_fn):
			txt_fns.append(txt_fn)
			annot_fns.append(annot_fn)

	logging.info("loaded {} corresponding txt and annot fns".format(len(txt_fns), len(annot_fns)))

	return txt_fns, annot_fns


def load_txt(fn):
	""" loads text file as a list of lines """
	
	# NOTE: preserves newlines (\n) in the text document. desired behavior?
	data = []
	with open(fn, "r") as f:
		for line in f:
			data.append(line)

	logging.info("loaded {}".format(fn))

	return data


def load_annot(fn):
	""" loads annotation file as a list of annotations where each annotation
		is a tuple consisting of (start, end) and each start and each end are
		tuples consisting of (line, col) integers """

	data = []
	with open(fn, "r") as f:
		for line in f:
			line = line.strip()
			start, end = line.split(",")
			start = [int(x) for x in start.split(".")]
			end = [int(x) for x in end.split(".")]

			data.append((start, end))

	logging.info("loaded {}".format(fn))

	return data


def len_prev_lines(current_line, txt_data):
	""" helper function for convert_annots """

	if current_line == 1:
		return 0
	else:
		l = 0
		for line_num in range(current_line - 1):
			l += len(txt_data[line_num])

	return l


def annots2raw(annot_data, txt_data):
	""" converts annot data from the "line.col" format to raw indices 
		the txt_data needs to be in "list of lines" format """

	annot_data_converted = []
	for annot in annot_data:
		start, end = annot

		# in the "line.col" format, "line" is 1-indexed, col is 0-indexed
		# i have no idea why, blame tkinter

		# convert to raw indices
		start_converted = len_prev_lines(start[0], txt_data) + start[1]
		end_converted = len_prev_lines(end[0], txt_data) + end[1]

		annot_data_converted.append((start_converted, end_converted))

	return annot_data_converted


def raw_annots2word_idcs(txt_str, annot_data):
	""" converts raw annot data to word idcs """

	words_with_idcs = [(m.group(0), (m.start(), m.end())) for m in re.finditer(r'\S+', txt_str)]
	txt_split = [x[0] for x in words_with_idcs]
	all_start_ends = [x[1] for x in words_with_idcs]

	annot_word_idcs = []
	for annot in annot_data:
		try:
			annot_word_idx = all_start_ends.index(annot)
			annot_word_idcs.append(annot_word_idx)
		except ValueError as e:
			# this annotation was a partial word (not a full word!) ignore
			logging.info("encountered partial annotation")

	return txt_split, annot_word_idcs


def gen_feature_vectors(txt_fn, txt_str, annot_data):
	
	# since a "word" is our basic unit, we can change our annotations
	# to integers denoting which words are brand names. this will make it
	# easier to select negative examples. we also split the text into a list of words
	txt_split, annot_word_idcs = raw_annots2word_idcs(txt_str, annot_data)

	# generate the POSITIVE examples
	pos_vecs = gen_feature_vectors_from_word_idcs(annot_word_idcs, txt_split, txt_fn)

	# generate the NEGATIVE examples
	all_word_idcs = range(len(txt_split))
	neg_idcs = select_negative_idcs(annot_word_idcs, all_word_idcs, txt_split)

	neg_vecs = gen_feature_vectors_from_word_idcs(neg_idcs, txt_split, txt_fn)

	return pos_vecs, neg_vecs


def is_neighbor(idx, annot_word_idcs):
	""" returns true if the given idx is a neighbor of one of the idcs in annot_word_ids """

	for annot_word_idx in annot_word_idcs:
		if idx == annot_word_idx - 1 or idx == annot_word_idx + 1:
			return True

	return False


def remove_from_lists(val, lists):
	""" removes val from all the lists in lists """
	
	for l in lists:
		if val in l:
			l.remove(val)


def select_negative_idcs(annot_word_idcs, all_word_idcs, txt_split):
	""" selects negative example indices """

	# indices of all words that are not annotated
	neg_possibilities = [idx for idx in all_word_idcs if idx not in annot_word_idcs]

	# indices of only neighbors
	neighbor_idcs = [idx for idx in neg_possibilities if is_neighbor(idx, annot_word_idcs)]

	# indices of only words with no special characters
	no_special_idcs = [idx for idx in neg_possibilities if txt_split[idx].isalpha()]

	# indices of word that start with a uppercase letter
	uppercase_idcs = [idx for idx in neg_possibilities if txt_split[idx][0].isupper()]

	# generate same number of negative examples as positive examples, if possible
	desired_num_neg = len(annot_word_idcs) * 2
	num_neg = desired_num_neg if len(neg_possibilities) >= desired_num_neg else len(neg_possibilities)

	neg_idcs = []
	for x in range(num_neg):

		selection = np.random.choice(["uppercase", "neighbor", "no special", "any"], size=1, p=[0.1, 0.2, 0.3, 0.4])

		# 10% chance of selecting a word with uppercase first letter
		if selection == "uppercase":
			if len(uppercase_idcs) == 0:
				idx = random.sample(neg_possibilities, 1)[0]
			else:
				idx = random.sample(uppercase_idcs, 1)[0]

		# 20% chance of selecting a neighboring word
		if selection == "neighbor":
			# if we are out of neighbors, just sample any negative
			if len(neighbor_idcs) == 0:
				idx = random.sample(neg_possibilities, 1)[0]
			else:
				idx = random.sample(neighbor_idcs, 1)[0]

		# 30% chance of selecting a word with NO special characters
		elif selection == "no special":
			if len(no_special_idcs) == 0:
				idx = random.sample(neg_possibilities, 1)[0]
			else:
				idx = random.sample(no_special_idcs, 1)[0]

		# 50% chance of selecting any random negative possibility
		elif selection == "any":
			idx = random.sample(neg_possibilities, 1)[0]

		neg_idcs.append(idx)
		remove_from_lists(idx, [neg_possibilities, neighbor_idcs, no_special_idcs, uppercase_idcs])


	return neg_idcs


def gen_feature_vectors_from_word_idcs(word_idcs, txt_split, txt_fn):

	vecs = []

	for i, word_idx in enumerate(word_idcs):
		vec = gen_feature_vector(txt_split, word_idx)

		# prefix the vector with some meta data
		# the word, the txt file the word came from, and the word index
		vec = [txt_split[word_idx], txt_fn, word_idx] + vec

		vecs.append(vec)

	return vecs


def get_pos_in_upper_seq(txt_split, word_idx, f_first_letter_upper):
	""" position in a sequence of words where (at least) the first letter is uppercase 
		0: the word is not uppercase - therefore it is not in a sequence of upper words 
		1: the word is the first word in a sequence of upper words
		2: ... etc """

	if not f_first_letter_upper:
		return False, 0

	before = []
	for i in reversed(range(word_idx)):
		if not txt_split[i][0].isupper():
			break
		before.append(i)

	after = []
	for i in range(word_idx + 1, len(txt_split)):
		if not txt_split[i][0].isupper():
			break
		after.append(i)

	# this upper case word is not part of a sequence
	if len(before) == 0 and len(after) == 0:
		return False, 0

	# this word IS part of a sequence,
	else:
		return True, len(before) + 1


def is_prev_word_x(txt_split, word_idx, x):

	if word_idx == 0:
		result = False
	else:
		result = txt_split[word_idx - 1].lower() == x.lower()

	return result


def gen_feature_vector(txt_split, word_idx):
	""" generates a feature vector given the text, split on words, and the
		word index to generate the vector for """

	word = txt_split[word_idx]

	# f1: is the first letter uppercase? (T/F)
	f_first_letter_upper = word[0].isupper()

	# f2: is the entire word uppercase? (T/F)
	f_all_upper = word.isupper()

	# f3: the length of the word (int)
	f_word_len = len(word)

	part_of_upper_seq, pos_in_upper_seq = get_pos_in_upper_seq(txt_split, word_idx, f_first_letter_upper)
	
	# f4: is the the word part of a sequence of upper-first-letter words? (T/F)
	f_part_of_upper_seq = part_of_upper_seq

	# f5: the absolute position of the word in the sequence of upper words (int; 0 if not part)
	# note: this could be "normalized" by reducing it to the range 1-10, for example
	f_pos_in_upper_seq = pos_in_upper_seq

	# f6: does the next word in the sequence contain numerals? (T/F)
	if word_idx == len(txt_split) - 1:
		f_next_word_has_numerals = False
	else:
		f_next_word_has_numerals = any(c.isdigit() for c in txt_split[word_idx + 1])

	# f7: the number of occurrences of this word in the text (int)
	f_num_occurrences = sum([1 for w in txt_split if w == word])

	# f8 does this word only contain letters? (T/F)
	f_word_is_alpha = word.isalpha()

	# f9 is the previous word "the"? (T/F)
	f_prev_word_the = is_prev_word_x(txt_split, word_idx, "the")

	# f10 is the previous word "from" (T/F)
	f_prev_word_from = is_prev_word_x(txt_split, word_idx, "from")

	# f11 is the previous word "by" (T/F)
	f_prev_word_by = is_prev_word_x(txt_split, word_idx, "by")

	vec = [f_first_letter_upper,
			f_all_upper,
			f_word_len, 
			f_part_of_upper_seq, 
			f_pos_in_upper_seq,
			f_next_word_has_numerals,
			f_num_occurrences, 
			f_word_is_alpha,
			f_prev_word_the,
			f_prev_word_from,
			f_prev_word_by]

	return vec


def main():
	
	# text and annotation filenames
	txt_fns, annot_fns = fns(DIR_DOC)

	all_pos_vecs = []
	all_neg_vecs = []

	# each text, annot file combo will generate some number of feature vectors
	for txt_fn, annot_fn in zip(txt_fns, annot_fns):

		logging.info("processing {}".format(txt_fn))

		txt_data = load_txt(txt_fn)
		annot_data = load_annot(annot_fn)

		# convert the annot data from the "line.col" format to raw indices
		annot_data = annots2raw(annot_data, txt_data)

		# also convert txt data to a single string (this must happen after converting
		# the annot data, since annots2raw needs txt data in list format)
		txt_str = "".join(txt_data)

		# make some feature vectors from the annotations in this text file
		pos_vecs, neg_vecs = gen_feature_vectors(txt_fn, txt_str, annot_data)

		all_pos_vecs += pos_vecs
		all_neg_vecs += neg_vecs

	# append label as last item in vector
	all_pos_vecs = [pos_vec + [True] for pos_vec in all_pos_vecs]
	all_neg_vecs = [neg_vec + [False] for neg_vec in all_neg_vecs]

	# combine all vectors into one list
	all_vecs = all_pos_vecs + all_neg_vecs

	# add an index as first item in each vector (sequential)
	all_vecs_with_indices = []
	idx = 0
	for vec in all_vecs:
		all_vecs_with_indices.append([idx] + vec)
		idx += 1

	header = ["id",
				"word", 
				"txt_file", 
				"index_of_word_in_txt_file", 
				"first_letter_uppercase", 
				"all_uppercase",
				"word_len",
				"part_of_upper_seq",
				"pos_in_upper_seq",
				"next_word_has_numerals",
				"num_of_occurrences_of_word",
				"word_only_contains_letters",
				"previous_word_is_the",
				"previous_word_is_from",
				"previous_word_is_by",
				"label"]

	with open("vectors.csv", "w") as f_handle:
		writer = csv.writer(f_handle, delimiter=",")
		writer.writerow(header)
		writer.writerows(all_vecs_with_indices)


if __name__ == '__main__':
	main()

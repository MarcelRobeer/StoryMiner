#!/usr/bin/env python

import sys
import string
import os.path
import timeit
import json
from argparse import ArgumentParser

import spacy
import en_core_web_md

from storyminer.io import Reader, Writer
from storyminer.miner import StoryMiner
from storyminer.userstory import UserStorySet, UserStory, FailedUserStory
from storyminer.utility import Printer, remove_punct

verbose = False
vprint = print if verbose else lambda *a, **k: None

def main(filename, systemname, export):
	"""General class to run the entire program
	"""

	## 1) Initialize spaCy just once (this takes most of the time...)
	vprint("Initializing Natural Language Processor ({}) . . .".format("spaCy"))
	start = timeit.default_timer()

	nlp = en_core_web_md.load()
	nlp_time = timeit.default_timer() - start
	status("Initialized", nlp_time)

	## 2) Mining
	start_ = timeit.default_timer()

	# Read the input file
	stories = Reader.parse(filename)
	user_stories = UserStorySet(nlp, systemname)

	# Parse every user story (remove punctuation and mine)
	miner = StoryMiner(user_stories.system)
	for i, s in enumerate(stories):
		try:
			us = parse(s, i + 1, nlp, miner)
			user_stories.set.append(us)
		except ValueError as e:
			user_stories.set.append(FailedUserStory(i + 1, s, str(e.args[0])))

	status("Done mining", timeit.default_timer() - start_)

	if export:
		## 3) Create output
		start_ = timeit.default_timer()
		output = str(user_stories.toJSON())
		status("Output JSON created", timeit.default_timer() - start_)

		## 4) Write output files
		start_ = timeit.default_timer()
		w = Writer()
		file = w.make_file("output", str(systemname), "json", output)
		status("Written to file '{}', done".format(file), timeit.default_timer() - start_)

	time = timeit.default_timer() - start
	vprint("Time taken: {}s".format(time))

	# Return objects so that they can be used as input for other tools
	return user_stories, time


def parse(text, id, nlp, miner):
	"""Create a new user story object and mines it to map all data in the user story text to a predefined model
	
	:param text: The user story text
	:param id: The user story ID, which can later be used to identify the user story
	:param nlp: Natural Language Processor (spaCy)
	:param miner: instance of class Miner
	:returns: A new user story object
	"""
	# Prepare for NLP 
	no_punct = remove_punct(text)
	no_double_space = ' '.join(no_punct.split())

	# Create user story object
	user_story = UserStory(id, text.rstrip(), no_double_space)
	user_story.doc = nlp(no_double_space)

	# Mine user story
	miner.structure(user_story)
	user_story.old_doc = user_story.doc
	user_story.doc = nlp(user_story.sentence)
	miner.mine(user_story, nlp)
	return user_story

def status(name, time):
	vprint("> {} (elapsed {:6.4f}s)".format(name, time))


def program(*args):
	p = ArgumentParser(
		usage='''storyminer.py <INPUT FILE>

///////////////////////////////////////////
//              Story Miner              //
///////////////////////////////////////////

This program has multiple functionalities:
    (1) Mine user story information
    (2) Get statistics for a user story set
''',
		epilog='''{*} Utrecht University.
			M.J. Robeer, 2017''')

	p.add_argument("filename",
                    help="input file with user stories", metavar="INPUT FILE",
                    type=lambda x: is_valid_file(p, x))
	p.add_argument('--version', action='version', version='Story Miner v0.3 BETA by M.J. Robeer')
	p.add_argument("-n", "--name", dest="system_name", help="your system name, as used in ontology and output file(s) generation", required=False)
	p.add_argument("-e", "--export", action="store_true", help="export to json", required=False)
	p.add_argument("-v", "--verbose", action="store_true", help="print outputs", required=False)

	if (len(args) < 1):
		args = p.parse_args()
	else:
		args = p.parse_args(args)

	if not args.system_name or args.system_name == '':
		args.system_name = "System"
	
	global verbose
	verbose = args.verbose

	return main(args.filename, args.system_name, args.export)

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("Could not find file " + str(arg) + "!")
    return open(arg, 'r')

if __name__ == "__main__":
	program()
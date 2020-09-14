import requests
import random
import asyncio
import aiohttp
import json

forums_data = []
title_words = []
body_words = []

async def init():
	global forums_data, title_words, body_words
	with open('forums.json', 'r') as f:
		forums_data = json.loads(f.read())

	title_words = []
	for thread in forums_data:
		title_words.extend(['#START#'] + thread['title'].split(' ') + ['#END#'])

	body_words = []
	for thread in forums_data:
		body_words.extend(['#START#'] + thread['body'].split(' ') + ['#END#'])

	print('initialized forum markov stuff')


def remove_punctuation(string):
	return string\
		.replace('.', '')\
		.replace(',', '')\
		.replace('!', '')\
		.replace('?', '')\

async def find_random_next_word(word, searching_list, favor_closing_parenthesis=False, favor_words=set(), alternate_searching_list=[]):
	possible_words = []
	favorable_words = []
	searching_list += alternate_searching_list
	for i, current_word in enumerate(searching_list):
		if current_word == word:
			next_word = searching_list[i + 1]
		else:
			continue
		if not next_word: continue
		closing_parenthesis = next_word[-1] == ')'
		if (closing_parenthesis and favor_closing_parenthesis) and current_word == word:
			favorable_words.append(next_word)
		elif closing_parenthesis:
			continue
		if next_word.lower() in favor_words and remove_punctuation(current_word) == remove_punctuation(word):
			word_count = body_words.count(remove_punctuation(next_word).lower())
			if word_count < 80:
				favorable_words.append(next_word)
			possible_words.append(next_word)

		elif current_word == word:
			if current_word in alternate_searching_list:
				favorable_words.append(next_word)
			possible_words.append(next_word)
		if i % 10:
			await asyncio.sleep(0)
	if len(favorable_words) == 0:
		if not possible_words:
			return '#END#'
		return random.choice(possible_words)
	else:
		await asyncio.sleep(0)
		if (
			random.randint(0, 1) == 0
			or (len(favorable_words) < 10 and random.random() < .7)
		):
			chosen = random.choice(favorable_words)
			print('favorable word:', chosen)
			return chosen
		return random.choice(possible_words)


async def generate_title():
	current_word = '#START#'
	in_parenthesis = False
	generated_title_words = []
	
	while current_word != '#END#':
		current_word = await find_random_next_word(current_word, list(title_words), favor_closing_parenthesis=in_parenthesis)
		if current_word[0] == '(':
			in_parenthesis = True
		if current_word != '#END#':
			generated_title_words.append(current_word)
		await asyncio.sleep(0)
	title = ' '.join(generated_title_words).strip()
	return title

def get_threads_with_word(word):
	body_words = []
	favorable_words = set()
	for thread in forums_data:
		thread_title = thread['title']
		if remove_punctuation(word.lower()) in remove_punctuation(thread_title.lower()).split():
			thread_body = thread['body']
			body_words.append('#START#')
			for word in thread_body.split(' '):
				# word_count = body_words.count(remove_punctuation(word).lower())
				# if word_count < 80:
				# 	favorable_words.add(word)
				body_words.append(word)
			body_words.append('#END#')

	return body_words, favorable_words

async def generate_body(title=''):
	current_word = '#START#'
	in_parenthesis = False
	generated_body_words = []
	i = 0
	other_body_words = []
	favor_words = set()
	for word in title.split():
		word_count = body_words.count(remove_punctuation(word).lower())
		if word_count < 80:
			body_words_tmp, favorable_words_tmp = get_threads_with_word(word)
			other_body_words.extend(body_words_tmp)
			# favor_words.update(favorable_words_tmp)
			favor_words.add(word)
	print('favorable:', favor_words)
	while current_word != '#END#':
		i += 1
		current_word = await find_random_next_word(current_word, list(body_words), favor_closing_parenthesis=in_parenthesis, favor_words=favor_words, alternate_searching_list=other_body_words)
		current_word = current_word\
			.replace('\n\n\n\n', '\n\n')\
			.replace('\n\n\n', '\n\n')
		if current_word[0] == '(':
			in_parenthesis = True
		if current_word[-1] == ')':
			in_parenthesis = False
		if current_word != '#END#':
			generated_body_words.append(current_word)
		await asyncio.sleep(0)
		if i % 15 == 0:
			yield ' '.join(generated_body_words).strip()
			await asyncio.sleep(0.5)
	yield ' '.join(generated_body_words).strip()
	# return ' '.join(generated_body_words).strip()

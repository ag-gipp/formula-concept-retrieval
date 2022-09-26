# Perform semantic search using and (inverse) semantic index
# on NTCIR arXiv (astro-ph) or Wikipedia (MathIR task) dataset respectively

#TODO include Formula Concept Database (AnnoMathTeX)

import pickle
import rapidfuzz

root_path = "E:\\MathQa/semanticsearch/"
#root_path = "semanticsearch/"
#subject = "astro-ph"
subject = ""

# DEFINE

# define function for dict list appending
def append_to_list_if_unique(list,item):
	if item not in list:
		list.append(item)

def append_to_dict_list(dict,key,item,unique):
	if key in dict:
		if unique:
			append_to_list_if_unique(dict[key],item)
		else:
			dict[key].append(item)
	else:
		dict[key] = []
		if unique:
			append_to_list_if_unique(dict[key],item)
		else:
			dict[key].append(item)

# open catalogs
def get_formula_catalog(catalog):
	# open formula catalog
	catalog_filename = catalog + "-Formula_Catalog.pkl"

	with open(root_path + catalog_filename, "rb") as f:
		Formula_Catalog = pickle.load(f)
	return Formula_Catalog

def get_identifier_semantics_catalog(inverse,multiple):
	# get Wikipedia (inverse) identifier semantics catalog (single or multiple)
	if inverse:
		mode1 = "Inverse_"
	else:
		mode1 = ""
	if multiple:
		mode2 = "_multiple"
	else:
		mode2 = "_single"

	file_path = root_path + "modes7-12/" + "Wikipedia-"\
				+ mode1 + "Identifier_Semantics_Catalog" + mode2 + ".pkl"

	with open(file_path, "rb") as f:
		Identifier_Semantics_Catalog = pickle.load(f)
	return Identifier_Semantics_Catalog

# formula search
def search_formulae_by_identifier_symbols(identifier_symbols,catalog):

	# open catalogs
	Formula_Catalog = get_formula_catalog(catalog=catalog)

	# find all formulae containing at least one identifier symbol from all queried names
	match_candidates = {}
	for formula in Formula_Catalog.items():
		found = []
		for identifier_symbol in identifier_symbols:
			if identifier_symbol in formula[1]["id"]:
					found.append(identifier_symbol)

		#if len(found) == len(identifier_symbols):
		match_candidates[formula[0]] = len(found)

	match_candidates_sorted = sorted(match_candidates.items(), key=lambda kv: kv[1], reverse=True)
	query_results = match_candidates_sorted

	# return query results
	return query_results

def search_formulae_by_identifier_names(identifier_names,catalog,multiple):

	# open catalogs
	Formula_Catalog = get_formula_catalog(catalog=catalog)
	Inverse_Identifier_Semantics_Catalog = get_identifier_semantics_catalog(inverse=True,multiple=multiple)

	# find all formulae containing at least one identifier symbol from all queried names
	query_results = {}
	for formula in Formula_Catalog.items():
		found = {}
		for identifier_name in identifier_names:
			identifierSymbols = Inverse_Identifier_Semantics_Catalog[identifier_name]
			for identifierSymbol in identifierSymbols:
				if identifierSymbol in formula[1]["id"]:
					append_to_dict_list(found,identifier_name,identifierSymbol,unique=True)

		if len(found) == len(identifier_names):
			query_results[formula[0] + " (" + formula[1]["file"] + ")"] = found

	# return query results
	return query_results

def search_formulae_by_fuzzystring_arxivwikipedia(formula_input_string, result_limit, catalog):

	formula_catalog = get_formula_catalog(catalog)

	match_candidates = {}

	for formula_index_entry in formula_catalog.items():
		formula_index_string = formula_index_entry[0]
		fuzz_ratio = rapidfuzz.fuzz.ratio(formula_index_string, formula_input_string)
		match_candidates[formula_index_string] = fuzz_ratio

	match_candidates_sorted = sorted(match_candidates.items(), key=lambda kv: kv[1], reverse=True)
	query_results = match_candidates_sorted[:result_limit]

	return query_results

def search_formulae_by_identifiers(input,result_limit,mode_number):

	catalogs = ["NTCIR-12_Wikipedia","NTCIR-12_arXiv"]
	identifier_input_modes = ["symbols","names"]
	multiple_modes = [False,True]

	# 6 evaluation modes:
	# wikip,symbs,single if mode_number == 1
	# wikip,names,single if mode_number == 2
	# wikip,names,multiple if mode_number == 3
	# arxiv,symbs,single if mode_number == 4
	# arxiv,names,single if mode_number == 5
	# arxiv,names,multiple if mode_number == 6
	if mode_number == 1:
		mode_vector = [0, 0, 0]
	if mode_number == 2:
		mode_vector = [0, 1, 0]
	if mode_number == 3:
		mode_vector = [0, 1, 1]
	if mode_number == 4:
		mode_vector = [1, 0, 0]
	if mode_number == 5:
		mode_vector = [1, 1, 0]
	if mode_number == 6:
		mode_vector = [1, 1, 1]

	catalog=catalogs[mode_vector[0]]
	identifier_input_mode=identifier_input_modes[mode_vector[1]]
	multiple_mode=multiple_modes[mode_vector[2]]

	if identifier_input_mode == "symbols":
		query_results = \
			search_formulae_by_identifier_symbols(
			identifier_symbols=input,
			catalog=catalog
		)
	elif identifier_input_mode == "names":
		query_results = \
			search_formulae_by_identifier_names(
			identifier_names=input,
			catalog=catalog,
			multiple=multiple_mode
		)

	return list(query_results)[:result_limit]

# EXECUTE

# formula = 'E = m c^2'
# identifiers = ['E','m','c']
#
# result_limit = 10
#
# # arXiv
#
# catalog = "NTCIR-12_arXiv"
# query_results_arxiv_formula\
# 	= search_formulae_by_fuzzystring(formula_input_string=formula,
# 									 result_limit=result_limit,catalog=catalog)
#
# # arxiv,symbs,single if mode_number == 4
# query_results_arxiv_identifiers\
# 	= search_formulae_by_identifiers(input=identifiers,
# 									 result_limit=result_limit,mode_number=4)
#
# # Wikipedia
#
# catalog = "NTCIR-12_Wikipedia"
# query_results_wikipedia_formula\
# 	= search_formulae_by_fuzzystring(formula_input_string=formula,
# 									 result_limit=result_limit,catalog=catalog)
#
# # wikip,symbs,single if mode_number == 1
# query_results_wikipedia_identifiers\
# 	= search_formulae_by_identifiers(input=identifiers,
# 									 result_limit=result_limit,mode_number=1)

#print('end')
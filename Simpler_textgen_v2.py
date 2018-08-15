import random
import pymorphy2
import re
import csv
import pandas as pd
morph = pymorphy2.MorphAnalyzer()
from num2words import num2words


def check_rules(sentence, row, dataarray):
    if '|' in sentence.sentence:
            result = re.search('\|(.*)\|', sentence.sentence)

            if execute_functions(result.group(1), row, dataarray) is True:
                sentence.sentence = re.sub('\|(.*)\|', '', sentence.sentence)
                return sentence
            else:
                return None
    else:
        return None


def add_actual_values(sentence_rules, row):
    list_bare = []
    for i in row.split(';'):
        list_bare.append(i)
    enumerated_list = list(enumerate(list_bare))
    for i in enumerated_list:
        print(i[1])
        sentence_rules = re.sub('line'+str(i[0]), str(i[1]), sentence_rules)
        print(sentence_rules)
    return sentence_rules


def mean_count(row_number, a):
    mean = a[a.columns[row_number]].mean()
    return mean


def median_count(row_number, a):
    median = a[a.columns[row_number]].median()
    return int(median)


def min_count(row_number, a):
    min = a[a.columns[row_number]].min()
    return int(min)


def max_count(row_number, a):
    max = a[a.columns[row_number]].max()
    return int(max)


def execute_functions(sentence_rules, row, data_arr):
    data_arr = pd.read_csv(data_arr, encoding='utf-8', delimiter=';')
    sentence_rules = add_actual_values(sentence_rules, row)
    print(sentence_rules)
    sentence_rules = re.sub('(\(\d\))', '(\\1, data_arr)', sentence_rules)
    sentence_rules = re.sub('\'?([а-яА-ЯёЁ]+)\'?', '\'\\1\'', sentence_rules)
    print(eval(sentence_rules))
    return eval(sentence_rules)


def pack_whitespaces(line):
    if ' ' or '.' in line:
        packed_line = line.replace(' ', '_')
        packed_line = packed_line.replace('.', '#')
        return packed_line
    else:
        return line

def unpack_whitespaces(line):
    if '_' or '.' in line:
        unpacked_line = line.replace('_', ' ')
        unpacked_line = unpacked_line.replace('#', '.')
        return unpacked_line
    else:
        return line



class DataPoint:  # the basis of this generator type, data point with data class

    def __init__(self, name, data_class, id):
        self.name = name
        self.data_class = data_class
        self.id = id
        self.string = ''


class Sentence:  # sentence class, can use as many data points as it suits

    def __init__(self, data_points, sentence):
        self.data_points = data_points
        self.sentence = sentence


def parse_sentences(sentences): # parses sentences of template and turns them into objects of Sentence Class
    allsentences = []
    with open(sentences, 'r', encoding='utf-8') as f:
        sentences_out = f.readlines()
    for i in sentences_out:
        i = Sentence(re.findall(r'(?<!line)\d+(?!\))', i), i)
        allsentences.append(i)
    return allsentences


def get_data_line(line, names):  # pulls data points from dataset and marks them according to their type
    csv_row = line.split(';')
    enumerated_list = list(enumerate(csv_row))
    alldata = []
    # shit_data = []
    for i in enumerated_list:
        strippedstring = i[1].strip()
        if 'yes' in strippedstring:
            obj = DataPoint(names[i[0]], 'bool_positive', i[0])
            alldata.append(obj)
            continue
        if 'no' in strippedstring:
            obj = DataPoint(names[i[0]], 'bool_negative', i[0])
            alldata.append(obj)
            continue
        if 'Неизвестно' in strippedstring:
            # shit_data.append(i)
            # print(shit_data)
            pass
        else:
            obj = DataPoint(names[i[0]], 'usual', i[0])
            obj.string = i[1].replace('%', '$')
            alldata.append(obj)
    return alldata


def data_class_sort(seed):  # just a little method to help boolean iteration
    iteration_markers = []
    if seed.data_class == 'bool_positive':
        iteration_markers = ['9', '10']
    if seed.data_class == 'bool_negative':
        iteration_markers = ['10', '9']
    return iteration_markers


def iterate_data_bool(iteration_markers, seed, alldata, sentences):  # filling up boolean templates
    iter1 = iteration_markers[0]
    iter2 = iteration_markers[1]
    text_lines1 =[]
    for i in sentences:
        if iter1 in i.data_points:
            if len(i.data_points) > 1:
                niggacheck = []
                niggaset = [1, 2]
                for iter3 in alldata:
                    if iter3.data_class == 'bool_positive':
                        niggacheck.append(1)
                    if iter3.data_class == 'bool_negative':
                        niggacheck.append(2)
                if not set(niggaset).issubset(niggacheck):
                    print('sentcheck failed, getting to next sentence')
                    continue
                    # break
                else:
                    print('sentcheck passed, sentence is clear')
            i.data_points.remove(iter1)
            firstdata = [seed.name.lower()]
            for a in alldata:
                if a.data_class == seed.data_class:
                    firstdata.append(a.name.lower())
                    alldata.remove(a)
            toreturn = re.sub(iter1, ", ".join(firstdata), i.sentence)
            while i.data_points:
                for itera in i.data_points:
                    if itera == iter2:
                        i.data_points.remove(itera)
                        seconddata = []
                        for iterb in alldata:
                            if iterb.id >= 9 and iterb.data_class != seed.data_class:
                                seconddata.append(iterb.name.lower())
                                alldata.remove(iterb)
                        toreturn = re.sub(iter2, ", ".join(seconddata), toreturn)
            else:
                text_lines1.append(toreturn)
                break
        else:
            continue
    if text_lines1:
        returning = text_lines1[0].replace('\n', '')+'\n'
        return returning
    else:
        return'false'


def is_number(s):  # just a small method to quickly check for number
    try:
        int(s)
        return True
    except ValueError:
        return False

def data_get_data(csv_file, template, dictionary):  # main and kinda clunky algo for generation
    a = open(csv_file, encoding='utf-8')
    names = a.readline().split(";")
    for line in a:
        text_lines = []
        sentences = parse_sentences(template)
        alldata = get_data_line(line, names)
        alldatastr =[]
        for data_instance in alldata:
            alldatastr.append(str(data_instance.id))
        random.shuffle(sentences) # сделать порядок
        for i in sentences:
            testcheck = check_rules(i, line, csv_file)
            if testcheck is not None and re.match(r'(?<!line)\d+(?!\))', testcheck.sentence) is not None:
                sentences.remove(i)
                sentences.append(testcheck)
            elif testcheck is not None and re.match(r'(?<!line)\d+(?!\))', testcheck.sentence) is None:
                tostack = testcheck.sentence
                text_lines.append(tostack)
        while alldata:
            print('working...'+line.split(';')[0])
            seed = random.choice(alldata)
            if seed.data_class == 'bool_positive' or seed.data_class == 'bool_negative':
                alldata.remove(seed)
                alldatastr.remove(str(seed.id))
                newsent = iterate_data_bool(data_class_sort(seed), seed, alldata, sentences)
                if newsent == 'false':
                    continue
                text_lines.append(newsent)
            else:
                alldata.remove(seed)
                for i in sentences:
                    if str(seed.id) in i.data_points and len(i.data_points) == 1 and '|' not in i.sentence and str(seed.id) in alldatastr:
                        i.data_points.remove(str(seed.id))
                        toreturn = re.sub(str(seed.id), pack_whitespaces(seed.string), i.sentence)
                        text_lines.append(toreturn.rstrip() + "\n")
                        alldatastr.remove(str(seed.id))
                    if str(seed.id) in i.data_points and set(i.data_points).issubset(alldatastr) and len(i.data_points) > 1 and '|' not in i.sentence:
                        toreturn = re.sub(str(seed.id), pack_whitespaces(seed.string), i.sentence)
                        alldatastr.remove(str(seed.id))
                        i.data_points.remove(str(seed.id))
                        while i.data_points:
                            for itera in i.data_points:
                                i.data_points.remove(str(itera))
                                for iterb in alldata:
                                    if str(itera) == str(iterb.id):
                                        print('-____________-')
                                        print(itera)
                                        print(iterb.id)
                                        print('-____________-')
                                        toreturn = re.sub(" "+str(itera), " "+str(pack_whitespaces(iterb.string)), toreturn)
                                        alldata.remove(iterb)
                                        alldatastr.remove(str(itera))
                                        break
                        text_lines.append(toreturn.rstrip() + "\n")
                        print('xxxxxxxxxxxxxxxx')
                        print(toreturn)
                        print('xxxxxxxxxxxxxxxx')
                        break
                    else:
                        continue
        else:
            intab = '?*/:<">|+!.%@'
            outtab = '             '
            trantab = ''.maketrans(intab, outtab)
            splittedline = line.split(';')[0]
            ready_line = splittedline.translate(trantab)
            with open('out'+ready_line+'.txt', 'a') as the_file:
                templist = list(dictionary.keys())
                first = is_in_sent(text_lines, templist)
                text_lines_srt = first + list(set(text_lines) - set(first))
                for i in text_lines_srt:
                    #templist = list(dictionary.keys())
                    for a in templist:
                        i = re.sub('{'+a+'}', random.choice(dictionary[a].split(',')), i)
                    i = unpack_whitespaces(i)
                    i = preprocessing_number_agreement(i)
                    i = preprocessing_number_change(i)
                    i = preprocessing_no_agreement(i)
                    i = i.replace('$', '')
                    the_file.write(i.capitalize()+'\n')
            with open('outcsv.csv', 'a') as csv_file_final:
                the_file2 = open('out'+ready_line+'.txt', 'r')
                data = the_file2.readlines()
                data = ''.join(data).replace('\n','')
                writer = csv.writer(csv_file_final, delimiter = ';')
                writer.writerow([line.split(';')[0], data])


def is_in_sent(lst, lst2):
    first_lst = []
    for sent in lst:
        for word in lst2:
            if word in sent:
                first_lst.append(sent)
    return sorted(first_lst)

def preprocessing_number_change(line):  # preprocessing -- changing numbers to words
    if re.findall(r"\b\d+\b(?!\.?\d*\$)", line):
        a = re.findall(r"\b\d+\b(?!\.?\d*\$)", line)
        results = list(map(int, a))
        results = sorted(results, reverse = True)
        results = list(map(str, results))
        for i in results:
            line = re.sub(i, num2words(i, lang = 'ru'), line)

        return line
    else:
        return line


def preprocessing_number_agreement(line):  # preprocessing -- making word after number agree with number (rus)
    linearray = line.split()
    for idx, elem in enumerate(linearray):
        if elem.isdigit():
            try:
                test = linearray[idx + 1]
                if test[-1].isalpha():
                    tomorph = morph.parse(linearray[idx+1])[0]
                    linearray[idx + 1] = tomorph.make_agree_with_number(int(elem)).word
                else:
                    toreturn = test[-1]
                    test = test.replace(test[-1], '')
                    tomorph = morph.parse(test)[0].normalized
                    test = tomorph.make_agree_with_number(int(elem[-1])).word
                    test += toreturn
                    linearray[idx + 1] = test
            except IndexError:
                print('error mate')
                continue

    return ' '.join(linearray)


def preprocessing_no_agreement(line):  # preprocessing -- making all words after nyet be in genetive mode.
    stopwords = ['и', 'а', 'но']
    linearray = line.split()
    tochange = {}
    for idx, elem in enumerate(linearray):
        if elem == 'нет':
            for idy, elema in enumerate(linearray[idx:]):
                if elema in stopwords:  # if we find stopword after нет
                    for elemb in linearray[idx:idx+idy]:  # we take all elements between нет and stopword
                        if elemb[-1].isalpha():
                            toappend = try_inflection(elemb)
                            tochange[elemb] = toappend
                        else:
                            toreturn1 = elemb[-1]
                            elemb = elemb.replace(elemb[-1], '')
                            toappend = try_inflection(elemb)
                            toappend += toreturn1
                            elemb += toreturn1
                            tochange[elemb] = toappend
                            break
                    break
                if elema[-1].isalpha():
                    toappend2 = try_inflection(elema)
                    tochange[elema] = toappend2
                else:
                    toreturn = elema[-1]
                    elema = elema.replace(elema[-1], '')
                    toappend2 = try_inflection(elema)
                    toappend2 += toreturn
                    elema += toreturn
                    tochange[elema] = toappend2
            break
    linearray = [tochange.get(item, item) for item in linearray]
    return ' '.join(linearray)


def try_inflection(word):  # small service algo to try and inflect words down the line
    try:
        word = morph.parse(word)[0].inflect({'gent'}).word
        return word
    except AttributeError:
        return word


def get_dictionary(dictionary):  # getting a dictionary from csv file for further use
    with open(dictionary, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile, delimiter=';')
        mydict = {rows[0]: rows[1] for rows in reader}
        return mydict

testdictionary = get_dictionary('testdictionary.csv')

data_get_data('test.csv', 'testtemplate1.txt', testdictionary)

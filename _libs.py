"""
    :author Jerent Steeve:
    :licence MIT:
"""

from pathlib import Path
import random
import uuid
import os
import sys
import re


BASIC_ATTR = [u"varchar2", u"varchar", u"number", u"date"]  # to complete


def dictionary_exist(name):
    """
        Check if dictionary exists
        :param name: name of dictionary
        :return: True if the file exists, otherwise False
    """
    my_file = Path("./dictionary/" + name + ".dict")
    return my_file.is_file()


def number_line_dictionary(name):
    """
        Give number of lines for a dictionary.
        :param name: name of dictionary
        :return: number of line, otherwise False

    """
    if dictionary_exist(name):
        return sum(1 for line in open("./dictionary/" + name + ".dict"))
    else:
        return False


def select_line(name, line):
    """
    Give value of a line in a dictionary.
    :param name: name of dictionary
    :param line: line number to search value in dictionary
    :return: Give value of line, otherwise False
    """
    res = False
    max_line = number_line_dictionary(name)
    # x is a cursor
    x = 1

    # Check if dictionary exists, otherwise return False
    if dictionary_exist(name):
        f = open("./dictionary/" + name + ".dict")
    else:
        return False

    # Check if line is not upper to maximum line
    if line > max_line:
        return res

    # This loop parse line per line the dictionary and cursor 'x' is incremented here
    # when x is equal to line number, returned variable is modified by the value of line
    for l in f:
        if x == line:
            res = l.replace("\n", "")
            break
        x += 1
    return res


def is_number(s):
    try:
        float(s) # for int, long and float
    except ValueError:
        try:
            complex(s) # for complex
        except ValueError:
            return False
    return True


def decimal_9(n_loop):
    """
    :param n_loop: number of loop
    :return: max value decimal
    """
    result = '0'
    for loop in range(0, n_loop):
        result += '9'
    return int(result)


def filter_args_number(type_v, args):
    """
    :param args: all argument of term int or double
    """
    limit_maxi = sys.maxsize
    maxi = 1000
    limit_mini = -(sys.maxsize)
    mini = 0
    max_decimal = 50
    decimal = 0
    if len(args) > 0:
        for a in args:
            if re.match("^max=", a):
                val = a.replace('max=', '')
                if not is_number:
                    print("Max value " + val + " is not a number")
                    exit(1)
                if type_v == 'int':
                    x_max = int(float(val))
                elif type_v == 'float':
                    x_max = float(val)
                if x_max <= limit_maxi:
                    maxi = x_max
            if re.match("^min=", a):
                val = a.replace('min=', '')
                if not is_number:
                    print("Min value " + val + " is not a number")
                    exit(1)
                if type_v == 'int':
                    x_min = int(float(val))
                elif type_v == 'float':
                    x_min = float(val)
                if x_min >= limit_mini:
                    mini = x_min
            if re.match("^decimal=", a):
                val = a.replace('decimal=', '')
                if not is_number:
                    print("Max value " + val + " is not a number")
                    exit(1)
                x = int(float(val))
                if not x == 0 and x < max_decimal:
                    decimal = int(float(val))
    if mini == maxi:
            maxi+=1
            print('Change : min is equal to max, max+1')
    elif maxi < mini:
        exchange = mini
        mini = maxi
        maxi = exchange
        print('Change : min = ' + str(mini) + ', max = ' + str(maxi))
    return maxi, mini, decimal_9(decimal)

def number_attr(type_v, args):
    """
    Return random number if type is a int or double
    :param type_v: type of term
    :param maxi: maximum value
    :return: random number, otherwise None if type_v is not defined
    """
    args = args.replace(' ', '')
    args = args.split(',')
    maxi, mini, max_dec = filter_args_number(type_v, args)
    print(maxi, mini, max_dec)
    
    if type_v == "int":
        return random.randrange(mini, maxi)
    elif type_v == "float":
        if max_dec == 0 and mini != maxi:
            return float(str(random.uniform(mini, maxi)))
        else:
            return float(str(random.randrange(int(mini), int(maxi))) + '.' + str(random.randrange(1, max_dec)))
    else:
        return 0


def rand_term(term):
    """
    Give a attribute of the insert and a random value
    :param term: an term (eg. : attribute:type)
    :return: return json with attribute name and value, otherwise False
    """
    # Variables
    params = term.split(':')
    attribute, type_v = params[0], params[1]
    maxi, n = None, 0
    x = (type_v.replace(')', '')).split('(')
    val = None

    # check if user do not have abuse of parentheses
    if len(x) == 2:
        type_v, args = x[0], x[1]

    # Check if variable is not defined or is not approved
    if attribute is None and type_v is None \
            or attribute in BASIC_ATTR:
        return False
    if type_v not in ["int", "float"]:
        max_line = number_line_dictionary(type_v)
        if not max_line:
            return False
        n = random.randrange(1, max_line + 1)

    # set returned value
    if type_v in ["int", "float"]:
        val = number_attr(type_v, args)
    if val is None:
        val = select_line(type_v, n)

    return {'name': attribute, 'value': val}


def is_array_of_string(tab):
    """
    Check if element of array is only string
    :param tab: an Array
    :return: True is all elements of array are string
    """
    for i in tab:
        if not isinstance(i, str):
            return False
    return True


def create_insert(name='', tab=[], loop=1):
    """
    Generate lines of Insert (SQL)
    :param name: name of table
    :param tab: Array with terms
    :param loop: number line generate
    :return: code error if error is find
    """
    if type(name) is str:
        name.replace(' ', '_')
    else:
        return 200

    if not type(loop) is int:
        return 300

    if len(tab) == 0 or not is_array_of_string(tab):
        return 100
    
    if len(tab) > 20:
        return 104
    # Set first insert for test
    res = [rand_term(i) for i in tab if rand_term(i)]

    # TEST
    # check if Array is not empty
    if len(res) == 0:
        return 400
    i = 0

    # check if attribute do not have duplicate
    for x in res:
        ii = 0
        for y in res:
            if x['name'] == y['name'] and i != ii:
                return 404, i, ii
            ii += 1
        i += 1
    all_tab = [res, ]

    # add n-1 loop
    if loop > 1:
        if loop > 50:
            loop = 50
        for i in range(0, loop-1):
            all_tab.append([rand_term(i) for i in tab if rand_term(i)])
    _generate_file_insert(name, all_tab)


def _generate_file_insert(name, all_tab):
    """
    Generate a file of insert with multiples args.
    :param: Contain args of 
    """
    # check if directory insert exists, otherwise he create this directory
    if not os.path.exists('./Insert'):
        os.mkdir(u'./Insert')
    # generate an unique id to name file
    id_file = (str(uuid.uuid4())).replace('-', '_')

    # Create file
    path = "./Insert/" + id_file + "_" + name + ".sql"
    my_file = Path(path)
    if not my_file:
        my_file.touch()

    # write request in the file
    f = open(path, "a+")
    for x in all_tab:
        attr, val = "(", "("
        maxi = len(x)
        i = 1
        for y in x:
            attr += y["name"]
            if isinstance(y["value"], str):
                val += "\'{0}\'".format(y["value"])
            else:
                val += str(y["value"])
            if maxi > i:
                attr += ","
                val += ","
            i += 1
        attr += ")"
        val += ")"
        f.writelines(u"Insert into " + name + attr + u" values " + val + u"\n")
    f.close()

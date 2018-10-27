import os
import os.path as op
import tempfile
from pyswip import Prolog
from pyswip import Functor
from pyswip.prolog import PrologError

DEFAULT_LIMIT = 100

def format_value(value):
    output = ""
    if type(value) is list:
        output = "[ " + ", ".join([format_value(val) for val in value]) + " ]"
    elif type(value) is Functor and value.arity == 2:
        output = "{0}{1}{2}".format(value.args[0], value.name, value.args[1])
    else:
        output = "{}".format(value)

    return output

def format_result(result):
    result = list(result)

    if len(result) == 0:
        return "false."

    if len(result) == 1 and len(result[0]) == 0:
        return "true."

    output = ""
    for res in result:
        for var in res:
            output += var + " = " + format_value(res[var])
        output += " ;\n"
    output = output[:-3] + " ."

    return output

def run(code):
    prolog = Prolog()

    output = []
    ok = True

    tmp = ""
    isQuery = False
    for line in code.split("\n"):
        line = line.strip()
        if line == "":
            continue

        if line[:2] == "?-":
            isQuery = True
            line = line[2:]

        tmp += " " + line

        if tmp[-1] == ".":
            # End of statement
            tmp = tmp[:-1] # Removes "."
            maxresults = DEFAULT_LIMIT
            # Checks for maxresults
            if tmp[-1] == "}":
                tmp = tmp[:-1] # Removes "."
                limitStart = tmp.rfind('{')
                if limitStart == -1:
                    ok = False
                    output.append("ERROR: Found '}' before '.' but opening '{' is missing!")
                else:
                    limit = tmp[limitStart+1:]
                    try:
                        maxresults = int(limit)
                    except:
                        ok = False
                        output.append("ERROR: Invalid limit {" + limit + "}!")
                    tmp = tmp[:limitStart]

            try:
                if isQuery:
                    output.append(format_result(prolog.query(tmp, maxresult=maxresults)))
                else:
                    prolog.assertz(tmp)
            except PrologError as error:
                ok = False
                output.append("ERROR: {}".format(error))

            tmp = ""
            isQuery = False

    return output, ok

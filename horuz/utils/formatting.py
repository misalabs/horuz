import codecs
import json
import traceback


def recursive_items(dictionary):
    for key, value in sorted(dictionary.items()):
        if type(value) is dict:
            yield from recursive_items(value)
        else:
            yield (key, value)


def beautify_query(query, fields=[], output="oj"):
    """
    Prepare the query for the user.
    Parameters
    ----------
    query : ElasticSearch Query
    fields : Fields that nees to be in the result
    output : JSON, Interactive
    """
    data = []
    try:
        if query and query['hits']:
            for hit in query['hits']['hits']:
                source = hit["_source"]
                d = source
                d["_id"] = hit["_id"]
                data.append(d)
    except Exception as e:
        raise ValueError("""
            Query term is malformed.
            Exception: %r
            Traceback: %s
            """ % (e, traceback.format_exc()))

    if output == "json":
        data = json.dumps(data, indent=4, sort_keys=True)
    elif output == "interactive":
        new_data = []
        for d in data:
            new_d = {}
            for key, value in recursive_items(d):
                new_d[key] = codecs.decode(str(value), "unicode_escape")
            new_data.append(new_d)
        data = new_data
    return data

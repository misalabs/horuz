import codecs
import json
import traceback


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
                # raise ValueError(hit)
                source = hit["_source"]
                if fields:
                    d = {}
                    for field in fields:
                        try:
                            d[field] = hit[field]
                        except KeyError:
                            try:
                                d[field] = source[field]
                            except KeyError:
                                if output == "json":
                                    try:
                                        if "result" not in d:
                                            d["result"] = {}
                                        d["result"][field] = source['result'][field]
                                        if field == "html":
                                            d["result"]["html"] = codecs.decode(
                                                d["result"]["html"], "unicode_escape")
                                    except (KeyError, TypeError):
                                        pass
                                elif output == "interactive":
                                    try:
                                        d["result.{}".format(field)] = source['result'][field]
                                        if field == "html":
                                            d["result.{}".format(field)] = codecs.decode(
                                                d["result.{}".format(field)]["html"], "unicode_escape")
                                    except (KeyError, TypeError):
                                        pass
                else:
                    d = {'_id': hit["_id"]}
                    d.update(source)
                data.append(d)
    except Exception as e:
        raise ValueError("""
            Query term is malformed.
            Exception: %r
            Traceback: %s
            """ % (e, traceback.format_exc()))

    if output == "json":
        data = json.dumps(data, indent=4, sort_keys=True)
    return data

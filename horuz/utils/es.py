import datetime
import json

import click
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.exceptions import RequestError, ConnectionError, ConnectionTimeout

from horuz.utils.generators import get_random_name


class ElasticSearchAPI:
    """
    Interaction with our Elasticsearch server
    """

    def __init__(self, address, ctx):
        """
        Interact with ES.
        Parameters
        ----------
        address : string
            ElasticSearch Address
        ctx : Environment Class
            cli env class
        """
        try:
            self.es = Elasticsearch(
                address, connection_class=RequestsHttpConnection)
        except (ConnectionError, ConnectionTimeout):
            self.ctx.log("Error init connection ES") 
        except Exception as e:
            self.ctx.log("Error init ES {}".format(e))
            self.es = None
        self.ctx = ctx

    def create_index(self, name):
        """
        Create the index in our ES Server.
        Parameters
        ----------
        name : String
            Index Name
        Returns
        -------
        boolean
            created or not
        """
        created = False
        try:
            if not self.es.indices.exists(name):
                self.es.indices.create(index=name, ignore=400)
            created = True
        except (ConnectionError, ConnectionTimeout):
            self.ctx.log("Create index connection error")
        except Exception as e:
            self.ctx.log("Create index error {}".format(e))      
        finally:
            return created

    def delete_index(self, index):
        """
        Delete the index
        Parameters
        ----------
        Index : String
            Index name
        Returns
        -------
        boolean
            deleted or not
        """
        deleted = False
        try:
            self.es.indices.delete(index=index, ignore=[400, 404])
            deleted = True
        except Exception as e:
            self.ctx.log("Delete index error {}".format(e))
        finally:
            return deleted

    def save_in_index(self, index, record):
        """
        Save the information in the specified index.
        Parameters
        ----------
        index : String
            Index Name
        record : json
            The information we want to save
        Returns
        -------
        boolean
            saved or not
        """
        # Validate if the index exists. If not create
        self.create_index(index)
        saved = False
        try:
            self.es.index(index=index, body=record)
            saved = True
        except (ConnectionError, ConnectionTimeout):
            self.ctx.log("Save index connection error")  
        except Exception as e:
            self.ctx.log("Save index error {}".format(e))
        finally:
            return saved

    def get_all_indexes(self):
        """
        Get all Indexes in ElasticSeach
        """
        return self.es.indices.get_alias()

    def get_index_mapping(self, index):
        """
        Get the index mappping
        Parameters
        ----------
        index : String
            Index Name
        Returns
        -------
        json
        """
        try:
            return self.es.indices.get_mapping(index)
        except Exception as e:
            self.ctx.vlog("Mapping error {}".format(e))

    def query(self, index, term, size=100, raw=False, fields=[]):
        """
        Search in Elasticsearch server
        Parameters
        ----------
        index : String
            Index Name
        term : String
            Search Query
        size : String
            Size query search
        fields : List
            A list of fields of the source
        """
        self.create_index(index)
        if raw is False:
            self.ctx.vlog("ElasticSeach Lucene: {}".format(term))
            if term:
                try:
                    return self.es.search(
                        index=index,
                        q=term,
                        sort=["time:desc"],
                        size=size,
                        _source=fields)
                except (RequestError, ConnectionError, ConnectionTimeout) as e:
                    self.ctx.vlog("Query Error {}".format(e))
        else:
            search_args = {"index": index, "body": term}
            self.ctx.vlog("ElasticSeach Query Raw: {}".format(search_args))
            try:
                return self.es.search(**search_args)
            except (RequestError, ConnectionError, ConnectionTimeout) as e:
                self.ctx.vlog("Query Error {}".format(e))

    def connected(self):
        try:
            self.es.cluster.health()
            return True
        except Exception:
            return False


class HoruzES:
    """
    Horuz ElasticSearch connection
    """
    def __init__(self, domain, ctx=None):
        self.es = ElasticSearchAPI(ctx.config.get("elasticsearch_address"), ctx)
        self.domain = domain
        self.ctx = ctx

    def save_ffuf_data(self, data, session):
        """
        Save ffuf data to ES
        Parameters
        ----------
        data : Dict
            Json data
        session : String
            Session name
        """
        session = session if session else get_random_name()
        config_url = data["config"]["url"].replace("FUZZ", "")
        # If data is saved, we do not save it again
        record_exists = self.es.query(
            index=self.domain,
            term='''
                host: "*{}" AND time: {} AND type: ffuf
            '''.format(
                config_url.replace("/", '').replace("http:", ''),
               data["time"]))
        if record_exists and record_exists['hits']['hits']:
            self.ctx.vlog("Record {} {} exists: ", config_url, data["time"], record_exists)
            return
        # Save the new data
        es_data = {
            "host": config_url,
            "time": data.get("time"),
            "type": "ffuf",
            "session": session,
            "cmd": data.get("commandline"),
            "result": []
        }
        # Save the new data
        len_results = len(data.get("results"))
        if data.get("results"):
            with click.progressbar(data["results"], label='Collecting data for session: {}'.format(session)) as results:
                for result in results:
                    es_data["result"] = result
                    # Get request/response data
                    es_data["result"]["html"] = ""
                    if "outputdirectory" in data["config"] and data["config"]["outputdirectory"]:
                        try:
                            with open("{}/{}".format(data["config"]["outputdirectory"], result["resultfile"]), encoding="utf-8", errors="ignore") as f:
                                es_data["result"]["html"] = f.read()
                        except FileNotFoundError:
                            self.ctx.vlog("Could not open file")
                    self.ctx.vlog(es_data)
                    # Saving to ES
                    self.es.save_in_index(self.domain, es_data)

        else:
            self.ctx.vlog(es_data)
            self.es.save_in_index(self.domain, es_data)
        self.ctx.log("\nProject name: {}".format(self.domain))
        self.ctx.log("\nSession name: {}".format(session))
        self.ctx.log("Results: {}".format(len_results))
        return

    def save_general_data(self, data, session):
        """
        Save General JSON data
        """
        session = session if session else get_random_name()
        with click.progressbar(data, label='Collecting data for session: {}'.format(session)) as results:
            for d in results:
                d.update({
                    "time": datetime.datetime.now(),
                    "session": session})
                self.ctx.vlog(d)
                self.es.save_in_index(self.domain, d)
        self.ctx.log("\nProject name: {}".format(self.domain))
        self.ctx.log("\nSession name: {}".format(session))
        self.ctx.log("Results: {}".format(len(data)))

    def save_json(self, files, session):
        """
        Save JSON Data to ES.
        """
        for filepath in files:
            with open(filepath, "r") as fp:
                data = {}
                try:
                    data = json.load(fp)
                except json.decoder.JSONDecodeError:
                    self.ctx.vlog("Error decoding the JSON Data")
                    continue
                if "ffuf" in str(data):
                    self.save_ffuf_data(data, session)
                else:
                    self.save_general_data(data, session)
        return

    def query(self, term, size=100, raw=False, fields=[]):
        """
        Send Queries to ES
        """
        q = None
        self.ctx.vlog("Sending the query '{}' to ElasticSeach.".format(term))
        try:
            q = self.es.query(self.domain, term, size, raw, fields)
        except Exception as e:
            self.ctx.log("Query connection failed: {}!".format(e))
            self.ctx.vlog("{}!".format(e))

        return q

    def delete(self):
        """
        Delete and Index from ES
        """
        d = None
        try:
            d = self.es.delete_index(self.domain)
        except Exception:
            self.ctx.log("Query connection failed!")
        return d

    def indexes(self):
        """
        Get all Indexes from ES.
        """
        s = None
        try:
            s = sorted(self.es.get_all_indexes().keys())
        except Exception:
            self.ctx.log("Query connection failed!")
        return s

    def project_mapping(self):
        """
        Get the mapping indexes
        """
        mapping = []
        try:
            props = self.es.get_index_mapping(self.domain)
            if props:
                for p in props[self.domain]["mappings"]["properties"].keys():
                    if "properties" in props[self.domain]["mappings"]["properties"][p].keys():
                        for pin in props[self.domain]["mappings"]["properties"][p]["properties"].keys():
                            mapping.append("{}.{}".format(p, pin))
                    else:
                        mapping.append(p)
        except Exception as e:
            self.ctx.log("Mapping connection failed! {}".format(e))
        return mapping

    def is_connected(self):
        """
        Check if ES is connected
        """
        return self.es.connected()

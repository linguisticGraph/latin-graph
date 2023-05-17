from neo4j import GraphDatabase, basic_auth
import time
import json

class Neo4jConnection:

    def __init__(self, uri, user, pwd, db):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.db = db
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=basic_auth(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if self.db is not None else self.__driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

class Exporter:

    def __init__(self, uri, user, password, db):
        self.conn = Neo4jConnection(uri=uri,
                               user=user,
                               pwd=password,
                               db=db)

    def close(self):
        self.conn.close()

    def create_query(self,fname):
        query = "CREATE\n"
        with open(fname) as f:
            for line in f:
                line = json.loads(line)
                properties = line['properties']
                new_properties = ""
                if len(properties) > 0:
                    new_properties = "{"
                    for k in properties:
                        v = properties[k]
                        if type(v) == str:
                            v = v.replace("'","")
                            new_properties = new_properties + f"{k}: '{v}', "
                        else:
                            new_properties = new_properties + f"{k}: {v}, "
                    new_properties = new_properties[:-2]+"}"
                if line['jtype'] == 'node':
                    query = query + f"(id{line['identity']}:{line['label']} {new_properties}),\n"
                else:
                    query = query + f"(id{line['subject']})-[:{line['name']} {new_properties}]->(id{line['object']}),\n"

        query = query[:-2]
        return self.insert_data(query)

    def insert_data(self, query):
        resp = self.conn.query(query)
        return resp



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Export 2 Neo4j',
        description="Export JSONL dump to Neo4j database")

    parser.add_argument('--address',default='')
    parser.add_argument('--port',default='')
    parser.add_argument('--db', default='')
    parser.add_argument('--user', default='')
    parser.add_argument('--password', default='')
    parser.add_argument('--dump', default='')
    args = parser.parse_args()


    e = Exporter(f'neo4j://{args.address}:{args.port}',args.user,args.password,args.db)
    e.create_query(args.dump)
    e.close()
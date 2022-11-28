from neo4j import GraphDatabase
import csv


#establish connection
def neo_connect():
    with open("utils/cred.txt") as file1:
        data = csv.reader(file1, delimiter=",")
        for row in data:
            username = row[0]
            pswd = row[1]
            uri = row[2]
    print(username, pswd, uri)
    driver = GraphDatabase.driver(uri=uri, auth=(username, pswd))
    session = driver.session()
    return session

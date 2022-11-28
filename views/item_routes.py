from application import app
from flask import request, jsonify
import uuid

from utils.neo_connector import neo_connect
session = neo_connect()


#ITEM API'S

@app.route("/getallitems", methods=["GET"])
def get_all_items():
    query1 = """
    MATCH (n:Item) 
    WITH n
    MATCH (n)-[r1:STAMPED_AS]->(s), (n)-[r2:CATEGORIZED_AS]->(m), (n)-[r3:CLASSED_AS]->(c)
    RETURN n.title as title,
                    n.node_id as node_id,
                    n.author as author,
                    n.date_acquired as date_acquired,
                    n.replacement_cost as replacement_cost,
                    n.fine_rate as fine_rate,
                    n.yr_published as year_published,
                    s.type as status,
                    m.type as media,
                    c.type as classification
    """
    results = session.run(query1)
    data = results.data()
    return jsonify(data)


@app.route("/createitem", methods=["POST"])
def create_item():
    json_data = request.get_json()
    print(json_data)
    title = json_data['title']
    search_title = title.lower()
    author = json_data['author']
    date_acquired = json_data['date_acquired']
    replacement_cost = json_data['replacement_cost']
    fine_rate = json_data['fine_rate']
    yr_published = json_data['yr_published']
    node_id = uuid.uuid4()
    status = json_data['status']
    status_id = uuid.uuid4()
    media = json_data['media']
    media_id = uuid.uuid4()
    classed = json_data['classed']
    classed_id = uuid.uuid4()

    query1 = """
    create (n:Item{title:$title, 
                    search_title:$search_title,
                    node_id:$node_id,
                    author:$author,
                    date_acquired:$date_acquired,
                    replacement_cost:$replacement_cost,
                    fine_rate:$fine_rate,
                    yr_published:$yr_published}) 
    MERGE (s:Status {type:$status}) 
        ON CREATE SET s.status_id = $status_id 
    MERGE (m:Media {type:$media})
        ON CREATE SET m.media_id = $media_id
    MERGE (c:Classification {type:$classed})
        ON CREATE SET c.classed_id = $classed_id
    CREATE (n)-[:STAMPED_AS]->(s), (n)-[:CATEGORIZED_AS]->(m), (n)-[:CLASSED_AS]->(c) 
    """

    map = {"title": title,
           "search_title": search_title,
           "node_id": str(node_id),
           "author": author,
           "date_acquired": date_acquired,
           "replacement_cost": replacement_cost,
           "fine_rate": fine_rate,
           "yr_published": yr_published,
           "status": status,
           "status_id": str(status_id),
           "media": media,
           "media_id": str(media_id),
           "classed": classed,
           "classed_id": str(classed_id)
           }
    try:
        session.run(query1, map)
        return (f"Item node created with name: {title} and node_id: {node_id}")
    except Exception as e:
        return (str(e))


@app.route("/getitemdetail/<string:node_id>", methods=["GET"])
def get_item_detail(node_id):
    query1 = """
    MATCH (n: Item{node_id:$node_id}) 
    WITH n
    MATCH (n)-[r1:STAMPED_AS]->(s), (n)-[r2:CATEGORIZED_AS]->(m), (n)-[r3:CLASSED_AS]->(c)
    RETURN n.title as title,
                    n.node_id as node_id,
                    n.author as author,
                    n.date_acquired as date_acquired,
                    n.replacement_cost as replacement_cost,
                    n.fine_rate as fine_rate,
                    n.yr_published as year_published,
                    s.type as status,
                    m.type as media,
                    c.type as classification
    """
    map = {"node_id": node_id}

    results = session.run(query1, map)
    data = results.data()
    return jsonify(data)


@app.route("/deleteitem", methods=["POST"])
def delete_item():
    json_data = request.get_json()
    print(json_data)
    node_id = json_data['node_id']
    query1 = """
     MATCH (n: Item{node_id:$node_id}) DETACH DELETE n
    """
    map = {"node_id": node_id,
           }
    try:
        session.run(query1, map)
        return (f"Item node deleted with id: {node_id}")
    except Exception as e:
        return (str(e))


@app.route("/updateitem", methods=["POST"])
def update_item():
    json_data = request.get_json()
    print(json_data)
    title = json_data['title']
    author = json_data['author']
    date_acquired = json_data['date_acquired']
    replacement_cost = json_data['replacement_cost']
    fine_rate = json_data['fine_rate']
    yr_published = json_data['yr_published']
    node_id = json_data['node_id']
    status = json_data['status']
    status_id = uuid.uuid4()
    media = json_data['media']
    media_id = uuid.uuid4()
    classed = json_data['classed']
    classed_id = uuid.uuid4()

    query1 = """
    MATCH (n:Item{node_id:$node_id}) 
    SET n.title = $title,
        n.search_title = $search_title, 
        n.author = $author,
        n.date_acquired = $date_acquired,
        n.replacement_cost = $replacement_cost,
        n.fine_rate = $fine_rate,
        n.yr_published = $yr_published
    WITH n
    MATCH (n)-[r1:STAMPED_AS]->(), (n)-[r2:CATEGORIZED_AS]->(), (n)-[r3:CLASSED_AS]->() DELETE r1, r2, r3
    MERGE (s:Status {type:$status}) 
        ON CREATE SET s.status_id = $status_id 
    MERGE (m:Media {type:$media})
        ON CREATE SET m.media_id = $media_id
    MERGE (c:Classification {type:$classed})
        ON CREATE SET c.classed_id = $classed_id
    CREATE (n)-[:STAMPED_AS]->(s), (n)-[:CATEGORIZED_AS]->(m), (n)-[:CLASSED_AS]->(c)
    """

    map = {"title": title,
           "search_title": title.lower(),
           "author": author,
           "date_acquired": date_acquired,
           "replacement_cost": replacement_cost,
           "fine_rate": fine_rate,
           "yr_published": yr_published,
           "node_id": node_id,
           "status": status,
           "status_id": str(status_id),
           "media": media,
           "media_id": str(media_id),
           "classed": classed,
           "classed_id": str(classed_id)
           }
    try:
        session.run(query1, map)
        return (f"Item node updated with title: {title} and node_id {node_id}")
    except Exception as e:
        return (str(e))


#STATUS/MEDIA/CLASSIFICATION API'S

@app.route("/getallstatus", methods=["GET"])
def get_all_status():
    query1 = """
    MATCH (n:Status) RETURN n.type as status,
                    n.status_id as id
    """
    results = session.run(query1)
    data = results.data()
    return jsonify(data)


@app.route("/getallmedia", methods=["GET"])
def get_all_media():
    query1 = """
    MATCH (n:Media) RETURN n.type as media,
                    n.media_id as id
    """
    results = session.run(query1)
    data = results.data()
    return jsonify(data)


@app.route("/getallclassed", methods=["GET"])
def get_all_classed():
    query1 = """
    MATCH (n:Classification) RETURN n.type as classification,
                    n.classed_id as id
    """
    results = session.run(query1)
    data = results.data()
    return jsonify(data)


@app.route("/filteritems", methods=["POST"])
def get_filtered_items():
    json_data = request.get_json()
    print('JSON DATA********')
    print(json_data)
    title = json_data['title']
    author = json_data['author']
    yr_published = json_data['yr_published']
    status = json_data['status']
    terms = []
    status_data = ''

    if title != '':
        terms.append(f'n.title = "{title}" ')
    if author != '':
        terms.append(f'n.author = "{author}" ')
    if yr_published != '':
        terms.append(f'n.yr_published = "{yr_published}"')
    if status != 'Select Status':
        status_data = ('-[:STAMPED_AS]->(s:Status{type:"' + f'{status}' + '"})')
        print(status_data)

    if title == '' and author == '' and yr_published == '':
        search_data = ''
    else:
        search_terms = ' AND '.join(terms)
        search_data = " WHERE " + search_terms
        print('SEARCH DATA********')
        print(search_data)

    query = """
        MATCH (n:Item)""" + status_data + """
        """ + search_data + """ 
        MATCH (n)-[r:STAMPED_AS]->(s), (n)-[r2:CATEGORIZED_AS]->(m), (n)-[r3:CLASSED_AS]->(c)
        RETURN n.title as title,
                        n.node_id as node_id,
                        n.author as author,
                        n.date_acquired as date_acquired,
                        n.replacement_cost as replacement_cost,
                        n.fine_rate as fine_rate,
                        n.yr_published as year_published,
                        s.type as status,
                        m.type as media,
                        c.type as classification
        """
    print(query)

    results = session.run(query)
    data = results.data()

    print('PRINT DATA')
    print(data)
    return jsonify(data)


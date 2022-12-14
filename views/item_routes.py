import datetime
from datetime import datetime
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
                    toString(n.date_acquired) as date_acquired,
                    n.replacement_cost as replacement_cost,
                    n.fine_rate as fine_rate,
                    n.yr_published as year_published,
                    n.days_for_loan as dfl,
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
    #mock = json_data['mock']
    title = json_data['title']
    author = json_data['author']
    date_acquired = json_data['date_acquired']
    replacement_cost = json_data['replacement_cost']
    fine_rate = json_data['fine_rate']
    dfl = json_data['dfl']
    if dfl == '':
        dfl = 30
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
                    search_author:$search_author,
                    date_acquired:$date($date_acquired),
                    replacement_cost:$replacement_cost,
                    fine_rate:$fine_rate,
                    days_for_loan:$dfl,
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
           "search_title": title.lower(),
           "node_id": str(node_id),
           "author": author,
           "search_author": author.lower(),
           "date_acquired": date_acquired,
           "replacement_cost": replacement_cost,
           "fine_rate": fine_rate,
           "dfl": dfl,
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
                    toString(n.date_acquired) as date_acquired,
                    n.replacement_cost as replacement_cost,
                    n.fine_rate as fine_rate,
                    n.yr_published as year_published,
                    n.days_for_loan as dfl,
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
    #mock = json_data['mock']
    author = json_data['author']
    date_acquired = json_data['date_acquired']
    replacement_cost = json_data['replacement_cost']
    fine_rate = json_data['fine_rate']
    dfl = json_data['dfl']
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
        n.search_author = $search_author,
        n.date_acquired = date($date_acquired),
        n.replacement_cost = $replacement_cost,
        n.days_for_loan = $dfl,
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
           "search_author": author.lower(),
           "date_acquired": date_acquired,
           "replacement_cost": replacement_cost,
           "fine_rate": fine_rate,
           "dfl": dfl,
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
        terms.append(f'n.search_title = "{title}" ')
    if author != '':
        terms.append(f'n.search_author = "{author}" ')
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
                        toString(n.date_acquired) as date_acquired,
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


@app.route("/getonloanto/<string:node_id>", methods=["GET"])
def get_on_loan_to(node_id):
    query1 = """
    MATCH (i: Item{node_id:$node_id})-[:STAMPED_AS]->(s:Status{type:"On Loan"})
    WITH i 
    MATCH (i)<-[r:BORROWED]-(n:User)
    WHERE r.status = "active"
    WITH n,r
    RETURN n.f_name as f_name,
                    n.l_name as l_name,
                    n.user_id as user_id,
                    n.email as email,
                    n.address as address,
                    n.dob as dob,
                    n.tel as tel,
                    toString(r.date_borrowed) as date_borrowed,
                    toString(r.date_due) as due_date,
                    r.overdue as overdue,
                    r.days_overdue as days_overdue
    """
    map = {"node_id": node_id}

    results = session.run(query1, map)
    data = results.data()
    print(data)
    return jsonify(data)


@app.route("/checkborrowed", methods=["GET"])
def check_borrowed_items():
    query1 = """
    MATCH (i:Item)<-[r:BORROWED]-(n:User)
    WHERE r.status = "active"
    RETURN n.f_name as f_name,
                    n.l_name as l_name,
                    n.user_id as user_id,
                    n.email as email,
                    toString(r.date_borrowed) as date_borrowed,
                    toString(r.date_due) as due_date,
                    r.rel_id as borrowed_id,
                    r.overdue as overdue,
                    i.title as title,
                    i.node_id as node_id,
                    i.author as author,
                    toString(i.date_acquired) as date_acquired,
                    i.replacement_cost as replacement_cost,
                    i.fine_rate as fine_rate,
                    i.yr_published as year_published
                        
    """

    results = session.run(query1)
    data = results.data()
    return jsonify(data)


@app.route("/overdueitem", methods=["POST"])
def overdue_item():
    json_data = request.get_json()
    print(json_data)
    node_id = json_data['node_id']
    #user_id = json_data['user_id']
    borrowed_id = json_data['borrowed_id']
    days_overdue = json_data['days_overdue']
    overdue = True

    query1 = """
     MATCH (u)-[r:BORROWED]->(i)
     WHERE r.rel_id = $borrowed_id
     SET r.overdue = $overdue, r.days_overdue = $days_overdue
     RETURN r.rel_id as borrowed_id,
            r.overdue as overdue,
            r.days_overdue as days_overdue
    """
    map = {"borrowed_id": borrowed_id,
           "overdue": overdue,
           "days_overdue": days_overdue
           }
    try:
        session.run(query1, map)
        return (f"Item {node_id} set to overdue with borrowed_id: {borrowed_id} by {days_overdue} days ")
    except Exception as e:
        return (str(e))



@app.route("/issueoverduefine", methods=["POST"])
def issue_overdue_fine():
    #for json data - need user id (and item id?)
    json_data = request.get_json()
    print(json_data)
    node_id = json_data['node_id']
    user_id = json_data['user_id']
    fine_rate = json_data['fine_rate']
    reason = json_data['reason']
    fine_id = uuid.uuid4()
    date_issued = datetime.now()
    fine_status = "active"
    issued_to_id = uuid.uuid4()
    issued_for_id = uuid.uuid4()

    query1 = """
     MATCH (i: Item{node_id:$node_id})
     MATCH (u: User{user_id:$user_id})
     CREATE (u)<-[r1:ISSUED_TO]-(f:Fine)-[r2:ISSUED_FOR]->(i)
     SET f.fine_id = $fine_id,
             f.fine_rate = $fine_rate,
             f.reason = $reason,
             f.date_issued = date($date_issued),
             f.fine_status = $fine_status,
             r1.issued_to_id = $issued_to_id,
             r2.issued_for_id = $issued_for_id
    """
    map = {"node_id": node_id,
           "user_id": user_id,
           "fine_rate": fine_rate,
           "reason": reason,
           "fine_id": str(fine_id),
           "date_issued": date_issued,
           "fine_status": fine_status,
           "issued_to_id": str(issued_to_id),
           "issued_for_id": str(issued_for_id)
           }
    try:
        session.run(query1, map)
        return f"fine issued for user id: {user_id} for {reason}, amount:{fine_rate} per day, fine status is: {fine_status}"
    except Exception as e:
        print(str(e))
        return str(e)


@app.route("/getfineid/<string:node_id><string:user_id>", methods=["GET"])
def get_fine_id(node_id, user_id):
    query1 = """
     MATCH (u: User{user_id:$user_id})<-[r1:ISSUED_TO]-(f:Fine)-[r2:ISSUED_FOR]->(i: Item{node_id:$node_id})
        WHERE f.fine_status = "active"
        RETURN f.fine_id as fine_id,
            f.reason as reason,
            f.fine_status as status
        """

    map = {
        "node_id": node_id,
        "user_id": user_id
    }

    results = session.run(query1, map)
    data = results.data()
    return jsonify(data)
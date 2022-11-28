from application import app
from flask import request, jsonify
import uuid
from datetime import datetime, timedelta

from utils.neo_connector import neo_connect
session = neo_connect()


#USER API'S

@app.route("/getallusers", methods=["GET"])
def get_all_users():
    query1 = """
    MATCH (n: User)
    OPTIONAL MATCH (n)-[r:BORROWED{status:"active"}]->() 
    RETURN DISTINCT n.f_name as f_name,
                    n.l_name as l_name,
                    n.user_id as user_id,
                    n.email as email,
                    n.address as address,
                    n.dob as dob,
                    n.tel as tel, 
                    r.status as borrowed_status        
    """
    results = session.run(query1)
    data = results.data()
    return jsonify(data)


@app.route("/createuser", methods=["POST"])
def create_node():
    json_data = request.get_json()
    print(json_data)
    f_name = json_data['f_name']
    l_name = json_data['l_name']
    email = json_data['email']
    address = json_data['address']
    dob = json_data['dob']
    tel = json_data['tel']
    id_provided = json_data['id_provided']
    user_id = uuid.uuid4()
    password = 'tempPassword' # call secure password generator function and hash password to store on database

    #Run first query to check if email exists in database - if it does send back error message

    query1 = """
    create (n:User{f_name:$f_name, 
            l_name:$l_name,
            user_id:$user_id,
            email:$email,
            password:$password,
            address:$address,
            dob:$dob,
            tel:$tel,
            id_provided:$id_provided
            })
    """
    map = {"f_name": f_name,
           "l_name": l_name,
           "email": email,
           "address": address,
           "dob": dob,
           "tel": tel,
           "id_provided": id_provided,
           "user_id": str(user_id),
           "password": password
           }
    try:
        session.run(query1, map)
        return (f"User node created with name: {f_name} {l_name} and node_id: {user_id}")
    except Exception as e:
        return (str(e))


@app.route("/getuserdetail/<string:user_id>", methods=["GET"])
def get_user_detail(user_id):
    query1 = """
    MATCH (n: User{user_id:$user_id})
    RETURN n.f_name as f_name,
                    n.l_name as l_name,
                    n.user_id as user_id,
                    n.email as email,
                    n.address as address,
                    n.dob as dob,
                    n.tel as tel
    """
    map = {"user_id": user_id}

    results = session.run(query1, map)
    data = results.data()
    return jsonify(data)


@app.route("/deleteuser", methods=["POST"])
def delete_user():
    json_data = request.get_json()
    print(json_data)
    user_id = json_data['user_id']
    query1 = """
     MATCH (n: User{user_id:$user_id}) DELETE n
    """
    map = {"user_id": user_id}

    try:
        session.run(query1, map)
        return (f"User node deleted with node_id: {user_id}")
    except Exception as e:
        return (str(e))


@app.route("/updateuser", methods=["POST"])
def update_user():
    json_data = request.get_json()
    print(json_data)
    user_id = json_data['user_id']
    f_name = json_data['f_name']
    l_name = json_data['l_name']
    email = json_data['email']
    address = json_data['address']
    dob = json_data['dob']
    tel = json_data['tel']
    query1 = """
    MATCH (n:User{user_id:$user_id})
        SET n.f_name = $f_name, 
            n.l_name = $l_name,
            n.email = $email,
            n.address = $address,
            n.dob = $dob,
            n.tel = $tel
    """
    map = {"f_name": f_name,
           "l_name": l_name,
           "email": email,
           "address": address,
           "dob": dob,
           "tel": tel,
           "user_id": user_id
           }
    try:
        session.run(query1, map)
        return (f"User node updated with name: {f_name} {l_name} and node_id: {user_id}")
    except Exception as e:
        return (str(e))


@app.route("/borrowitem", methods=["POST"])
def borrow_item():
    json_data = request.get_json()
    print(json_data)
    user_id = json_data['user_id']
    node_id = json_data['node_id']
    days_for_loan = 30
    rel_id = uuid.uuid4()
    get_date = datetime.now()
    date_borrowed = get_date.strftime("%d,%m,%Y")
    get_due_date = datetime.now() + timedelta(days=days_for_loan)
    date_due = get_due_date.strftime("%d,%m,%Y")

    query = """
    MATCH (n:Item{node_id:$node_id})-[:STAMPED_AS]-(s)
    RETURN s.type as Status
    """

    query1 = """
    MATCH (u:User{user_id:$user_id})
    MATCH (n:Item{node_id:$node_id})
    CREATE (u)-[r:BORROWED { rel_id:$rel_id, date_borrowed:$date_borrowed, date_due:$date_due, status:"active" }]->(n)
    WITH n
    MATCH (n)-[r1:STAMPED_AS]->() DELETE r1
    MERGE (s:Status {type:"On Loan"}) 
    MERGE (n)-[r2:STAMPED_AS]->(s)
    """

    map = {"node_id": node_id,
           "rel_id": str(rel_id),
           "date_borrowed": date_borrowed,
           "date_due": date_due,
           "user_id": user_id
           }

    results = session.run(query, map)
    data = results.data()
    if data[0]['Status'] == 'Available':
        try:
            session.run(query1, map)
            return (f"user Id:{user_id} borrowed item id: {node_id}")
        except Exception as e:
            return (str(e))
    else:
        return 'Item is unavailable'


@app.route("/returnitem", methods=["POST"])
def return_item():
    json_data = request.get_json()
    print(json_data)
    user_id = json_data['user_id']
    node_id = json_data['node_id']
    rel_id = uuid.uuid4()
    get_date = datetime.now()
    date_returned = get_date.strftime("%d,%m,%Y,%H,%M")

    query1 = """
    MATCH (u:User{user_id:$user_id})
    MATCH (n:Item{node_id:$node_id})
    OPTIONAL MATCH (u)-[r3:BORROWED]-(n)
    SET r3.status = "inactive"
    CREATE (u)-[r:RETURNED { rel_id:$rel_id, date_returned:$date_returned }]->(n)
    WITH n
    MATCH (n)-[r1:STAMPED_AS]->() DELETE r1
    MERGE (s:Status {type:"Available"}) 
    MERGE (n)-[r2:STAMPED_AS]->(s)
    """

    map = {"node_id": node_id,
           "rel_id": str(rel_id),
           "date_returned": date_returned,
           "user_id": user_id
           }
    try:
        session.run(query1, map)
        return (f"user Id:{user_id} returned item id: {node_id}")
    except Exception as e:
        return (str(e))


@app.route("/getuserborroweditems/<string:user_id>", methods=["GET"])
def get_user_borrowed_items(user_id):
    query1 = """
    MATCH (u: User{user_id:$user_id})
    WITH u 
    OPTIONAL MATCH (u)-[r:BORROWED]->(n:Item)-[:STAMPED_AS]->(s:Status{type:"On Loan"})
    WHERE r.status = "active"
    OPTIONAL MATCH (n)-[:CATEGORIZED_AS]->(m), (n)-[:CLASSED_AS]->(c)
    RETURN n.title as title,
                    n.node_id as node_id,
                    n.author as author,
                    n.date_acquired as date_acquired,
                    n.replacement_cost as replacement_cost,
                    n.fine_rate as fine_rate,
                    n.yr_published as year_published,
                    s.type as status,
                    m.type as media,
                    c.type as classification,
                    r.date_borrowed as date_borrowed,
                    r.date_due as due_date
    """
    map = {"user_id": user_id}

    results = session.run(query1, map)
    data = results.data()
    return jsonify(data)


from application import app
from flask import request, jsonify, make_response
import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

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
                    toString(n.dob) as dob,
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
    full_name = f_name + '' + l_name
    email = json_data['email']
    address = json_data['address']
    dob = json_data['dob']
    tel = json_data['tel']
    id_provided = json_data['id_provided']
    user_id = uuid.uuid4()
    password = generate_password_hash(json_data['password'])

    query1 = """
    create (n:User{f_name:$f_name, 
            search_f_name:$search_f_name,
            l_name:$l_name,
            search_l_name:$search_l_name,
            search_full_name: $search_full_name,
            user_id:$user_id,
            email:$email,
            password:$password,
            address:$address,
            dob:date($dob),
            tel:$tel,
            id_provided:$id_provided
            })
    """
    map = {"f_name": f_name,
           "search_f_name": f_name.lower(),
           "l_name": l_name,
           "search_l_name": l_name.lower(),
           "search_full_name": full_name.lower(),
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
        return (f"Member created with name: {f_name} {l_name} and node_id: {user_id}")
    except Exception as e:
        return str(e)


@app.route("/getuserdetail/<string:user_id>", methods=["GET"])
def get_user_detail(user_id):
    query1 = """
    MATCH (n: User{user_id:$user_id})
    RETURN n.f_name as f_name,
                    n.l_name as l_name,
                    n.user_id as user_id,
                    n.email as email,
                    n.address as address,
                    toString(n.dob) as dob,
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
    full_name = f_name + '' + l_name
    email = json_data['email']
    address = json_data['address']
    dob = json_data['dob']
    tel = json_data['tel']
    query1 = """
    MATCH (n:User{user_id:$user_id})
        SET n.f_name = $f_name,
            n.search_f_name = $search_f_name,
            n.l_name = $l_name,
            n.search_l_name = $search_l_name,
            n.search_full_name = $search_full_name,
            n.email = $email,
            n.address = $address,
            n.dob = date($dob),
            n.tel = $tel
    """
    map = {"f_name": f_name,
           "search_f_name": f_name.lower(),
           "l_name": l_name,
           "search_l_name": l_name.lower(),
           "search_full_name": full_name.lower(),
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
    print('BORROW CALLED *******')
    json_data = request.get_json()
    print(json_data)
    user_id = json_data['user_id']
    node_id = json_data['node_id']
    if json_data['dfl'] != '':
        days_for_loan = int(json_data['dfl'])
    else:
        days_for_loan = 30
    rel_id = uuid.uuid4()
    date_borrowed = datetime.now()
    date_due = datetime.now() + timedelta(days=days_for_loan)
    overdue = False
    days_overdue = 0

    query = """
    MATCH (n:Item{node_id:$node_id})-[:STAMPED_AS]-(s)
    RETURN s.type as Status
    """

    query1 = """
    MATCH (u:User{user_id:$user_id})
    MATCH (n:Item{node_id:$node_id})
    CREATE (u)-[r:BORROWED { rel_id:$rel_id, 
                            date_borrowed:date($date_borrowed), 
                            date_due:date($date_due), 
                            status:"active",
                            days_overdue: $days_overdue, 
                            overdue:$overdue }]->(n)
    WITH n
    MATCH (n)-[r1:STAMPED_AS]->() DELETE r1
    MERGE (s:Status {type:"On Loan"}) 
    MERGE (n)-[r2:STAMPED_AS]->(s)
    """

    map = {"node_id": node_id,
           "rel_id": str(rel_id),
           "date_borrowed": date_borrowed,
           "date_due": date_due,
           "user_id": user_id,
           "overdue": overdue,
           "days_overdue": days_overdue
           }

    results = session.run(query, map)
    data = results.data()
    print(data[0]['Status'])
    if data[0]['Status'] == 'Available':
        try:
            session.run(query1, map)
            print(query1)
            return (f"user Id:{user_id} borrowed item id: {node_id}")
        except Exception as e:
            print('exception raised')
            print(str(e))
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
    date_returned = datetime.now()

    query1 = """
    MATCH (u:User{user_id:$user_id})
    MATCH (n:Item{node_id:$node_id})
    OPTIONAL MATCH (u)-[r3:BORROWED]-(n)
    SET r3.status = "inactive"
    CREATE (u)-[r:RETURNED { rel_id:$rel_id, date_returned:date($date_returned) }]->(n)
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
        print(str(e))
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
                    toString(n.date_acquired) as date_acquired,
                    n.replacement_cost as replacement_cost,
                    n.fine_rate as fine_rate,
                    n.yr_published as year_published,
                    s.type as status,
                    m.type as media,
                    c.type as classification,
                    toString(r.date_borrowed) as date_borrowed,
                    toString(r.date_due) as date_due,
                    r.overdue as overdue
    """
    map = {"user_id": user_id}

    results = session.run(query1, map)
    data = results.data()
    return jsonify(data)


@app.route("/getfines/<string:user_id>", methods=["GET"])
def get_fines(user_id):
    query1 = """
     MATCH (u: User{user_id:$user_id})<-[r1:ISSUED_TO]-(f:Fine)-[r2:ISSUED_FOR]->(i)
        RETURN f.fine_id as fine_id,
            f.reason as reason,
            f.fine_status as status,
            toString(f.date_issued) as date_issued,
            f.fine_rate as fine_rate,
            toString(f.item_due_back) as item_due_back,
            i.title as title,
            i.author as author,
            i.node_id as node_id,
            i.days_for_loan as dfl
        """

    map = {
        "user_id": user_id
    }
    try:
        results = session.run(query1, map)
        data = results.data()
        return jsonify(data)
    except Exception as e:
        print(str(e))
        return str(e)


@app.route("/filtermembers", methods=["POST"])
def get_filtered_members():
    json_data = request.get_json()
    print('JSON DATA********')
    print(json_data)
    f_name = json_data['f_name']
    l_name = json_data['l_name']
    email = json_data['email']
    borrowed = json_data['borrowed']
    terms = []
    status_data = ''
    status_return = ''
    op_borrow = ''

    if f_name != '':
        terms.append(f'n.search_f_name = "{f_name}" ')
    if l_name != '':
        terms.append(f'n.search_l_name = "{l_name}" ')
    if email != '':
        terms.append(f'n.email = "{email}"')
    if borrowed != '':
        if borrowed == 'YES':
            status_data = ('-[r:BORROWED{status:"active"}]->()')
            status_return = ', r.status as borrowed_status'
        elif borrowed == 'NO':
            status_data = ('WHERE NOT (n)-[:BORROWED{status:"active"}]->() WITH n')
        print(status_data)
    else:
        op_borrow = 'OPTIONAL MATCH (n)-[r:BORROWED{status:"active"}]->() WITH n,r'
        status_return = ', r.status as borrowed_status'

    if f_name == '' and l_name == '' and email == '':
        search_data = ''
    else:
        search_terms = ' AND '.join(terms)
        search_data = " WHERE " + search_terms
        print('SEARCH DATA********')
        print(search_data)

    query = """
        MATCH (n:User)""" + status_data + """
        """ + op_borrow + search_data + """ 
        RETURN DISTINCT n.f_name as f_name,
                    n.l_name as l_name,
                    n.user_id as user_id,
                    n.email as email,
                    n.address as address,
                    toString(n.dob) as dob,
                    n.tel as tel""" + status_return + """
        """
    print(query)

    results = session.run(query)
    data = results.data()

    print('PRINT DATA')
    print(data)
    return jsonify(data)


@app.route("/checkemail/<string:email>", methods=["GET"])
def check_email(email):
    query1 = """
    MATCH (n: User)
    WHERE n.email = $email
    RETURN n.email as email    
    """
    map = {'email': email}

    results = session.run(query1, map)
    data = results.data()
    return jsonify(data)


@app.route("/quickfiltermembers/<string:search_request>", methods=["GET"])
def quick_filtered_members(search_request):
    print('JSON DATA********')
    print(search_request)

    query = """
        MATCH (n:User)
        WHERE n.email = $search_request OR n.search_f_name = $search_request 
            OR n.search_last_name = $search_request OR n.search_full_name = $search_request OR n.user_id = $search_request
        RETURN DISTINCT n.f_name as f_name,
                    n.l_name as l_name,
                    n.user_id as user_id,
                    n.email as email,
                    n.address as address,
                    toString(n.dob) as dob,
                    n.tel as tel
        """
    print(query)

    map = {"search_request": search_request.lower()}

    results = session.run(query, map)
    data = results.data()

    print('PRINT DATA')
    print(data)
    return jsonify(data)


@app.route("/memberlostitem", methods=["POST"])
def member_lost_item():
    json_data = request.get_json()
    print(json_data)
    user_id = json_data['user_id']
    node_id = json_data['node_id']

    query1 = """
    MATCH (u:User{user_id:$user_id})-[r3:BORROWED]->(n:Item{node_id:$node_id})
    SET r3.status = "inactive"
    RETURN r3.status as status
    """

    map = {"node_id": node_id,
           "user_id": user_id
           }
    try:
        session.run(query1, map)
        return (f"user Id:{user_id} lost item id: {node_id}")
    except Exception as e:
        print(str(e))
        return (str(e))
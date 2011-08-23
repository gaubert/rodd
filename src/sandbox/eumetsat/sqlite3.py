
from eumetsat.db.rodd_db import DAO, Channel



def main():

    dao = DAO()
    
    session = dao.get_session()
    
    #result = session.query(Channel).filter_by(name='EPS-4').first()
    
    ch = Channel("MyName1","124.124.123.2",5,34,"myFunction")
    
    if not session.query(Channel).filter_by(name='MyName1').first():
        session.add(ch)
    
        session.commit()
    
    result = session.query(Channel).filter_by(name='MyName1').first()
    

    
    print(result)
    

if __name__ == "__main__":
    main()



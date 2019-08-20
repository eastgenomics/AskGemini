import unittest
from extractor import *
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy import create_engine
from zope.sqlalchemy import ZopeTransactionExtension

Session = sessionmaker()
ConnectionString = "mysql://ga_ro:readonly@sql01/genetics_ark_1_1_0"
engine = create_engine(ConnectionString)
#Session.configure(bind=engine)
Base.metadata.create_all(engine)




class TestCalculateGeminiAF(unittest.TestCase):


    def setUp(self):
        # connect to the database
        self.connection = engine.connect()

        # begin a non-ORM transaction
        self.trans = self.connection.begin()

        # bind an individual Session to the connection
        self.session = Session(bind=self.connection)



    #def test_get_variant_id(self):
        #self.assertEqual(ex.get_variant_id(args), 4919366)
        # 5     | 476530 | C    | G
    #   pass

    def test_find_samples_with_variant(self):

        self.session.commit()
        self.assertEqual(find_samples_with_variant(11736653),['cardiac',1052,12941.8,0.48384,1])


    def tearDown(self):
        self.session.close()

        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        self.trans.rollback()

        # return connection to the Engine
        self.connection.close()


if __name__ == '__main__':
    unittest.main()

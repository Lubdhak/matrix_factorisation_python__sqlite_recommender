# matrix_factorisation_python_sqlite_recommender


Features
============

- Configurable number of items in Recommendation
- Considers item if skipped
- Favours new items in Recommedation Generation
- Model can be saved to pickle/sqlite
- Option to set a minimum score
- Can recommend both catagory wise and global products
- User can rate the Product on the Scale of 1 to 5
 

Installation
------------
Data Set
~~~~~~~~~~~~
266 Products
7 catagories
14 user
838 reviews [may differ]
~~~~~~~~~~~~~~~~~


Run Command
~~~~~~~~~~~~
cd matrix_factorisation_python__sqlite_recommender
python3 main.py
~~~~~~~~~~~~~~~~~

Future Development
-----------
- Use of Apiori Algorithm to leverage items that are mostly brought together

Other side of Matrix Factorisation 
-----------
In Matrix Factorisation the weights are learnt by itself which is great when the data is sparse & most traditional model fails to deal with this scenario but over the time when data gets dense there is no scope of improvement cause: 

- We cannot add any extra weight externally
- The vector length is fixed so any feature prior or post User-item interaction cannot be taken into consideration
- All correlation between features are treated naively hence we cannot include any constant or variable human factors into the computation hence it under-fits dense data
- Generalisation is the strength of Matrix Factorisation Models and Also the weakness
- Over the time it’ll start recommending product with very less confidence score
- Appart from Suggestions there are situation like sending Email / Push notifications to the users requires items to have very high confidence score.


Project History
---------------
Started as a part of an Job Assignment - "Tinder for Software Stacks" & i got the job 

Help and Support
----------------
Website: http://qbitdata.in/

Linkedin: https://www.linkedin.com/in/lubdhak/

_Special Thanks to www.analyticsvidhya.com_

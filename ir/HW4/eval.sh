python search.py -d dictionary.txt -p postings.txt -q cs3245-hw4/q1.xml -o result1.txt
python search.py -d dictionary.txt -p postings.txt -q cs3245-hw4/q2.xml -o result2.txt
python check.py -p "cs3245-hw4/q1-qrels+ve.txt" -n "cs3245-hw4/q1-qrels-ve.txt" -r result1.txt
python check.py -p "cs3245-hw4/q2-qrels+ve.txt" -n "cs3245-hw4/q2-qrels-ve.txt" -r result2.txt
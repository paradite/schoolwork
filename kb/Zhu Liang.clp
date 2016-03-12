; ; Diagnosis Program adapted from Textbook p.97
; ; Uses CLIPS version 6.30 on OS X
; ; TEMPLATES

; ; Sign of a symptom
(deftemplate sign
(slot symptom (type SYMBOL))
(slot organ (type SYMBOL) (default NIL))
(slot site (type SYMBOL) (default NIL)))

; ; Final Diagnosis
(deftemplate diagnosis
(slot disorder (type SYMBOL))
(slot organ (type SYMBOL) (default NIL)))

; ; Question
(deftemplate question
(slot symptom (type SYMBOL))
(slot organ (type SYMBOL) (default NIL))
(slot answer (type SYMBOL) (default NIL)))

; ; Activate questions for different sites
(defrule questions-upper
(sign (symptom pain) (organ abdomen) (site upper))
=>
(assert (question (symptom poor-appetite) (organ abdomen)))
(assert (question (symptom weight-loss) (organ abdomen))))

(defrule questions-lower
(sign (symptom pain) (organ abdomen) (site lower))
=>
(assert (question (symptom severe-pain) (organ abdomen)))
(assert (question (symptom nausea) (organ abdomen)))
(assert (question (symptom fever) (organ abdomen)))
(assert (question (symptom diarrhea) (organ abdomen))))

(defrule questions-upper-right
(sign (symptom pain) (organ abdomen) (site upper-right))
=>
(assert (question (symptom severe-pain) (organ abdomen)))
(assert (question (symptom vomiting) (organ abdomen)))
(assert (question (symptom fever) (organ abdomen))))

; ; Ask questions when available
(defrule ask-question
?question <- (question (symptom ?symptom) (answer NIL))
=>
(printout t "Do you have " ?symptom "? (Y/y or N/n) ")
(bind ?n (read))
(switch ?n (case y then (modify ?question (answer y)))
		(case Y then (modify ?question (answer y)))
		(case n then (modify ?question (answer n)))
		(case N then (modify ?question (answer n)))))

; ; Process the answer to questions
(defrule process-answer
(question (symptom ?symptom) (answer ?answer&~NIL))
=>
(switch ?answer (case y then (assert(sign (symptom ?symptom))))))

; ; Restart function
(deffunction restart
()
(retract *)
(assert (sign (symptom pain) (organ abdomen)))
(printout t "****************************************" crlf crlf)
)

; ; Fail when no questions to ask and no conclusion reached
(defrule fail
(not (exists(question (answer NIL))))
(not (exists(diagnosis)))
=>
(printout t crlf "Sorry, I am not able to diagnose your disease!" crlf crlf)
(printout t "Do you want to run this program again? (Y/y or N/n) ")
(bind ?n (read))
(switch ?n (case y then (restart))
		(case Y then (restart))
		(case n then (halt))
		(case N then (halt))))

; ; The initial facts
; ; i.e. Patient reports abdominal pain
(deffacts the-facts
(sign (symptom pain) (organ abdomen)))

; ; First, gather information about site of pain
(defrule data
?sign <- (sign (symptom pain) (organ abdomen) (site NIL))
=>
(printout t "Where is the pain? (1.Lower; 2.Upper; 3.Upper-Right; Others: stop) ")
(bind ?n (read))
(switch ?n (case 1 then (modify ?sign (site lower)))
	   (case 2 then (modify ?sign (site upper)))
	   (case 3 then (modify ?sign (site upper-right)))
	   (default then (halt))))

; ; Diagnosis of tumor of stomach
(defrule stomach-tumor
(sign (symptom pain) (organ abdomen) (site upper))
(sign (symptom poor-appetite))
(sign (symptom weight-loss))
=>
(assert (diagnosis (disorder tumor) (organ stomach))))

; ; Diagnosis of ulceration of large intestine
(defrule ulceration
(sign (symptom pain) (organ abdomen)(site lower))
(sign (symptom diarrhea))
(sign (symptom nausea))
(not (sign (symptom fever)))
=>
(assert (diagnosis (disorder ulceration) (organ large-intestine))))

; ; Diagnosis of inflammation of small intestine
(defrule inflammation
(sign (symptom pain) (organ abdomen)(site lower))
(sign (symptom diarrhea))
(sign (symptom fever))
=>
(assert (diagnosis (disorder inflammation) (organ small-intestine))))

; ; Diagnosis of inflammation of appendix
(defrule appendicitis
(sign (symptom pain) (organ abdomen) (site lower))
(sign (symptom fever))
(sign (symptom nausea))
(sign (symptom severe-pain))
=>
(assert (diagnosis (disorder inflammation) (organ appendix))))

; ; Diagnosis of stones in gall bladder
(defrule gallstones
(sign (symptom pain) (organ abdomen) (site upper-right))
(sign (symptom severe-pain))
=>
(assert (diagnosis (disorder stones) (organ gallbladder))))

; ; Diagnosis of infection of gallbladder
(defrule gallbladder
(sign (symptom pain) (organ abdomen) (site upper-right))
(sign (symptom vomiting))
(sign (symptom fever))
=>
(assert (diagnosis (disorder infection) (organ gallbladder))))

; ; 
; ; Report the diagnosis and halt
(defrule report
(diagnosis (disorder ?x) (organ ?y))
=>
(printout t crlf "My diagnosis: " ?x " of " ?y "." crlf crlf)
(printout t "Do you want to run this program again? (Y/y or N/n) ")
(bind ?n (read))
(switch ?n (case y then (restart))
		(case Y then (restart))
		(case n then (halt))
		(case N then (halt)))
)

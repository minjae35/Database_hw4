# W4111 - Introduction to Databases, Spring 2026: Sample Questions

## Introduction

This document contains some examples/sample short written answer questions to help prepare for exam #3. These questions are not representative of the exam as a whole
or the exam length. The questions are simply examples of what the short written questions will look like.

## Sample Questions

### Q1 $-$ Functional Dependencies

Consider the relation:

**R(A, B, C, D, E)**

The following sample tuples are given:

| A  | B  | C  | D  | E  |
|----|----|----|----|----|
| a1 | b1 | c1 | d1 | e1 |
| a1 | b1 | c2 | d1 | e2 |
| a2 | b1 | c1 | d2 | e3 |
| a2 | b1 | c2 | d2 | e4 |
| a3 | b2 | c1 | d3 | e5 |
| a3 | b2 | c2 | d3 | e6 |

---

#### **Questions**

1. Identify all **non-trivial functional dependencies** that hold on this relation based on the data shown.

2. For each of the following, state whether the functional dependency holds. Briefly justify your answer.
   - (a) A → D  
   - (b) B → A  
   - (c) A → B  
   - (d) (A, C) → E  

3. Find a **candidate key** for this relation. Show your reasoning.

4. Does the functional dependency **C → E** hold? Why or why not?

---

#### **Instructions**
- Base your answers **only on the data provided**.
- Clearly justify each answer using the tuples.
- Partial credit will be given for correct reasoning.

### **Q2 $-$ 3NF vs. BCNF**

Consider the relation:

**R(A, B, C)**

with the following functional dependencies:

- A → B  
- B → C  

---

#### **Questions**

1. What are the **candidate key(s)** for R? Show your reasoning.

2. Is the relation **R in Third Normal Form (3NF)**? Explain why or why not.

3. Is the relation **R in Boyce-Codd Normal Form (BCNF)**? Explain why or why not.

4. If R is not in BCNF, decompose R into a set of relations that are in BCNF. Show the resulting schemas.

---

#### **Instructions**
- Clearly justify each answer.
- You may use formal definitions of 3NF and BCNF in your explanation.

### **Q3 $-$ Join Algorithms**

Consider joining two relations **R** and **S**.

1. Briefly describe:
   - Nested-loop join  
   - Indexed nested-loop join  
   - Merge join  
   - Hash join  

2. Under what conditions is each algorithm preferred?

3. Why does the choice of **outer vs. inner relation** matter in nested-loop joins?
---

### **Q4 $-$ Join Algorithms**

Assume a relation $R$ has $N$ records. 

1. Expressed as order notation "function" of $N$, what is the approximate complexity/cost of:
   - (a) Full table scan  
   - (b) B+-tree index lookup  
   - (c) Hash lookup  

2. Why might building an index be beneficial even if it has a cost?

3. Explain why a query plan that is optimal for one operation may not be optimal for the entire query.

---

### **Q5 $-$ Materialization vs. Pipelining**

1. Define:
   - (a) Materialization  
   - (b) Pipelining  

2. What are the advantages and disadvantages of each?

3. Why can pipelining not always be used?

---

### **Q6 $-$ Logical vs Physical Plans**

Consider the query:

SELECT name FROM instructor WHERE salary < 75000;

1. Write two equivalent relational algebra expressions.
2. Which one is likely more efficient? Why?

---

### **Q7 $-$ Conjunctive vs Disjunctive Selection**

Assume:
- Index exists on name
- No index on dept_name

Compare the performance of:

1. WHERE name = 'Smith' AND dept_name = 'CS'  
2. WHERE name = 'Smith' OR dept_name = 'CS'  

Why does the index help in one case but not the other?

---

### **Q8 $-$ Join Algorithm Selection**

Given:
- R has 1,000 tuples
- S has 1,000,000 tuples
- Index exists on S.join_attr

1. Which join algorithm is most appropriate?
2. Which relation should be the outer relation? Why?

---

### **Q9 $-$ Transaction Execution**

Consider a transaction that transfers $50 from account A to account B.

1. What can go wrong if the transaction fails after updating A but before updating B?
2. Which ACID property is violated?
3. How does the DBMS prevent this problem?

---

### **Q10 $-$ Isolation Levels**

Compare the following isolation levels:

- Read Uncommitted  
- Read Committed  
- Repeatable Read  
- Serializable  

For each, state one anomaly that can occur.

---

### **Q11 $-$ ACID vs BASE**

1. What does BASE stand for?
2. How does BASE differ from ACID?
3. When might a system prefer BASE over ACID?

---

### **Q12 $-$ Concurrency Control**

1. What is **Strict Two-Phase Locking (Strict 2PL)**?
2. Why does it guarantee serializability?
3. What problem does it help prevent during transaction abort?

---

### **Q13 $-$ Scaling and Architecture**

1. What is the difference between:
   - scale-up
   - scale-out  

2. What is a **shared-nothing architecture**?
3. Why is scale-out challenging for relational operations like joins?

---

### **Q14 $-$ Serializability**

1. Define **serializability**.
2. Why is it considered the main correctness criterion?
3. Explain the difference between:
   - conflict serializability  
   - view serializability  

---

### **Q15 $-$ Cascading Rollbacks**

1. What is a cascading rollback?
2. Why is it undesirable?
3. How do **cascadeless schedules** prevent this?

---

### **Q16 $-$ Strict Two-Phase Locking (2PL)**

1. Describe the rules of **Strict 2PL**.
2. Why does it guarantee serializability?
3. How does it simplify recovery?

---

### **Q17 $-$ Resource-Oriented Design**

Given entities:
- Course
- Section
- Participant

1. Design REST endpoints for:
   - retrieving all sections of a course  
   - retrieving all participants in a section  

2. Explain the difference between:
   - a resource  
   - a collection resource  

---


### **Q18 $-$ Data Engineering Pipeline**

1. What are the steps in ETL?
2. What is the difference between ETL and ELT?
3. Why is data engineering often the most time-consuming part of analytics?

---

### **Q19 $-$ Deadlock Prevention vs Detection**

1. What is the difference between:
   - deadlock prevention  
   - deadlock detection  

2. Explain one prevention technique:
   - wait-die  
   - wound-wait  
   - timeout  

3. What is a **wait-for graph**, and what does a cycle indicate?

---

### **Q20 $-$ Star Schema Design**

You are designing a data warehouse for sales.

1. What is a **fact table**?
2. What are **dimension tables**?
3. Give an example of:
   - one fact  
   - two dimensions  

4. Why is this model useful for analytics?

---
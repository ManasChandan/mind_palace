## 📑 Table of Contents

<ul>
  <li><a href="#what-is-surrogate-key">What is a surrogate key?</a></li>
  <li><a href="#surrogate-vs-natural-key">Surrogate key vs Natural (Business) key</a></li>
  <li><a href="#why-surrogate-keys">Why do we need surrogate keys?</a></li>
  <li><a href="#how-surrogate-keys-made">How are surrogate keys made?</a></li>
  <li><a href="#how-surrogate-keys-assigned">How are surrogate keys assigned in practice?</a></li>
  <li><a href="#how-surrogate-keys-maintained">How are surrogate keys maintained?</a></li>
  <li><a href="#surrogate-early-late">Surrogate keys and early / late arriving data</a></li>
  <li><a href="#surrogate-vs-natural-facts">Surrogate keys vs natural keys in fact tables</a></li>
  <li><a href="#common-mistakes">Common mistakes</a></li>
</ul>

---

<div id="what-is-surrogate-key"></div>

## What is a surrogate key?

A **surrogate key** is a **warehouse-generated, meaningless, unique identifier** used as the **primary key of a dimension table**.

It has **no business meaning**.

### Simple definition

> A surrogate key is an ID created by the data warehouse, not by the source system.

---

<div id="surrogate-vs-natural-key"></div>

## Surrogate key vs Natural (Business) key

### Natural / Business key

* Comes from the source system
* Has business meaning
* Can change or be reused

**Examples**

* Customer ID from CRM
* Product Code
* Account Number
* Email address

---

### Surrogate key

* Created in the warehouse
* Usually an integer
* Never changes
* Never reused

**Example**

```text
Customer_SK = 102347

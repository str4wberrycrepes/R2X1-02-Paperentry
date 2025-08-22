# R2X1-02 | R3X2-02 Data Readers/Importers

## Overview
This toolkit contains scripts for importing structured data into **Neo4j**.  
Currently supported:
- **Ontology Importer** → Parse RDF/OWL ontology files and push them into Neo4j.  
- **Research Paper Importer** → Import research papers and keywords from Excel spreadsheets into Neo4j.  

Scripts may assume the Neo4j database you’re pushing into is **empty**.

---

## Requirements
Install dependencies:
```bash
pip install rdflib neo4j pandas
```

A running Neo4j instance (either local or remote)

---

## Configuration
Scripts use a `conf.json` file with your Neo4j connection details:

```json
{
    "url": "neo4j://localhost:7687",
    "user": "neo4j",
    "pass": "password"
}
```

---

# 1. RDF Importer (RDF → Neo4j)

### Purpose
Parses RDF/OWL files to extract:
- Classes  
- Subclass relationships (`rdfs:subClassOf`)  
- Disjoint relationships (`owl:disjointWith`)  

Then imports them as nodes and relationships into Neo4j.

### Usage
```bash
python rdf_importer.py
```

Script:
1. Parses the RDF file (`.rdf` or `.owl`)  
2. Prints extracted classes and relationships  
3. Pushes them into Neo4j as `(:Class)` nodes  

### Neo4j Output
- **Nodes**:  
  `(:Class {name: "Animal"})`  

- **Relationships**:  
  - `(Mammal)-[:SUBCLASS_OF]->(Animal)`  
  - `(Bird)-[:DISJOINT_WITH]->(Mammal)`  

### Example RDF Fragment
```xml
<owl:Class rdf:about="#Animal"/>
<owl:Class rdf:about="#Mammal">
    <rdfs:subClassOf rdf:resource="#Animal"/>
</owl:Class>
<owl:Class rdf:about="#Bird">
    <owl:disjointWith rdf:resource="#Mammal"/>
</owl:Class>
```

Imports into Neo4j as:
```
(Mammal)-[:SUBCLASS_OF]->(Animal)
(Bird)-[:DISJOINT_WITH]->(Mammal)
```

---

# 2. XLSX Importer (Excel → Neo4j)

### Purpose
Reads data from an Excel file and imports:
- `(:paper)` nodes for each paper  
- `(:keyword)` nodes for unique keywords  
- `(:keyword)-[:IN]->(:paper)` relationships  

### Excel File Format
The Excel sheet must have columns:
- **title** → Paper title  
- **rescode** → Research code  
- **authors** → Authors  
- **batch** → Batch identifier  
- **keywords** → Comma-separated keywords  

**Example:**
| title          | rescode | authors      | batch | keywords               |
|----------------|---------|--------------|-------|------------------------|
| AI in Health   | 001     | Smith, John  | 2025  | AI, Healthcare, Ethics |
| Marine Studies | 002     | Doe, Jane    | 2025  | Marine, Climate        |

### Usage
```bash
python xlsx_importer.py
```
You will be prompted for the Excel file path.

### Neo4j Output
- **Paper node**:
  ```
  (:paper {
      name: "AI in Health",
      rescode: "2025_001",
      authors: "Smith, John",
      batch: "2025"
  })
  ```

- **Keyword node**:
  ```
  (:keyword {name: "AI"})
  ```

- **Relationship**:
  ```
  (:keyword {name: "AI"})-[:IN]->(:paper {name: "AI in Health"})
  ```

---

## Notes
- Scripts **clear the database** before inserting data.  
- Run them only on an **empty Neo4j database** or you **will** lose existing data.  
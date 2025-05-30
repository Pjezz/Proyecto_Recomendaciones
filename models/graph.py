from neo4j import GraphDatabase

# Conecta a tu base
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "estructura"))

def get_recommendations(brand, budget, transmission, types):
    query = """
    MATCH (c:Car)-[:HAS_BRAND]->(m:Marca {nombre: $brand})
    WHERE c.presupuesto = $budget AND c.transmision = $transmision
    AND ANY(t IN $tipos WHERE t IN c.tipos)
    RETURN c.modelo AS modelo, c.precio AS precio, c.transmision AS transmision
    LIMIT 10
    """
    with driver.session() as session:
        result = session.run(query, brand=brand, budget=budget, transmision=transmission, tipos=types)
        return [record.data() for record in result]

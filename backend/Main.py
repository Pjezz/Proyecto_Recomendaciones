from gestionador import Gestionador

def main():
    USER = "neo4j"
    PASSWORD = "proyectoNEO4J"
    URL = "bolt://localhost:7474"

    try:
        conexion = Gestionador(URL, USER, PASSWORD)
        print("Conexión exitosa a Neo4j")
    except Exception as e:
        print("Error al conectar a Neo4j:", e)
    finally:
        conexion.close()

if __name__ == "__main__":
    main()

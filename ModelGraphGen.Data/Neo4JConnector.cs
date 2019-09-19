using System;
using System.Linq;
using ModelGraphGen.Domain;
using Neo4j.Driver.V1;

namespace ModelGraphGen.Data
{
    /// <summary>
    /// Class to manage connection with a Neo4j database
    /// </summary>
    public class Neo4JConnector : IDisposable   
    {
        private readonly IDriver _driver;

        /// <summary>
        /// Constructor
        /// </summary>
        /// <param name="uri"></param>
        /// <param name="user"></param>
        /// <param name="password"></param>
        public Neo4JConnector(string uri, string user, string password)
        {
            _driver = GraphDatabase.Driver(uri, AuthTokens.Basic(user, password));
        }
        
        /// <summary>
        /// 
        /// </summary>
        public void Dispose()
        {
            // if driver exists, dispose him
            _driver?.Dispose();
        }

        #region Transactions
        
        public void InsertIfcEntity(string entityLabel, int entityId)
        {
            using (var session = _driver.Session())
            {
                var entityResult = session.WriteTransaction(tx =>
                {
                    var result = tx.Run("CREATE (n: " +
                                        entityLabel +
                                        "{name: $entityLabel}) " +
                                        "SET n.EntityId = $entityId " +
                                       "RETURN n",
                        new { entityLabel, entityId });
                    return result;
                });
              
            }
        }

        public void InsertIfcRelationships(int sourceId, int targetId)
        {
            using (var session = _driver.Session())
            {
                var entityResult = session.WriteTransaction(tx =>
                {
                    var result = tx.Run("MATCH (a),(b) " +
                                        "WHERE a.EntityId = $sourceId OR b.EntityId = $targetId " +
                                        "CREATE (a)-[r:hasRelation]->(b) " +
                                        "RETURN r ",
                        new {sourceId , targetId });
                    return result;
                });
            }
        }

        public void SetParameter<T>(int entityId, string pName, T pVal) 
        {
            using (var session = _driver.Session())
            {
                var entityResult = session.WriteTransaction(tx =>
                {
                    var result = tx.Run("MATCH (a) " +
                                        "WHERE a.EntityId= $entityId " +
                                        "SET a." +
                                        pName + " = $pVal "+
                                        "RETURN a ",
                        new { entityId, pName, pVal});
                    return result;
                });

            }
        }
        #endregion

        #region utilities
        public void DeleteAllNodes()
        {
            using (var session = _driver.Session())
            {
                var greeting = session.WriteTransaction(tx =>
                {
                    var result = tx.Run("Match(n) delete n");
                    return result;
                });
            }
        }



        #endregion
    }
}

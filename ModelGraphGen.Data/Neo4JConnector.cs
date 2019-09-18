using System;
using System.Linq;
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

        public void PrintGreeting(string message)
        {
            using (var session = _driver.Session())
            {
                var greeting = session.WriteTransaction(tx =>
                {
                    var result = tx.Run("CREATE (a:test{id: 1}) " +
                                        "SET a.message = $message " +
                                        "RETURN a.message + ', from node ' + id(a)",
                        new { message });
                    return result;
                });
                Console.WriteLine(greeting);

            }
        }


        #endregion
    }
}

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Neo4j.Driver.V1;

namespace App_BoltConnectionTester
{
    class Program
    {
        static void Main(string[] args)
        {
            var uri = "bolt://localhost:7687";
            var user = "neo4j";
            var password = "password";

            var  _driver = GraphDatabase.Driver(uri, AuthTokens.Basic(user, password));

            Console.Write(_driver);

            using (var session = _driver.Session(AccessMode.Read))
            {
                var greeting = session.WriteTransaction(tx =>
                {
                    var result = tx.Run("MATCH(e) RETURN e");
                    return result.Keys;
                });
                Console.WriteLine(greeting);
            }

        }
    }
}

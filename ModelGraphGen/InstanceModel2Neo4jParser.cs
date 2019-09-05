using System;
using ModelGraphGen.Ifc_InstanceOnly;

namespace ModelGraphGen
{
    /// <summary>
    /// </summary>
    public class InstanceModel2Neo4jParser
    {
        public string SourceLocation { get; set; }
        public string TargetLocation { get; set; }

        /// <summary>
        /// </summary>
        public string CreateNeo4jScript()
        {
            var sourceFile = SourceLocation;
            var modelType = "IFC";

            string neo4JScript = null;

            // switch format
            switch (modelType)
            {
                case "IFC":
                    var modelParser = new Ifc2Neo4JInstanceOnly();
                    neo4JScript = modelParser.Parse(sourceFile);
                    break;

                // add additional data structures here
            }

            return neo4JScript;
        }

        /// <summary>
        ///     Store resulting Neo4j Script in text file
        /// </summary>
        public void StoreResult()
        {
            Console.WriteLine("Started Storing...");


            Console.WriteLine("Finished. ");
        }
    }
}
using System;
using System.IO;
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
        public string CreateNeo4JScript()
        {
            var sourceFile = SourceLocation;
            var modelType = "IFC";

            string neo4JScript = null;

            // switch format
            switch (modelType)
            {
                case "IFC":
                    var modelParser = new Ifc2Neo4JInstanceOnly();
                    neo4JScript = modelParser.DeserializeInstanceData(sourceFile);
                    break;

                //ToDo: add additional data structures here
            }
            
            return neo4JScript;
        }

        /// <summary>
        ///     Store resulting Neo4j Script in text file
        /// </summary>
        public void StoreResult(string script)
        {
            Console.WriteLine("Started Storing...");
            // save script to targetLocation
            // This text is added only once to the file.
           
                // Create a file to write to.
                File.WriteAllText(@TargetLocation, script);
           
            

            Console.WriteLine("Finished. ");
        }
    }
}